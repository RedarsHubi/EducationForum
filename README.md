# Educational Forum Application Documentation

## Authors

- Malika Oubilla - Full Stack Developer
- Reda Cherkoaui - Full Stack Developer

Both authors contributed to all aspects of the project, including backend development, frontend design, database management, and deployment.

## 1. Introduction and System Overview

### 1.1 Purpose

This document provides comprehensive documentation for our educational forum application. It is designed to serve as a reference for developers, administrators, and users of the system.

### 1.2 System Architecture

Our educational forum is built using the following technologies:

- **Backend**: Python with Django framework
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, and Vanilla JavaScript
- **Real-time features**: WebSockets

### 1.3 Key Features

- User Authentication
- Live Chat
- Private Messaging
- Reputation System (Upvote/Downvote)
- Report Handling
- Subject-based Organization (Mathematics, Physics, History, Psychology, Computer Science, etc.)

### 1.4 Target Audience

This documentation is intended for:

- Developers maintaining or extending the system
- System administrators
- Educators and students using the forum
- Moderators managing subject-specific discussions

### 1.5 Educational Focus

This forum is designed to facilitate academic discussions and collaborative learning across various subjects. It provides a platform for students and educators to engage in topic-specific conversations, share knowledge, and seek assistance in their studies.

## 2. System Requirements and Setup

### 2.1 Server Requirements

- Python 3.8+
- PostgreSQL 12+
- Django 3.2+
- Daphne (for WebSocket support)

### 2.2 Client Requirements

- Modern web browser with JavaScript enabled
- Internet connection

### 2.3 Development Environment Setup

1. Clone the repository:

  git clone [repository_url]
  cd [project_directory]

2. Create and activate a virtual environment:
In Unix systems:
  python -m venv venv
  source venv/bin/activate
In PowerShell:
  ./.venv/Scripts/Activate.ps1

3. Install dependencies:
  
  pip install -r requirements.txt

4. Set up the PostgreSQL database:
- Create a new database
- Update the database configuration in `settings.py`

5. Run migrations:
  python manage.py migrate

6. Start the development server:
  daphne [project_name].asgi:application

### 2.4 Production Deployment

- The application is deployed using Railway
- Ensure all necessary environment variables are set in Railway's dashboard
- Configure the PostgreSQL add-on in Railway
- Set up HTTPS (Railway typically handles this automatically)
- Ensure Daphne is properly configured to handle both HTTP and WebSocket connections

### 2.5 WebSocket Configuration

- Daphne is used to handle WebSocket connections for live chat and private messaging features
- Ensure the `ASGI_APPLICATION` setting in `settings.py` is correctly pointing to your ASGI application

## 3. Key Components and Features

### 3.1 User Management

- Custom user model with academic-focused fields
- JWT-based authentication
- User profiles with bio, institution, and subjects of interest

### 3.2 Forum Structure

- Subject-based organization (Math, Physics, History, etc.)
- Threads and posts within each subject
- Upvote/downvote system for posts

### 3.3 Real-time Features

- Live chat for group discussions
- Private messaging between users
- Implemented using WebSockets via Daphne

### 3.4 Reputation System

- Users gain/lose reputation based on post votes
- Reputation displayed on user profiles

### 3.5 Moderation Tools

- Report system for flagging inappropriate content
- Moderator dashboard for handling reports

## Technical Implementation

- **Backend**: Django (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **WebSockets**: Daphne
- **Deployment**: Railway platform

## Security and Performance

- HTTPS encryption
- JWT for secure authentication
- Database optimizations and caching as needed

---

This documentation provides an overview of your educational forum's structure, features, and technical implementation. For more detailed information on specific components or functionalities, refer to the relevant sections in the codebase or consult the development team.