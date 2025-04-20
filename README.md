# SmartScope Documentation Management System

A modern documentation management system built with Flask, HTMX, and MongoDB, featuring a dark theme and responsive design.

## Features

- **Document Management**
  - Create, edit, and organize documents
  - Hierarchical document structure with chapters and subchapters
  - Auto-save functionality
  - Draft management system

- **User Interface**
  - Dark theme with Bootstrap 5
  - Responsive design
  - Interactive document tree
  - Real-time content editing
  - HTMX-powered dynamic updates

- **Document Structure**
  - Introduction
  - Project Overview
  - Scope
  - Chapters and Subchapters
  - Dynamic content management

## Architecture

### Component Architecture

```mermaid
graph TD
    subgraph Frontend
        A[Main Layout] --> B[Document Tree]
        A --> C[Content Editor]
        B --> D[HTMX Events]
        C --> D
        D --> E[Auto-save]
    end

    subgraph Backend
        F[Flask App] --> G[MongoDB]
        D --> F
        E --> F
    end

    subgraph Data Flow
        H[User Actions] --> D
        D --> I[Content Updates]
        I --> E
        E --> J[Database]
    end
```

### Document Structure Flow

```mermaid
graph LR
    A[Document] --> B[Metadata]
    A --> C[Introduction]
    A --> D[Project Overview]
    A --> E[Scope]
    A --> F[Chapters]
    
    F --> G[Chapter 1]
    F --> H[Chapter 2]
    F --> I[Chapter N]
    
    G --> J[Subchapters]
    H --> K[Subchapters]
    I --> L[Subchapters]
```

## Workflows

### Document Creation Flow

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Backend
    participant DB

    User->>UI: Click "New Document"
    UI->>Backend: POST /create-document
    Backend->>DB: Create Draft Document
    DB-->>Backend: Document Created
    Backend-->>UI: Load Document Editor
    UI->>User: Show Document Tree
    
    loop Content Editing
        User->>UI: Edit Content
        UI->>Backend: Auto-save Content
        Backend->>DB: Update Document
    end
```

### Content Management Flow

```mermaid
stateDiagram-v2
    [*] --> DocumentList
    DocumentList --> DocumentEditor: Select Document
    DocumentEditor --> ContentEditor: Select Section
    ContentEditor --> AutoSave: Edit Content
    AutoSave --> ContentEditor: Save Changes
    ContentEditor --> DocumentEditor: Navigate
    DocumentEditor --> DocumentList: Save & Exit
```

### Auto-save Mechanism

```mermaid
graph LR
    A[User Input] --> B{Debounce Timer}
    B -->|500ms| C[HTMX Request]
    C --> D[Backend]
    D --> E[MongoDB]
    E --> F[Success Response]
    F --> G[Update Status]
```

### Document Tree Navigation

```mermaid
graph TD
    A[Document Tree] --> B[Introduction]
    A --> C[Project Overview]
    A --> D[Scope]
    A --> E[Chapters]
    
    E --> F[Chapter 1]
    E --> G[Chapter 2]
    
    F --> H[Subchapter 1.1]
    F --> I[Subchapter 1.2]
    
    G --> J[Subchapter 2.1]
    G --> K[Subchapter 2.2]
    
    style A fill:#2d3748,stroke:#4a5568
    style B fill:#2d3748,stroke:#4a5568
    style C fill:#2d3748,stroke:#4a5568
    style D fill:#2d3748,stroke:#4a5568
    style E fill:#2d3748,stroke:#4a5568
    style F fill:#2d3748,stroke:#4a5568
    style G fill:#2d3748,stroke:#4a5568
    style H fill:#2d3748,stroke:#4a5568
    style I fill:#2d3748,stroke:#4a5568
    style J fill:#2d3748,stroke:#4a5568
    style K fill:#2d3748,stroke:#4a5568
```

### Frontend Components

```mermaid
graph TD
    subgraph Layout
        A[Main Container] --> B[Sidebar]
        A --> C[Content Area]
    end

    subgraph Sidebar
        B --> D[Document Tree]
        D --> E[Section Items]
        E --> F[Chapter Items]
        F --> G[Subchapter Items]
    end

    subgraph Content
        C --> H[Editor Header]
        C --> I[Content Editor]
        C --> J[Save Controls]
    end
```

### Backend Services

```mermaid
graph LR
    subgraph API
        A[HTMX Endpoints] --> B[Document Service]
        A --> C[Content Service]
        A --> D[Auto-save Service]
    end

    subgraph Database
        B --> E[MongoDB]
        C --> E
        D --> E
    end
```

## Architecture

### Frontend
- **Templates**
  - `index.html`: Main application layout
  - `create_edit_document.html`: Document creation and editing interface
  - `docs_list.html`: Document listing and management
  - `settings.html`: Application settings

- **Static Assets**
  - `styles.css`: Main application styles
  - `styles_wizard.css`: Document creation wizard styles
  - Custom icons and components

### Backend
- **Routes**
  - Document Management:
    - `/docs`: List all documents
    - `/create-document`: Create new document
    - `/edit-doc/<doc_id>`: Edit existing document
    - `/delete-doc/<doc_id>`: Delete document
  - Content Management:
    - `/load-content/<section_id>`: Load document section content
    - `/load-content/chapter/<chapter_number>`: Load chapter content
    - `/save-content/<section_id>`: Save section content
    - `/auto-save-content/<section_id>`: Auto-save content changes
  - Auto-save:
    - `/auto-save`: Handle document auto-save

- **Database**
  - MongoDB document structure:
    ```json
    {
      "_id": ObjectId,
      "title": String,
      "product": String,
      "version": String,
      "status": String,
      "introduction": String,
      "project_overview": String,
      "scope": String,
      "chapters": [
        {
          "number": Integer,
          "title": String,
          "content": String,
          "subchapters": [
            {
              "number": Integer,
              "title": String,
              "content": String
            }
          ]
        }
      ],
      "created_at": DateTime,
      "updated_at": DateTime
    }
    ```

## Workflows

### Document Creation
1. User clicks "New Document"
2. System creates a draft document in MongoDB
3. User fills in document metadata (title, product, version)
4. User navigates through document sections using sidebar
5. Content is auto-saved as user types
6. User can manually save changes
7. Document status can be set to draft, review, or published

### Content Editing
1. User clicks a section in the document tree
2. Content editor loads in the main panel
3. Changes are auto-saved after 500ms of inactivity
4. User can manually save changes
5. Content is preserved between section navigation

### Document Management
1. Documents are listed with their metadata
2. Users can edit, delete, or view documents
3. Document status is clearly indicated
4. Changes are tracked with timestamps

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure MongoDB connection in `app.py`
4. Run the application:
   ```bash
   python app.py
   ```

## Development

### Adding New Features
1. Create new routes in `app.py`
2. Add corresponding templates
3. Update static assets as needed
4. Test with HTMX interactions

### Styling Guidelines
- Use Bootstrap 5 classes
- Follow dark theme color scheme
- Maintain responsive design
- Use HTMX for dynamic updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [HTMX](https://htmx.org/) for making dynamic web applications simple
- [Sortable.js](https://github.com/SortableJS/Sortable) for drag-and-drop functionality
- [Tailwind CSS](https://tailwindcss.com/) for the beautiful UI
- [Flask](https://flask.palletsprojects.com/) for the Python web framework 