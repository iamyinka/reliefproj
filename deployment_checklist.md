# Relief Application - Production Deployment Checklist

## Pre-Deployment Setup

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env` and configure all variables
- [ ] Set `DEBUG=False` in production environment
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set secure `SECRET_KEY` (generate new one for production)
- [ ] Configure database credentials (PostgreSQL recommended)

### 2. Database Setup
- [ ] Create production database
- [ ] Run migrations: `python manage.py migrate`
- [ ] Load package fixtures: `python manage.py loaddata packages/fixtures/initial_packages.json`
- [ ] Create superuser: `python manage.py createsuperuser`

### 3. Contact Information
- [ ] Set `CONTACT_PHONE` to your organization's phone number
- [ ] Set `CONTACT_EMAIL` to your support email address
- [ ] Set `ORGANIZATION_NAME` to your organization's name

### 4. Email Configuration
- [ ] Configure SMTP settings for email notifications
- [ ] Test email sending functionality
- [ ] Set up email templates if needed

## Security Configuration

### 5. SSL/HTTPS Setup
- [ ] Configure SSL certificate
- [ ] Set `SECURE_SSL_REDIRECT=True` in production settings
- [ ] Configure reverse proxy (Nginx) for HTTPS

### 6. Static Files
- [ ] Run `python manage.py collectstatic`
- [ ] Configure web server to serve static files
- [ ] Set up CDN for static files (optional)

### 7. Cache Setup (Optional but Recommended)
- [ ] Install Redis
- [ ] Configure Redis cache settings
- [ ] Test cache functionality

## Application Configuration

### 8. Relief App Settings
- [ ] Review `APPLICATION_RESTRICTION_DAYS` (default: 21 days)
- [ ] Review `QR_CODE_EXPIRY_DAYS` (default: 7 days)  
- [ ] Review `LOW_STOCK_THRESHOLD` (default: 10 packages)

### 9. Package Management
- [ ] Review and customize package data in fixtures
- [ ] Test package creation/editing in admin interface
- [ ] Verify stock management functionality

## Monitoring and Logging

### 10. Logging Setup
- [ ] Create logs directory: `mkdir logs`
- [ ] Configure log rotation
- [ ] Set up log monitoring (optional)

### 11. Error Monitoring
- [ ] Set up error tracking (Sentry recommended)
- [ ] Configure email notifications for critical errors
- [ ] Test error handling and reporting

## Testing

### 12. Functional Testing
- [ ] Test package browsing on homepage
- [ ] Test complete application flow
- [ ] Test QR code generation and scanning
- [ ] Test admin package management
- [ ] Verify contact information displays correctly

### 13. Performance Testing
- [ ] Load test with expected traffic
- [ ] Optimize database queries if needed
- [ ] Test under high concurrent users

## Deployment

### 14. Web Server Configuration
- [ ] Configure Nginx/Apache virtual host
- [ ] Set up WSGI server (Gunicorn recommended)
- [ ] Configure process manager (systemd/supervisor)

### 15. Background Tasks (Optional)
- [ ] Set up Celery for background tasks
- [ ] Configure Redis as message broker
- [ ] Set up periodic tasks for notifications

### 16. Backup Strategy
- [ ] Set up automated database backups
- [ ] Configure media files backup
- [ ] Test restore procedures

## Post-Deployment

### 17. Final Verification
- [ ] Test all functionality on production
- [ ] Verify SSL certificate installation
- [ ] Check all forms and API endpoints
- [ ] Monitor application logs

### 18. Documentation
- [ ] Document deployment process
- [ ] Create admin user guide
- [ ] Document maintenance procedures

## Environment Variables Summary

Required for production:
```
DEBUG=False
SECRET_KEY=your-new-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=relief_production_db
DB_USER=relief_user
DB_PASSWORD=secure-password
DB_HOST=localhost
DB_PORT=5432

CONTACT_PHONE=+234XXXXXXXXXX
CONTACT_EMAIL=support@yourdomain.com
ORGANIZATION_NAME=Your Organization Name

EMAIL_HOST=smtp.youremail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
```

## Quick Deployment Commands

```bash
# 1. Set up virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Set up database
python manage.py migrate
python manage.py loaddata packages/fixtures/initial_packages.json
python manage.py createsuperuser

# 5. Collect static files
python manage.py collectstatic

# 6. Test the application
python manage.py runserver

# 7. Deploy with Gunicorn (production)
gunicorn reliefproj.wsgi:application --bind 0.0.0.0:8000
```

## Support

For deployment issues or questions, contact your development team or refer to the Django deployment documentation.