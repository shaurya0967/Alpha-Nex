import os
import hashlib
import secrets
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, send_from_directory, abort
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from app import db, mail, app
from models import User, Upload, Review, WithdrawalRequest, WebsiteRating, LegalConsent
from utils import allowed_file, generate_verification_token, send_verification_email

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
upload_bp = Blueprint('upload', __name__)
review_bp = Blueprint('review', __name__)
admin_bp = Blueprint('admin', __name__)

# Main routes
@main_bp.route('/')
def landing():
    return render_template('landing.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_verified:
        flash('Please verify your email first.', 'warning')
        return redirect(url_for('auth.verify_email'))
    
    if current_user.role == 'uploader':
        uploads = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.upload_date.desc()).all()
        return render_template('dashboard/uploader.html', uploads=uploads)
    elif current_user.role == 'reviewer':
        # Get uploads that are not from this user for reviewing
        uploads = Upload.query.filter(Upload.user_id != current_user.id, Upload.status == 'pending').all()
        return render_template('dashboard/reviewer.html', uploads=uploads)
    else:
        return redirect(url_for('admin.dashboard'))

@main_bp.route('/legal/terms')
def terms():
    return render_template('legal/terms.html')

@main_bp.route('/legal/privacy')
def privacy():
    return render_template('legal/privacy.html')

@main_bp.route('/legal/content-policy')
def content_policy():
    return render_template('legal/content_policy.html')

@main_bp.route('/rate-website', methods=['GET', 'POST'])
@login_required
def rate_website():
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        feedback = request.form.get('feedback', '')
        
        if rating and 1 <= rating <= 5:
            website_rating = WebsiteRating(
                user_id=current_user.id,
                rating=rating,
                feedback=feedback
            )
            db.session.add(website_rating)
            db.session.commit()
            flash('Thank you for rating Alpha Nex!', 'success')
        else:
            flash('Please provide a valid rating.', 'error')
        
        return redirect(url_for('main.dashboard'))
    
    return render_template('rating/website_rating.html')

