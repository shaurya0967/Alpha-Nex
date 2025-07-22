#!/usr/bin/env python3
"""
Alpha Nex Utility Functions
Essential helper functions for email verification, file validation, and platform utilities
"""
import secrets
from flask import current_app
from flask_mail import Message
from app import mail

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def send_verification_email(user):
    """Send email verification link to user"""
    token = user.verification_token
    verification_url = f"http://localhost:5000/auth/verify/{token}"
    
    msg = Message(
        subject='Verify Your Alpha Nex Account',
        recipients=[user.email],
        body=f'''
Welcome to Alpha Nex!

Please click the following link to verify your email address:
{verification_url}

If you did not create an account with Alpha Nex, please ignore this email.

Best regards,
The Alpha Nex Team
        ''',
        html=f'''
<html>
<body>
    <h2>Welcome to Alpha Nex!</h2>
    <p>Please click the button below to verify your email address:</p>
    <a href="{verification_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
    <p>If the button doesn't work, copy and paste this link into your browser:</p>
    <p>{verification_url}</p>
    <p>If you did not create an account with Alpha Nex, please ignore this email.</p>
    <p>Best regards,<br>The Alpha Nex Team</p>
</body>
</html>
        '''
    )
    
    mail.send(msg)
