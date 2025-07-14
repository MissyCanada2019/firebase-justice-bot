# SmartDispute.ai - Canadian Legal Automation Platform

## Overview

SmartDispute.ai is a comprehensive AI-driven legal automation platform built specifically for Canadian law, covering all levels of government (federal, provincial, municipal) and providing intelligent document analysis, case management, and court-ready form generation.

## Key Features

### Authentication & User Management
- Google OAuth integration (no Replit login)
- Firebase authentication with analytics
- Social login UI prepared for Twitter, Facebook, and email
- 1000 user pilot program with tracking
- Admin system with role-based access

### Cloud Storage Integration
- Google Drive file upload and processing
- OneDrive integration with secure downloads
- Dropbox file access and validation
- Tabbed interface for multiple upload options
- Secure file validation and temporary file management

### Comprehensive Legal Coverage
- **Federal Law**: Criminal Code, Charter Rights, Parliament Bills, Supreme Court decisions
- **Provincial Law**: All 10 provinces + 3 territories with statutes and court decisions
- **Municipal Law**: Bylaws from 20+ major Canadian cities
- **Family Law**: Divorce Act, custody laws, support enforcement
- **Criminal Law**: Complete criminal code coverage, youth justice, appeals
- **CAS/Child Protection**: All provincial child protection acts

### AI-Powered Features
- Legal document analysis and merit scoring
- Court-ready form generation
- Case law matching and recommendations
- Charter compliance analysis
- Automated legal research

### Payment Processing
- PayPal integration with instant activation
- Canadian Interac e-Transfer support
- Email notifications to teresa@justice-bot.com
- PIPEDA-compliant data handling

## Technology Stack

- **Backend**: Flask with Python
- **Database**: PostgreSQL with UUID-based schema
- **Authentication**: Google OAuth + Firebase
- **AI Integration**: OpenAI API (optional)
- **Cloud Storage**: Google Drive, OneDrive, Dropbox APIs
- **Payment**: PayPal, e-Transfer
- **Deployment**: Replit with dual-port configuration

## Installation

1. Clone the repository
2. Set up environment variables:
   ```
   DATABASE_URL=your_postgresql_url
   GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
   OPENAI_API_KEY=your_openai_key (optional)
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python main.py`

## Environment Configuration

The application requires several environment variables for full functionality:

- `DATABASE_URL`: PostgreSQL connection string
- `GOOGLE_OAUTH_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_OAUTH_CLIENT_SECRET`: Google OAuth client secret
- `OPENAI_API_KEY`: OpenAI API key for AI features (optional)
- `SESSION_SECRET`: Flask session secret

## Legal Data Sources

The platform monitors 80+ legal sources including:
- Federal Parliament bills and Royal Assent tracking
- Provincial legislation across all Canadian provinces and territories
- Municipal bylaws from major Canadian cities
- Court decisions and case law
- Charter rights and freedoms applications

## Deployment

Optimized for Replit deployment with:
- Dual-port configuration (5000 + 8080)
- Automated health checks
- Database connection pooling
- Background task scheduling for legal data updates

## License

This project is designed to make Canadian legal processes more accessible and fair for all Canadians, regardless of economic status.

## Contact

For support or inquiries: teresa@justice-bot.com