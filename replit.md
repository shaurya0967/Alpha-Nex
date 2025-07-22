# Alpha Nex - AI Training Data Platform

## Overview

Alpha Nex is a Flask-based web platform designed for collecting and reviewing user-uploaded content for AI training purposes. The platform operates on a community-driven model where users can either upload content (videos, audio, documents, code) or review others' submissions to maintain quality standards. The system includes a comprehensive reward mechanism using XP points and features robust legal compliance for AI training data collection.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **UI Framework**: Bootstrap 5.3.0 with custom dark theme
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JavaScript with Bootstrap components
- **Theme**: Dark theme implementation with CSS custom properties
- **Responsive Design**: Mobile-first approach using Bootstrap grid system

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-Login for session management
- **Email Service**: Flask-Mail for verification and notifications
- **File Handling**: Werkzeug for secure file uploads
- **Password Security**: Werkzeug password hashing

### Application Structure
- **Modular Design**: Blueprint-based routing (main, auth, upload, review, admin)
- **Model-View-Controller**: Clear separation with models.py, routes.py, and templates
- **Configuration**: Environment-based configuration with fallback defaults
- **Middleware**: ProxyFix for deployment behind reverse proxies

## Key Components

### User Management System
- **Multi-role Authentication**: Users can be uploaders, reviewers, or admins
- **Email Verification**: Required before platform access
- **User Profiles**: XP tracking, upload statistics, role-based permissions
- **Security Features**: Password hashing, verification tokens, daily upload limits

### Content Management
- **File Upload System**: Supports multiple formats (video, audio, documents, code)
- **File Validation**: Type checking, size limits (500MB daily per user)
- **Content Review Process**: Peer review system for quality control
- **Status Tracking**: Pending, approved, rejected content states

### Legal Compliance Framework
- **Comprehensive Agreements**: Terms of service, privacy policy, content policy
- **Upload Agreements**: Specific legal consent for AI training use
- **Consent Tracking**: Timestamped legal consent with IP address logging
- **Rights Management**: Perpetual, irrevocable licensing for AI training

### Reward System
- **XP Points**: Gamified contribution tracking
- **Role-based Rewards**: Different earning mechanisms for uploaders vs reviewers
- **Withdrawal Requests**: System for users to request payout of earned rewards
- **Quality Metrics**: Performance tracking and leaderboards

## Data Flow

### Upload Process
1. User authentication and role verification
2. Legal agreement acknowledgment
3. File upload with validation (type, size, ownership)
4. Content description and metadata capture
5. Queue for peer review
6. Review process with XP rewards
7. Final approval/rejection with feedback

### Review Process
1. Reviewer accesses pending content queue
2. Content evaluation against platform policies
3. Rating submission with detailed feedback
4. XP reward distribution
5. Content status update (approved/rejected)
6. Notification to original uploader

### User Registration Flow
1. Account creation with email verification
2. Role selection (uploader/reviewer)
3. Legal consent acknowledgment
4. Platform access grant
5. Dashboard customization based on role

## External Dependencies

### Email Services
- **SMTP Integration**: Gmail SMTP for email verification and notifications
- **Configuration**: Environment-based email server configuration
- **Templates**: HTML and text email templates for various communications

### File Storage
- **Local Storage**: Upload folder for content storage
- **File Security**: Secure filename generation and validation
- **Content Types**: Support for multimedia, documents, and code files

### Frontend Libraries
- **Bootstrap 5.3.0**: UI framework via CDN
- **Font Awesome 6.4.0**: Icon library via CDN
- **Custom CSS**: Dark theme implementation with CSS variables

## Deployment Strategy

### Environment Configuration
- **Database**: Configurable between SQLite (development) and PostgreSQL (production)
- **Secret Management**: Environment variables for sensitive configuration
- **Debug Mode**: Development/production mode switching
- **Mail Settings**: Environment-based SMTP configuration

### Production Considerations
- **Proxy Support**: ProxyFix middleware for reverse proxy deployment
- **Database Optimization**: Connection pooling and health checks
- **File Limits**: Configurable upload size limits and daily quotas
- **Security**: Session management and CSRF protection

### Scalability Features
- **Database Abstraction**: SQLAlchemy ORM for database independence
- **Modular Architecture**: Blueprint-based routing for feature separation
- **Configuration Management**: Environment-based settings for different deployment stages
- **Logging**: Comprehensive logging setup for monitoring and debugging

The platform is designed to handle the complex legal and technical requirements of AI training data collection while providing an intuitive user experience through its dark-themed interface and role-based functionality.