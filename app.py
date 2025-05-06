from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, session, flash
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from bson import ObjectId

# Import configuration and database
from config import Config
from database import mongo, DatabaseService

# Models
from models_for_documents.models import Section, Chapter, DocumentTemplate
from models_for_flask_login.models import User
from flask_login import LoginManager, login_required, current_user, login_user, logout_user

# Create a logger 
# if the name is not specified, the root logger will be used and it will propagate to all other loggers, like MongoDB logs
logger = logging.getLogger('smartscope')

def create_app(config_class=Config):
    # Create and configure the app
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)
    
    # Initialize MongoDB
    mongo.init_app(app)
    
    # Setup logging
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

    # Set up the root logger
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(mongo, user_id)
    
    return app

# Create the app instance
app = create_app()
db_service = DatabaseService(mongo)

# Add custom template filters
@app.template_filter('date')
def date_filter(value, format='%Y-%m-%d %H:%M'):
    """Format a datetime object to a string using the given format."""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return value
    return value.strftime(format)

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

# Basic routes
@app.route('/')
@login_required
def index():
    logger.info('Accessing root page, redirecting to dashboard')
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    logger.info('Accessing dashboard page')
    # Get document and template counts
    documents_count = mongo.db.documents.count_documents({})
    templates_count = mongo.db.templates.count_documents({})
    
    # Get recent documents (limit to 5)
    recent_documents = list(mongo.db.documents.find().sort('created_at', -1).limit(5))
    
    return render_template('dashboard.html', 
                          documents_count=documents_count, 
                          templates_count=templates_count,
                          recent_documents=recent_documents)

@app.route('/users')
def users():
    logger.info('Accessing users page')
    return render_template('users.html')

