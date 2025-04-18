from datetime import datetime

# MongoDB document schemas (for reference, not enforced by MongoDB)

template_schema = {
    "name": str,  # Name of the template
    "sections": [
        {
            "id": str,  # Unique identifier for the section
            "title": str,  # Display title
            "required": bool,  # Whether this section is required
            "content": str,  # HTML content with placeholders
        }
    ]
}

document_schema = {
    "template_id": str,  # Reference to the template
    "title": str,  # Document title
    "sections": list,  # List of included sections
    "field_values": dict,  # Values for placeholders
    "created_at": datetime,  # Creation timestamp
}

user_schema = {
    "username": str,  # Username
    "email": str,  # Email address
    "saved_documents": list,  # List of saved document IDs
    "created_at": datetime,  # Account creation timestamp
}