# Auth routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.is_banned:
                flash('Your account has been banned. Contact support.', 'error')
                return render_template('auth/login.html')
            
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('auth/register.html')
        
        # Create user
        user = User(
            username=username,
            email=email,
            verification_token=generate_verification_token()
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        try:
            send_verification_email(user)
            flash('Registration successful! Please check your email to verify your account.', 'success')
        except Exception as e:
            app.logger.error(f"Failed to send verification email: {e}")
            flash('Registration successful! However, we could not send the verification email. Please contact support.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/verify-email')
@login_required
def verify_email():
    if current_user.is_verified:
        return redirect(url_for('auth.role_selection'))
    return render_template('auth/verify_email.html')

@auth_bp.route('/verify/<token>')
def verify_token(token):
    user = User.query.filter_by(verification_token=token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        login_user(user)
        flash('Email verified successfully!', 'success')
        return redirect(url_for('auth.role_selection'))
    else:
        flash('Invalid or expired verification token.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/role-selection', methods=['GET', 'POST'])
@login_required
def role_selection():
    if not current_user.is_verified:
        flash('Please verify your email first.', 'warning')
        return redirect(url_for('auth.verify_email'))
    
    if request.method == 'POST':
        role = request.form.get('role')
        if role in ['uploader', 'reviewer']:
            current_user.role = role
            db.session.commit()
            flash(f'Role set to {role.title()}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid role selection.', 'error')
    
    return render_template('auth/role_selection.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))

# Upload routes
@upload_bp.route('/agreement')
@login_required
def agreement():
    if not current_user.is_verified:
        flash('Please verify your email first.', 'warning')
        return redirect(url_for('auth.verify_email'))
    
    if current_user.role != 'uploader':
        flash('Only uploaders can access this page.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('upload/agreement.html')

@upload_bp.route('/consent', methods=['POST'])
@login_required
def consent():
    if not current_user.is_verified:
        flash('Please verify your email first.', 'warning')
        return redirect(url_for('auth.verify_email'))
    
    if current_user.role != 'uploader':
        flash('Only uploaders can access this page.', 'error')
        return redirect(url_for('main.dashboard'))
    
    consent_given = request.form.get('consent') == 'on'
    
    if consent_given:
        current_user.consent_given = True
        current_user.consent_timestamp = datetime.now(timezone.utc)
        
        # Record legal consent
        legal_consent = LegalConsent(
            user_id=current_user.id,
            consent_type='upload_agreement',
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.environ.get('HTTP_USER_AGENT')
        )
        db.session.add(legal_consent)
        db.session.commit()
        
        flash('Consent recorded. You can now upload files.', 'success')
        return redirect(url_for('upload.upload_form'))
    else:
        flash('You must give consent to upload files.', 'error')
        return redirect(url_for('upload.agreement'))

@upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_form():
    if not current_user.is_verified:
        flash('Please verify your email first.', 'warning')
        return redirect(url_for('auth.verify_email'))
    
    if current_user.role != 'uploader':
        flash('Only uploaders can access this page.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if not current_user.consent_given:
        flash('You must agree to the upload terms first.', 'warning')
        return redirect(url_for('upload.agreement'))
    
    if request.method == 'POST':
        file = request.files.get('file')
        description = request.form.get('description', '')
        
        if not file or file.filename == '':
            flash('No file selected.', 'error')
            return render_template('upload/upload_form.html')
        
        if not allowed_file(file.filename):
            flash('File type not allowed.', 'error')
            return render_template('upload/upload_form.html')
        
        # Check file size limits
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if not current_user.can_upload(file_size):
            flash('Daily upload limit exceeded (500MB).', 'error')
            return render_template('upload/upload_form.html')
        
        # Generate file hash for duplicate detection
        file_content = file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        file.seek(0)
        
        # Check for duplicates
        existing_upload = Upload.query.filter_by(file_hash=file_hash).first()
        if existing_upload:
            flash('This file has already been uploaded.', 'error')
            return render_template('upload/upload_form.html')
        
        # Save file
        filename = secure_filename(file.filename or "unknown")
        unique_filename = f"{secrets.token_hex(8)}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Create upload record
        upload = Upload(
            filename=unique_filename,
            original_filename=filename,
            file_type=filename.rsplit('.', 1)[1].lower(),
            file_size=file_size,
            file_hash=file_hash,
            description=description,
            user_id=current_user.id
        )
        
        # Update user's daily upload size
        current_user.daily_upload_size += file_size
        
        db.session.add(upload)
        db.session.commit()
        
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Calculate remaining daily upload allowance
    current_user.reset_daily_upload_if_needed()
    max_daily_size = 500 * 1024 * 1024  # 500MB
    remaining_size = max_daily_size - current_user.daily_upload_size
    remaining_mb = remaining_size / (1024 * 1024)
    
    return render_template('upload/upload_form.html', remaining_mb=remaining_mb)

@upload_bp.route('/download/<int:upload_id>')
@login_required
def download_file(upload_id):
    upload = Upload.query.get_or_404(upload_id)
    
    # Only allow download if user is the uploader or a reviewer
    if current_user.id != upload.user_id and current_user.role != 'reviewer' and current_user.role != 'admin':
        abort(403)
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], upload.filename, as_attachment=True, download_name=upload.original_filename)

# Review routes
@review_bp.route('/content')
@login_required
def content_list():
    if not current_user.is_verified:
        flash('Please verify your email first.', 'warning')
        return redirect(url_for('auth.verify_email'))
    
    if current_user.role != 'reviewer':
        flash('Only reviewers can access this page.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get uploads that are not from this user and haven't been reviewed by this user
    reviewed_upload_ids = db.session.query(Review.upload_id).filter_by(user_id=current_user.id).subquery()
    uploads = Upload.query.filter(
        Upload.user_id != current_user.id,
        Upload.status == 'pending',
        ~Upload.id.in_(reviewed_upload_ids)
    ).order_by(Upload.upload_date.desc()).all()
    
    return render_template('review/content_list.html', uploads=uploads)

@review_bp.route('/review/<int:upload_id>', methods=['GET', 'POST'])
@login_required
def review_form(upload_id):
    if not current_user.is_verified:
        flash('Please verify your email first.', 'warning')
        return redirect(url_for('auth.verify_email'))
    
    if current_user.role != 'reviewer':
        flash('Only reviewers can access this page.', 'error')
        return redirect(url_for('main.dashboard'))
    
    upload = Upload.query.get_or_404(upload_id)
    
    # Prevent users from reviewing their own content
    if upload.user_id == current_user.id:
        flash('You cannot review your own content.', 'error')
        return redirect(url_for('review.content_list'))
    
    # Check if user has already reviewed this content
    existing_review = Review.query.filter_by(user_id=current_user.id, upload_id=upload_id).first()
    if existing_review:
        flash('You have already reviewed this content.', 'warning')
        return redirect(url_for('review.content_list'))
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        description = request.form.get('description', '').strip()
        
        # Validate description (minimum 50 characters)
        if len(description) < 50:
            flash('Review description must be at least 50 characters long.', 'error')
            return render_template('review/review_form.html', upload=upload)
        
        if rating not in ['good', 'fake', 'poor']:
            flash('Invalid rating selected.', 'error')
            return render_template('review/review_form.html', upload=upload)
        
        # Create review
        rating_values = {'poor': 1, 'fake': 2, 'good': 3}
        review = Review(
            user_id=current_user.id,
            upload_id=upload_id,
            rating=rating,
            rating_value=rating_values[rating],
            description=description
        )
        
        # Award XP for detailed review
        xp_award = 10 if len(description) >= 100 else 5
        review.xp_awarded = xp_award
        current_user.xp += xp_award
        
        db.session.add(review)
        db.session.commit()
        
        flash(f'Review submitted successfully! You earned {xp_award} XP.', 'success')
        return redirect(url_for('review.content_list'))
    
    return render_template('review/review_form.html', upload=upload)

# Admin routes
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get statistics
    total_users = User.query.count()
    total_uploads = Upload.query.count()
    total_reviews = Review.query.count()
    pending_withdrawals = WithdrawalRequest.query.filter_by(status='pending').count()
    
    # Get recent uploads and users
    recent_uploads = Upload.query.order_by(Upload.upload_date.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_uploads=total_uploads,
                         total_reviews=total_reviews,
                         pending_withdrawals=pending_withdrawals,
                         recent_uploads=recent_uploads,
                         recent_users=recent_users)

@admin_bp.route('/ban-user/<int:user_id>')
@login_required
def ban_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot ban admin users.', 'error')
    else:
        user.is_banned = True
        db.session.commit()
        flash(f'User {user.username} has been banned.', 'success')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/unban-user/<int:user_id>')
@login_required
def unban_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    flash(f'User {user.username} has been unbanned.', 'success')
    
    return redirect(url_for('admin.dashboard'))
