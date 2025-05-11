# SmartScope - Document Management System

A modern document management system built with Python, Flask, HTMX, and Bootstrap, featuring real-time editing, document templates, and user authentication.

## Features

- **User Authentication**
  - Secure login and registration system
  - User session management
  - Account deletion with data cleanup

- **Document Management**
  - Create and edit documents with a rich text editor
  - Hierarchical document structure (chapters, sections)
  - Real-time auto-saving
  - Document templates
  - Document versioning

- **Modern UI/UX**
  - Responsive design using Bootstrap 5
  - Dark mode support
  - HTMX for dynamic content updates
  - Bootstrap Icons for visual elements
  - Real-time updates without page refreshes

- **Security**
  - Password hashing
  - Session management
  - Protected routes
  - Secure MongoDB integration

## Tech Stack

- **Backend**
  - Flask 3.1.0
  - MongoDB (PyMongo 4.12.0)
  - Flask-Login 0.6.3
  - Gunicorn 23.0.0

- **Frontend**
  - Bootstrap 5.3.2
  - HTMX
  - Bootstrap Icons 1.11.1

## Prerequisites

- Python 3.x
- Docker and Docker Compose
- MongoDB (included in Docker setup)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd docker_smartscope_htmx_bootstrap
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

## Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
flask run
```

## Project Structure

```
.
├── app.py                 # Main application file
├── config.py             # Configuration settings
├── database.py           # Database connection and services
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker services configuration
├── static/              # Static files (CSS, JS)
├── templates/           # HTML templates
│   ├── partials/       # Reusable template components
│   └── ...
├── models_for_documents/  # Document-related models
├── models_for_flask_login/ # Authentication models
└── logs/                # Application logs
```

## Features in Detail

### Document Management
- Create documents with a hierarchical structure
- Real-time auto-saving
- Document templates for quick creation
- Rich text editing capabilities
- Document versioning and history

### User Interface
- Responsive design that works on all devices
- Dark mode support
- Dynamic content updates using HTMX
- Bootstrap 5 components and utilities
- Modern icon set with Bootstrap Icons

### Security Features
- Secure password hashing
- Session-based authentication
- Protected routes and resources
- MongoDB security best practices

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Support

[Add support information here] 