from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, session
from flask_pymongo import PyMongo
from bson import ObjectId
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from database import DatabaseService

# Models - editable document structure - models.py
from model.models import Section, Chapter, DocumentTemplate


app = Flask(__name__, static_folder='static')
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/smartscope")
mongo = PyMongo(app)
db_service = DatabaseService(mongo)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create a file handler
file_handler = RotatingFileHandler('logs/app.log', maxBytes=5000000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s'
))
console_handler.setLevel(logging.DEBUG)

# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

@app.route('/')
def index():
    logger.info('Accessing root page, redirecting to dashboard')
    return render_template('index.html')






# templates start
@app.route('/templates')
def templates():
    logger.info('Accessing templates page')
    templates = list(mongo.db.templates.find())
    return render_template('templates.html', templates=templates)

@app.route('/templates-list')
def templates_list():
    templates = list(mongo.db.templates.find())
    return render_template('templates_list.html', templates=templates)

@app.route('/delete-template/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    try:
        logger.info(f'Deleting template: {template_id}')
        result = mongo.db.templates.delete_one({'_id': ObjectId(template_id)})
        if result.deleted_count:
            logger.info(f'Successfully deleted template: {template_id}')
            templates = list(mongo.db.templates.find())
            return render_template('templates_list.html', templates=templates)
        else:
            logger.warning(f'Template not found for deletion: {template_id}')
            templates = list(mongo.db.templates.find())
            return render_template('templates_list.html', templates=templates)
    except Exception as e:
        logger.error(f'Error deleting template: {str(e)}', exc_info=True)
        templates = list(mongo.db.templates.find())
        return render_template('templates_list.html', templates=templates)

@app.route('/edit-template/<template_id>')
def edit_template(template_id):
    try:
        logger.info(f'Fetching template for edit: {template_id}')
        template = mongo.db.templates.find_one({'_id': ObjectId(template_id)})
        if template:
            return render_template('template_form.html', template=template)
        logger.warning(f'Template not found for edit: {template_id}')
        return '', 404
    except Exception as e:
        logger.error(f'Error fetching template for edit: {str(e)}', exc_info=True)
        return '', 500

@app.route('/template-form')
def template_form():
    return render_template('template_form.html')

@app.route('/create-template', methods=['POST'])
def create_template():
    try:
        # Get form data
        template_data = {
            'title': request.form.get('title'),
            'product': request.form.get('product'),
            'version': request.form.get('version'),
            'status': request.form.get('status'),
            'introduction': request.form.get('introduction'),
            'project_overview': request.form.get('project_overview'),
            'scope': request.form.get('scope')
        }
        
        # Insert into MongoDB
        result = mongo.db.templates.insert_one(template_data)
        
        if result.inserted_id:
            # Successfully saved
            templates = list(mongo.db.templates.find())
            return render_template('templates.html', templates=templates, message="Template created successfully!")
        else:
            # Failed to save
            return render_template('templates.html', templates=list(mongo.db.templates.find()), error="Failed to create template. Please try again.")
            
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        return render_template('templates.html', templates=list(mongo.db.templates.find()), error="An error occurred. Please try again.")
# templates end






@app.route('/dashboard')
def dashboard():
    logger.info('Accessing dashboard page')
    return render_template('dashboard.html')

@app.route('/users')
def users():
    logger.info('Accessing users page')
    return render_template('users.html')

@app.route('/settings')
def settings():
    logger.info('Accessing settings page')
    return render_template('settings.html')

# Document Routes
@app.route('/docs')
def docs():
    documents = list(mongo.db.documents.find())
    return render_template('docs_list.html', documents=documents)







# Helper function to find and update a nested document item by ID
def update_document_item(structure, item_id, content=None, title=None):
    """Recursively search and update an item in the document structure"""
    for item in structure:
        if str(item.get('id')) == str(item_id):
            if content is not None:
                item['content'] = content
            if title is not None:
                item['title'] = title
            return True
        
        # If this item has children, search there too
        if 'children' in item and item['children']:
            if update_document_item(item['children'], item_id, content, title):
                return True
    
    return False

# Function to schedule cleanup of inactive temporary documents
def cleanup_inactive_documents():
    """Remove temporary documents that have been inactive for more than 24 hours"""
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    try:
        inactive_docs = mongo.db.temp_documents.find({
            'last_activity': {'$lt': cutoff_time}
        })
        
        count = 0
        for doc in inactive_docs:
            mongo.db.temp_documents.delete_one({'_id': doc['_id']})
            count += 1
        
        if count > 0:
            logger.info(f"Cleaned up {count} inactive temporary documents")
    except Exception as e:
        logger.error(f"Error during temporary document cleanup: {str(e)}")

@app.route('/create-document3', methods=['GET', 'POST'])
def create_document3():
    # Get or create session ID
    session_id = request.cookies.get('session_id') or str(ObjectId())
    logger.info(f"Document session ID: {session_id}")
    
    if request.method == 'POST':
        # When "Save" is clicked - convert temp document to permanent
        temp_doc = mongo.db.temp_documents.find_one({'session_id': session_id})
        
        if temp_doc:
            # Create permanent document from temp
            permanent_doc = {
                'title': temp_doc.get('title', 'Untitled Document'),
                'structure': temp_doc.get('structure', []),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'user_id': session.get('user_id', None)  # If user authentication is used
            }
            
            # Insert as permanent document
            result = mongo.db.documents.insert_one(permanent_doc)
            logger.info(f"Created permanent document from temporary: {result.inserted_id}")
            
            # Delete the temporary document
            mongo.db.temp_documents.delete_one({'session_id': session_id})
            
            # Redirect to the document list or view
            return redirect(url_for('docs'))
        else:
            logger.warning(f"No temporary document found for session {session_id}")
    
    # For GET request
    # Check if there's an existing temporary document for this session
    temp_doc = mongo.db.temp_documents.find_one({'session_id': session_id})
    
    if not temp_doc:
        # Create a new temporary document with sample structure
        doc = DocumentTemplate(
            title="Project Report",
            chapters=[
                Chapter(
                    title="Chapter 1: Project Overview",
                    content="This chapter provides an overview of the project."
                ),
                Chapter(
                    title="Chapter 2: Project Activities",
                    content="This chapter details the main activities.",
                    sections=[
                        Section(
                            title="2.1: Software Installation",
                            content="How the software was installed.xxyy2"
                        ),
                        Section(
                            title="2.2: Software Tests",
                            content="Testing approach and results."
                        )
                    ]
                ),
                Chapter(
                    title="Chapter 3: Acceptance",
                    content="Acceptance procedures and criteria."
                ),
                Chapter(
                    title="Chapter 4: Final Payment",
                    content="Final financial arrangements."
                )
            ]
        )
        
        # Convert to dict
        doc_dict = doc.to_dict()
        
        # Process the structure to ensure each item has an ID
        def ensure_ids(items):
            processed = []
            for item in items:
                if 'id' not in item:
                    item['id'] = str(ObjectId())
                if 'children' in item and item['children']:
                    item['children'] = ensure_ids(item['children'])
                processed.append(item)
            return processed
        
        structure = ensure_ids(doc_dict['children'])
        
        # Store in temp collection
        temp_doc = {
            'session_id': session_id,
            'title': doc_dict['title'],
            'structure': structure,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        
        mongo.db.temp_documents.insert_one(temp_doc)
        logger.info(f"Created new temporary document for session {session_id}")
    else:
        # Update the last activity timestamp
        mongo.db.temp_documents.update_one(
            {'session_id': session_id},
            {'$set': {'last_activity': datetime.utcnow()}}
        )
        logger.info(f"Using existing temporary document for session {session_id}")
    
    # Set a cookie to identify this session
    response = make_response(render_template(
        'create_edit_doc.html', 
        document=temp_doc.get('structure', []),
        session_id=session_id
    ))
    response.set_cookie('session_id', session_id, max_age=60*60*24)  # 24 hour cookie
    return response

@app.route('/auto_save_document', methods=['POST'])
def auto_save_document():
    """Auto-save document content as user types"""
    session_id = request.cookies.get('session_id')
    if not session_id:
        logger.warning("Auto-save attempted without session ID")
        return jsonify({'status': 'error', 'message': 'No session found'}), 400
    
    try:
        data = request.json
        item_id = data.get('item_id')
        content = data.get('content')
        title = data.get('title')
        
        logger.debug(f"Auto-save for item {item_id} in session {session_id}")
        
        # Find the document
        temp_doc = mongo.db.temp_documents.find_one({'session_id': session_id})
        if not temp_doc:
            logger.warning(f"Auto-save: Document not found for session {session_id}")
            return jsonify({'status': 'error', 'message': 'Document not found'}), 404
        
        # Update the specific item in the structure
        updated = update_document_item(temp_doc['structure'], item_id, content, title)
        
        if updated:
            # Update the document in the database
            mongo.db.temp_documents.update_one(
                {'session_id': session_id},
                {
                    '$set': {
                        'structure': temp_doc['structure'],
                        'updated_at': datetime.utcnow(),
                        'last_activity': datetime.utcnow()
                    }
                }
            )
            logger.debug(f"Document auto-saved successfully for item {item_id}")
            return jsonify({
                'status': 'success', 
                'message': 'Document auto-saved',
                'timestamp': datetime.utcnow().strftime('%H:%M:%S')
            })
        
        logger.warning(f"Auto-save: Item {item_id} not found in document structure")
        return jsonify({'status': 'error', 'message': 'Item not found in document'}), 404
        
    except Exception as e:
        logger.error(f"Error during auto-save: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_document/<item_id>', methods=['GET'])
def get_document_item(item_id):
    """Get specific document item content for editing"""
    session_id = request.cookies.get('session_id')
    if not session_id:
        return "<p>Session expired. Please refresh the page.</p>", 400
    
    try:
        # Find the document
        temp_doc = mongo.db.temp_documents.find_one({'session_id': session_id})
        if not temp_doc:
            return "<p>Document not found. Please refresh the page.</p>", 404
        
        # Find the specific item (helper function)
        def find_item(items, target_id):
            for item in items:
                if str(item.get('id')) == str(target_id):
                    return item
                if 'children' in item and item['children']:
                    found = find_item(item['children'], target_id)
                    if found:
                        return found
            return None
        
        item = find_item(temp_doc['structure'], item_id)
        
        if item:
            # Render the editor with this item's content
            return render_template('partials/document_editor.html', 
                                  item=item,
                                  session_id=session_id)
        
        return "<p>Document section not found.</p>", 404
        
    except Exception as e:
        logger.error(f"Error getting document item: {str(e)}", exc_info=True)
        return f"<p>Error loading content: {str(e)}</p>", 500

@app.route('/add_document_item', methods=['POST'])
def add_document_item():
    """Add a new chapter or section to the document"""
    session_id = request.cookies.get('session_id')
    if not session_id:
        return jsonify({'status': 'error', 'message': 'No session found'}), 400
    
    try:
        parent_id = request.form.get('parent_id', None)  # None for root level
        title = request.form.get('title', 'New Section')
        
        # Find the document
        temp_doc = mongo.db.temp_documents.find_one({'session_id': session_id})
        if not temp_doc:
            return jsonify({'status': 'error', 'message': 'Document not found'}), 404
        
        # Create new item
        new_item = {
            'id': str(ObjectId()),
            'title': title,
            'content': '',
            'children': []
        }
        
        # If parent_id is None, add to root level
        if not parent_id:
            temp_doc['structure'].append(new_item)
            logger.info(f"Added new root-level item {new_item['id']}")
        else:
            # Find the parent and add to its children
            def add_to_parent(items, parent_id, new_item):
                for item in items:
                    if str(item.get('id')) == str(parent_id):
                        if 'children' not in item:
                            item['children'] = []
                        item['children'].append(new_item)
                        return True
                    if 'children' in item and item['children']:
                        if add_to_parent(item['children'], parent_id, new_item):
                            return True
                return False
            
            if not add_to_parent(temp_doc['structure'], parent_id, new_item):
                return jsonify({'status': 'error', 'message': 'Parent item not found'}), 404
            
            logger.info(f"Added new item {new_item['id']} under parent {parent_id}")
        
        # Update the document
        mongo.db.temp_documents.update_one(
            {'session_id': session_id},
            {
                '$set': {
                    'structure': temp_doc['structure'],
                    'updated_at': datetime.utcnow(),
                    'last_activity': datetime.utcnow()
                }
            }
        )
        
        # Return the HTML for the new item
        return render_template('partials/document_item.html', 
                              item=new_item,
                              is_new=True)
        
    except Exception as e:
        logger.error(f"Error adding document item: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Schedule the cleanup task to run daily if using a task scheduler
# For example, if using APScheduler:
# 
# from apscheduler.schedulers.background import BackgroundScheduler
# scheduler = BackgroundScheduler()
# scheduler.add_job(cleanup_inactive_documents, 'interval', hours=24)
# scheduler.start()

@app.route('/delete-doc/<doc_id>', methods=['DELETE'])
def delete_doc(doc_id):
    mongo.db.documents.delete_one({'_id': ObjectId(doc_id)})
    documents = list(mongo.db.documents.find())
    return render_template('docs_list.html', documents=documents)


if __name__ == '__main__':
    logger.info('Starting Flask application')
    app.run(host='0.0.0.0', debug=True, port=8000)