@app.route('/settings')
def settings():
    logger.info('Accessing settings page')
    return render_template('settings.html')

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account and all associated data"""
    password = request.form.get('password')
    confirmation = request.form.get('confirm')
    
    # Verify password and confirmation
    if not password or not confirmation:
        logger.warning(f'Account deletion attempt missing password or confirmation for user: {current_user.username}')
        return render_template('settings.html', error="Password and confirmation required to delete account")
    
    # Verify correct password
    if not current_user.check_password(password):
        logger.warning(f'Account deletion attempt with incorrect password for user: {current_user.username}')
        return render_template('settings.html', error="Incorrect password")
    
    user_id = current_user._id
    username = current_user.username
    
    try:
        # Delete all user data
        # 1. Delete user's documents
        mongo.db.documents.delete_many({'user_id': user_id})
        
        # 2. Delete user's templates 
        mongo.db.templates.delete_many({'user_id': user_id})
        
        # 3. Delete temp documents
        mongo.db.temp_documents.delete_many({'user_id': user_id})
        
        # 4. Finally delete the user account
        mongo.db.users.delete_one({'_id': user_id})
        
        logger.info(f'Successfully deleted account for user: {username}')
        
        # Log the user out
        logout_user()
        
        # Clear all cookies
        response = make_response(redirect(url_for('login')))
        response.delete_cookie('session_id')
        
        # Add flash message to be displayed after redirect
        flash('Your account has been successfully deleted', 'success')
        
        return response
        
    except Exception as e:
        logger.error(f'Error deleting account for user {username}: {str(e)}', exc_info=True)
        return render_template('settings.html', error=f"Error deleting account: {str(e)}")

# Template routes
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

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user by username
        user = User.get_by_username(mongo, username)
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            # Log in the user
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        logger.warning(f'Failed login attempt for username: {username}')
        return render_template('login.html', error="Invalid username or password")
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('session_id')
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        if User.get_by_username(mongo, username):
            return render_template('register.html', error="Username already exists")
            
        if User.get_by_email(mongo, email):
            return render_template('register.html', error="Email already exists")
            
        # Create new user
        user = User(username=username, email=email, password=password)
        
        # Save to database
        mongo.db.users.insert_one(user.to_dict())
        
        # Log in the user
        login_user(user)
        
        # Redirect to success page instead of dashboard
        return redirect(url_for('registration_success'))
        
    return render_template('register.html')

@app.route('/registration-success')
@login_required
def registration_success():
    """Display registration success page"""
    logger.info(f'User {current_user.username} viewing registration success page')
    return render_template('registration_success.html')

# Document routes
@app.route('/docs')
def docs():
    documents = list(mongo.db.documents.find())
    return render_template('docs_list.html', documents=documents)

@login_required
@app.route('/create-edit-doc', methods=['GET', 'POST'])
def create_edit_doc():
    """
    Route handler for document creation and editing functionality.

    This function manages both the creation of new documents and editing of existing ones:

    For GET requests:
    - Retrieves or generates a unique session ID for document editing
    - Checks for an existing temporary document in the session
    - If none exists, creates a new temporary document with sample structure
    - Renders the document editing interface

    For POST requests:
    - Converts a temporary document into a permanent one
    - Saves the document structure and metadata to the database
    - Removes the temporary document
    - Redirects to the document list

    Parameters:
        None (uses session and request data)

    Returns:
        GET: Rendered template for document editing interface
        POST: Redirect to document list after saving

    Session Data:
        - Uses session_id cookie for document tracking
        - Optionally uses user_id for document ownership
    """

    # Get or create session ID
    session_id = request.cookies.get('session_id') or str(ObjectId())
    logger.info("current_user.is_authenticated: "+str(current_user.is_authenticated))
    #logger.info("current_user.id: "+str(current_user._id))

    logger.info(f"User ID: {current_user._id}")
    logger.info(f"Session ID: {session_id}")
    #logger.info(f"Document session ID: {session_id}, User ID: {current_user._id if current_user.is_authenticated else 'Not logged in'}")


    ### for testing
    if 0: #request.method == 'POST':
        # When "Save" is clicked - convert temp document to permanent
        draft_doc = mongo.db.documents.find_one({'user_id': user_id, 'doc_status': 'draft'})
        
        if draft_doc:
            # Create permanent document from temp
            saved_doc = {
                'title': draft_doc.get('title', 'Untitled Document'),
                'structure': draft_doc.get('structure', []),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'user_id': session.get('user_id', None)  # If user authentication is used
            }
            
            # Insert as permanent document
            result = mongo.db.documents.insert_one(saved_doc)
            logger.info(f"Created permanent document from temporary: {result.inserted_id}")
            
            
            # Redirect to the document list or view
            return redirect(url_for('docs'))
        else:
            logger.warning(f"No temporary document found for session {session_id}")
    
    # For GET request
    # Check if there's an existing temporary document for this session
    user_id = current_user._id


    draft_docs = list(mongo.db.documents.find({'user_id': user_id, 'doc_status': 'draft'}))
    
    # if there are duplicate draft documents for the user, use the most recent one
    if len(draft_docs) > 1:
        logger.warning(f"There are duplicate draft documents for the user {user_id}. The draft documents must be only one in this version for each user")
        # Use the most recent draft document
        draft_doc = max(draft_docs, key=lambda x: x.get('updated_at', datetime.min))
    else:
        draft_doc = draft_docs[0] if draft_docs else None

    # if there is no draft document for the user, create a new one
    if not draft_doc:
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
                            content="How the software was installed."
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
        
        # Store in documents collection as draft
        draft_doc = {
            'user_id': user_id,
            'title': doc_dict['title'],
            'structure': structure,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'doc_status': 'draft'
        }
        
        mongo.db.documents.insert_one(draft_doc)
        logger.info(f"Created new draft document for user {user_id}")
    else:
        # Update the last activity timestamp
        mongo.db.documents.update_one(
            {'user_id': user_id, 'doc_status': 'draft'},
            {'$set': {'last_activity': datetime.now()}}
        )
        logger.info(f"Using existing draft document for user {user_id}")
    
    logger.info("# structure is: "+str(draft_doc.get('structure', [])))

    # Set a cookie to identify this session
    response = make_response(render_template(
        'create_edit_doc.html', 
        document=draft_doc.get('structure', []),
        session_id=session_id
    ))

    response.set_cookie('session_id', session_id, max_age=60*60*24)  # 24 hour cookie
    return response

@app.route('/auto_save_document', methods=['POST'])
def auto_save_document():
    """Auto-save document content as user types"""
    user_id = current_user._id
    if not user_id:
        logger.warning("Auto-save attempted without user ID")
        return "<span class='text-danger'>No user found</span>", 400
    
    try:
        # Get form data instead of JSON data
        item_id = request.form.get('item_id')
        title = request.form.get('title')
        content = request.form.get('content')
        
        logger.debug(f"Auto-save for item {item_id} for user {user_id}")
        
        # Find the document
        draft_doc = mongo.db.documents.find_one({'user_id': user_id, 'doc_status': 'draft'})
        if not draft_doc:
            logger.warning(f"Auto-save: Document not found for user {user_id}")
            return "<span class='text-danger'>Document not found</span>", 404
        
        # Update the specific item in the structure
        updated = update_document_item(draft_doc['structure'], item_id, content, title)
        
        if updated:
            # Update the document in the database
            mongo.db.documents.update_one(
                {'user_id': user_id, 'doc_status': 'draft'},
                {
                    '$set': {
                        'structure': draft_doc['structure'],
                        'updated_at': datetime.now(),
                        'last_activity': datetime.now()
                    }
                }
            )
            timestamp = datetime.now().strftime('%H:%M:%S')
            logger.debug(f"Document auto-saved successfully for item {item_id}")
            return f"<span class='text-success'>Saved at {timestamp}</span>"
        
        logger.warning(f"Auto-save: Item {item_id} not found in document structure")
        return "<span class='text-danger'>Item not found in document</span>", 404
        
    except Exception as e:
        logger.error(f"Error during auto-save: {str(e)}", exc_info=True)
        return f"<span class='text-danger'>Error saving: {str(e)}</span>", 500

# this has been called when the user clicks on a document item to edit
@app.route('/get_document/<item_id>', methods=['GET'])
def get_document_item(item_id):
    """Get specific document item content for editing"""
    user_id = current_user._id
    
    #session_id = request.cookies.get('session_id')
    #if not session_id:
    #    return "<p>Session expired. Please refresh the page.</p>", 400
    
    try:
        # Find the document
        draft_doc = mongo.db.documents.find_one({'user_id': user_id})

        logger.info(f"Draft document found through get_document method is: {draft_doc}")
        logger.info("item id we are looking for is: "+str(item_id))
        if not draft_doc:
            logger.error(f"Draft document not found for user {user_id}")
            return "<p>Draft document not found. Check the system logs for more details.</p>", 404
        
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
        
        item = find_item(draft_doc['structure'], item_id)
        logger.info(f"Item found through get_document method is: {item}")
        if item:
            # Render the editor with this item's content
            return render_template('partials/document_editor.html', 
                                  item=item,
                                  user_id=user_id)
        
        logger.error(f"Document section not found for item {item_id}")
        return "<p>Document section not found. Check the system logs for more details.</p>", 404
        
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
    app.logger.info('Starting Flask application')
    app.run(host=Config.HOST, debug=Config.DEBUG, port=Config.PORT)