# SmartScope - Document Management System

A modern document management system built with Python, Flask, HTMX, and Bootstrap, featuring real-time editing, document templates, and user authentication.
<img width="1647" alt="image" src="https://github.com/user-attachments/assets/37c6be18-4b51-45e4-bf82-9211d348020f" />

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that is short and to the point. It lets people do anything they want with your code as long as they provide attribution back to you and don't hold you liable.

```
MIT License

Copyright (c) 2024 SmartScope

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
## Support

### Getting Help

- **Documentation**: Check the [documentation](docs/) for detailed guides and API references
- **Issues**: If you find a bug or have a feature request, please [open an issue](https://github.com/yourusername/smartscope/issues)
- **Discussions**: Join our [GitHub Discussions](https://github.com/yourusername/smartscope/discussions) for general questions and community support
- **Stack Overflow**: Use the tag `smartscope` when asking questions on Stack Overflow

### Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**
   - Use the GitHub issue tracker
   - Include detailed steps to reproduce
   - Add screenshots if applicable
   - Specify your environment details

2. **Suggest Features**
   - Open a feature request issue
   - Describe the use case
   - Explain why it would be valuable

3. **Submit Pull Requests**
   - Fork the repository
   - Create a feature branch
   - Add tests for new features
   - Update documentation
   - Follow our coding standards

<!-- ### Community

- **Discord**: Join our [Discord server](https://discord.gg/smartscope) for real-time discussions
- **Twitter**: Follow [@SmartScope](https://twitter.com/smartscope) for updates
- **Blog**: Read our [blog](https://blog.smartscope.dev) for tutorials and news -->

### Professional Support

For enterprise users or those needing dedicated support:

- **Email**: nik.x625@gmail.com
<!-- - **Slack**: [Join our Slack workspace](https://smartscope.slack.com) -->
<!-- - **Consulting**: Available for custom implementations and integrations -->

<!-- ### Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community approachable and respectable. -->
