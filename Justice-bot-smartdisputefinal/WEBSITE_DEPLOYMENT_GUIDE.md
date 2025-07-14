# Justice-Bot Website Deployment Guide

## Overview
This guide will help you deploy Justice-Bot to your own website for a smooth transition from Replit.

## Quick Start - What You Need

1. **Domain Name**: Your website domain (e.g., justice-bot.ca)
2. **Web Hosting**: A server that supports Python/Flask applications
3. **PostgreSQL Database**: For storing user data and cases
4. **SSL Certificate**: For secure HTTPS connections

## Deployment Options

### Option 1: Cloud Hosting (Recommended)
- **Google Cloud Run**: Best for scalability and ease of deployment
- **Heroku**: Simple deployment with free tier available
- **AWS Elastic Beanstalk**: Enterprise-grade hosting
- **DigitalOcean App Platform**: Developer-friendly platform

### Option 2: Traditional Web Hosting
- VPS with Python support
- Dedicated server with root access

## Required Environment Variables

Create a `.env` file with these values:
```
DATABASE_URL=postgresql://username:password@host:port/database
SESSION_SECRET=your-secret-key-here
OPENAI_API_KEY=your-openai-key-here
```

## Files You Need to Deploy

### Core Application Files:
- `main.py` - Main entry point
- `simple_app.py` - Application logic
- `models.py` - Database models
- `templates/` - All HTML templates
- `static/` - CSS, JS, and images
- `requirements.txt` - Python dependencies

### Configuration Files:
- `gunicorn_config.py` (create this for production)
- `.env` (environment variables)

## Step-by-Step Deployment

### 1. Prepare Your Files
```bash
# Create requirements.txt
pip freeze > requirements.txt
```

### 2. Set Up Your Database
```sql
-- Run this on your PostgreSQL server
CREATE DATABASE justicebot;
```

### 3. Configure Your Domain
Point your domain's DNS to your hosting provider:
- A Record: @ → Your server IP
- CNAME: www → Your domain

### 4. Deploy to Cloud (Google Cloud Run Example)
```bash
# Install Google Cloud CLI
# Then run:
gcloud run deploy justice-bot \
  --source . \
  --port 8080 \
  --allow-unauthenticated \
  --region us-central1
```

### 5. Deploy to Heroku (Alternative)
```bash
# Install Heroku CLI
heroku create your-justice-bot
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

## Production Configuration

### Create `gunicorn_config.py`:
```python
bind = "0.0.0.0:8080"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
```

### Update `Procfile` for Heroku:
```
web: gunicorn main:app --config gunicorn_config.py
```

## Security Checklist

- [ ] Use HTTPS/SSL certificate
- [ ] Set strong SESSION_SECRET
- [ ] Configure firewall rules
- [ ] Enable database backups
- [ ] Set up monitoring alerts

## Post-Deployment Testing

1. Visit your domain: https://your-domain.com
2. Test user registration
3. Upload a test document
4. Verify AI analysis works
5. Check database connectivity

## Troubleshooting

### Internal Server Error?
- Check environment variables are set
- Verify database connection
- Look at application logs

### Can't Access Site?
- Verify DNS propagation (can take 24-48 hours)
- Check firewall rules
- Ensure port 8080/80/443 is open

## Support

For deployment help:
- Email: support@justice-bot.ca
- Documentation: Check the README.md file

---

Ready to deploy? Your Justice-Bot platform is configured and ready for your own website!