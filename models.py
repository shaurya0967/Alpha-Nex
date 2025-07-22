from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='uploader')  # uploader, reviewer, admin
    xp = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    daily_upload_size = db.Column(db.Integer, default=0)  # in bytes
    last_upload_reset = db.Column(db.Date, default=datetime.now(timezone.utc).date)
    consent_given = db.Column(db.Boolean, default=False)
    consent_timestamp = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Relationships
    uploads = db.relationship('Upload', backref='uploader', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='reviewer', lazy=True, cascade='all, delete-orphan')
    withdrawal_requests = db.relationship('WithdrawalRequest', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def reset_daily_upload_if_needed(self):
        """Reset daily upload size if it's a new day"""
        today = datetime.now(timezone.utc).date()
        if self.last_upload_reset != today:
            self.daily_upload_size = 0
            self.last_upload_reset = today
            db.session.commit()
    
    def can_upload(self, file_size):
        """Check if user can upload a file of given size"""
        self.reset_daily_upload_if_needed()
        max_daily_size = 500 * 1024 * 1024  # 500MB
        return (self.daily_upload_size + file_size) <= max_daily_size

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), unique=True, nullable=False)  # For duplicate detection
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    xp_awarded = db.Column(db.Integer, default=0)
    upload_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    reviews = db.relationship('Review', backref='upload', lazy=True, cascade='all, delete-orphan')
    
    def get_average_rating(self):
        reviews_list = db.session.query(Review).filter_by(upload_id=self.id).all()
        if not reviews_list:
            return None
        ratings = [r.rating_value for r in reviews_list]
        return sum(ratings) / len(ratings)
    
    def get_review_counts(self):
        reviews_list = db.session.query(Review).filter_by(upload_id=self.id).all()
        good = sum(1 for r in reviews_list if r.rating == 'good')
        fake = sum(1 for r in reviews_list if r.rating == 'fake')
        poor = sum(1 for r in reviews_list if r.rating == 'poor')
        return {'good': good, 'fake': fake, 'poor': poor}

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.String(10), nullable=False)  # good, fake, poor
    rating_value = db.Column(db.Integer, nullable=False)  # 1=poor, 2=fake, 3=good
    description = db.Column(db.Text, nullable=False)  # Required detailed description
    xp_awarded = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upload_id = db.Column(db.Integer, db.ForeignKey('upload.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'upload_id', name='unique_user_upload_review'),)

class WithdrawalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    payment_method = db.Column(db.String(100), nullable=False)
    payment_details = db.Column(db.Text, nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    processed_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class WebsiteRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class LegalConsent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consent_type = db.Column(db.String(50), nullable=False)  # upload_agreement, terms_of_service, etc.
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
