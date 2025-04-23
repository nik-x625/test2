from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_pymongo import PyMongo
from bson import ObjectId
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from database import DatabaseService

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


@app.route('/chapter/<chapter_id>')
def get_chapter(chapter_id):
    logger.info(f'Fetching chapter with ID: {chapter_id}')
    chapter = db_service.get_chapter(chapter_id)
    if chapter:
        logger.debug(f'Found chapter: {chapter.get("title")}')
        return render_template('chapter.html', chapter=chapter)
    logger.warning(f'Chapter not found with ID: {chapter_id}')
    return '', 404

@app.route('/api/chapters', methods=['GET'])
def get_chapters():
    logger.debug('Fetching all chapters')
    chapters = db_service.get_chapters()
    return render_template('chapters_list.html', chapters=chapters)

@app.route('/api/chapters', methods=['POST'])
def add_chapter():
    try:
        title = request.form.get('title')
        if not title:
            logger.warning('Attempted to add chapter with empty title')
            return '', 400
        
        logger.info(f'Adding new chapter: {title}')
        chapter = db_service.create_chapter(title)
        logger.debug(f'Successfully added chapter with ID: {chapter["_id"]}')
        return render_template('chapter_item.html', chapter=chapter)
    except Exception as e:
        logger.error(f'Error adding chapter: {str(e)}', exc_info=True)
        return '', 400

@app.route('/api/chapters/reorder', methods=['POST'])
def reorder_chapters():
    try:
        chapter_ids = request.form.getlist('chapter_id')
        if not chapter_ids:
            logger.warning('Attempted to reorder chapters with no IDs provided')
            return '', 400
            
        logger.info(f'Reordering {len(chapter_ids)} chapters')
        chapters = db_service.update_chapter_order(chapter_ids)
        logger.info('Successfully reordered chapters')
        return render_template('chapters_list.html', chapters=chapters)
    except Exception as e:
        logger.error(f'Error in reorder_chapters: {str(e)}', exc_info=True)
        return '', 500

@app.route('/api/chapters/<chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    logger.info(f'Attempting to delete chapter: {chapter_id}')
    result = db_service.delete_chapter(chapter_id)
    if result.deleted_count:
        logger.info(f'Successfully deleted chapter: {chapter_id}')
    else:
        logger.warning(f'Chapter not found for deletion: {chapter_id}')
    return '', 204

@app.route('/api/chapters/<chapter_id>/paragraphs', methods=['POST'])
def add_paragraph(chapter_id):
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            logger.warning(f'Attempted to add paragraph to chapter {chapter_id} with invalid data')
            return jsonify({'error': 'Content is required'}), 400
            
        logger.info(f'Adding paragraph to chapter: {chapter_id}')
        result = db_service.add_paragraph(chapter_id, data['content'])
        logger.debug(f'Successfully added paragraph to chapter: {chapter_id}')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'Error adding paragraph to chapter {chapter_id}: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/api/chapters/<chapter_id>/paragraphs/<paragraph_index>', methods=['PUT'])
def update_paragraph(chapter_id, paragraph_index):
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            logger.warning(f'Attempted to update paragraph {paragraph_index} in chapter {chapter_id} with invalid data')
            return jsonify({'error': 'Content is required'}), 400
            
        logger.info(f'Updating paragraph {paragraph_index} in chapter: {chapter_id}')
        result = db_service.update_paragraph(chapter_id, paragraph_index, data['content'])
        logger.debug(f'Successfully updated paragraph {paragraph_index} in chapter: {chapter_id}')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'Error updating paragraph {paragraph_index} in chapter {chapter_id}: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/api/chapters/<chapter_id>/paragraphs/<paragraph_index>', methods=['DELETE'])
def delete_paragraph(chapter_id, paragraph_index):
    try:
        logger.info(f'Attempting to delete paragraph {paragraph_index} from chapter: {chapter_id}')
        result = db_service.delete_paragraph(chapter_id, paragraph_index)
        logger.debug(f'Successfully deleted paragraph {paragraph_index} from chapter: {chapter_id}')
        return '', 204
    except Exception as e:
        logger.error(f'Error deleting paragraph {paragraph_index} from chapter {chapter_id}: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/api/chapters/<chapter_id>/edit', methods=['GET'])
def edit_chapter(chapter_id):
    try:
        logger.info(f'Fetching chapter for edit: {chapter_id}')
        chapter = db_service.get_chapter(chapter_id)
        if chapter:
            return render_template('chapter_edit.html', chapter=chapter)
        logger.warning(f'Chapter not found for edit: {chapter_id}')
        return '', 404
    except Exception as e:
        logger.error(f'Error fetching chapter for edit: {str(e)}', exc_info=True)
        return '', 500

@app.route('/api/chapters/<chapter_id>/cancel', methods=['GET'])
def cancel_edit(chapter_id):
    try:
        logger.info(f'Canceling edit for chapter: {chapter_id}')
        chapter = db_service.get_chapter(chapter_id)
        if chapter:
            return render_template('chapter_item.html', chapter=chapter)
        logger.warning(f'Chapter not found for cancel: {chapter_id}')
        return '', 404
    except Exception as e:
        logger.error(f'Error canceling chapter edit: {str(e)}', exc_info=True)
        return '', 500

@app.route('/api/chapters/<chapter_id>', methods=['PUT'])
def update_chapter(chapter_id):
    try:
        title = request.form.get('title')
        if not title:
            logger.warning(f'Attempted to update chapter {chapter_id} with empty title')
            return '', 400
            
        logger.info(f'Updating chapter {chapter_id} with title: {title}')
        if db_service.update_chapter(chapter_id, title):
            chapter = db_service.get_chapter(chapter_id)
            logger.debug(f'Successfully updated chapter {chapter_id}')
            return render_template('chapter_item.html', chapter=chapter)
        else:
            logger.warning(f'No changes made to chapter {chapter_id}')
            return '', 400
    except Exception as e:
        logger.error(f'Error updating chapter {chapter_id}: {str(e)}', exc_info=True)
        return '', 500

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

@app.route('/update-template/<template_id>', methods=['PUT'])
def update_template(template_id):
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
        
        # Update in MongoDB
        result = mongo.db.templates.update_one(
            {'_id': ObjectId(template_id)},
            {'$set': template_data}
        )
        
        if result.modified_count:
            # Successfully updated
            templates = list(mongo.db.templates.find())
            return render_template('templates.html', templates=templates, message="Template updated successfully!")
        else:
            # Failed to update
            return render_template('templates.html', templates=list(mongo.db.templates.find()), error="Failed to update template. Please try again.")
            
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        return render_template('templates.html', templates=list(mongo.db.templates.find()), error="An error occurred. Please try again.")

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



@app.route('/wizard/step2/<template_id>')
def wizard_step2(template_id):
    template = mongo.db.templates.find_one({'_id': ObjectId(template_id)})
    if not template:
        return "Template not found", 404
    return render_template('wizard_step2.html', template=template)

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





@app.route('/create-document1')
def create_document1():
    #templates = list(mongo.db.templates.find())
    return render_template('wizard.html')#, templates=templates)

@app.route('/create-document2', methods=['GET', 'POST'])
def create_document2():
    if request.method == 'POST':
        doc_data = {
            'title': request.form.get('title'),
            'product': request.form.get('product'),
            'version': request.form.get('version'),
            'status': request.form.get('status'),
            'content': request.form.get('content'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        mongo.db.documents.insert_one(doc_data)
        return redirect(url_for('docs'))
    return render_template('create_edit_document.html')


@app.route('/create-document3', methods=['GET', 'POST'])
def create_document3():
    if request.method == 'POST':
        doc_data = {
            'title': request.form.get('title'),
            'product': request.form.get('product'),
            'version': request.form.get('version'),
            'status': request.form.get('status'),
            'content': request.form.get('content'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        mongo.db.documents.insert_one(doc_data)
        return redirect(url_for('docs'))
    return render_template('create_doc_template3.html')






@app.route('/edit-doc/<doc_id>', methods=['GET', 'POST'])
def edit_doc(doc_id):
    if request.method == 'POST':
        doc_data = {
            'title': request.form.get('title'),
            'product': request.form.get('product'),
            'version': request.form.get('version'),
            'status': request.form.get('status'),
            'content': request.form.get('content'),
            'updated_at': datetime.utcnow()
        }
        mongo.db.documents.update_one({'_id': ObjectId(doc_id)}, {'$set': doc_data})
        return redirect(url_for('docs'))
    
    doc = mongo.db.documents.find_one({'_id': ObjectId(doc_id)})
    if not doc:
        return "Document not found", 404
    return render_template('create_edit_document.html', doc=doc)





@app.route('/delete-doc/<doc_id>', methods=['DELETE'])
def delete_doc(doc_id):
    mongo.db.documents.delete_one({'_id': ObjectId(doc_id)})
    documents = list(mongo.db.documents.find())
    return render_template('docs_list.html', documents=documents)

@app.route('/auto-save', methods=['POST'])
def auto_save():
    logger.info('Auto-saving document')
    try:
        data = request.form.to_dict()
        
        # If this is a new document (no _id), create a draft
        if '_id' not in data:
            # Generate a temporary ID for the draft
            temp_id = str(ObjectId())
            data['_id'] = temp_id
            data['status'] = 'draft'
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            
            # Insert or update the draft
            mongo.db.documents.update_one(
                {'_id': temp_id},
                {'$set': data},
                upsert=True
            )
        else:
            # Update existing document
            doc_id = data.pop('_id')
            data['updated_at'] = datetime.utcnow()
            
            mongo.db.documents.update_one(
                {'_id': ObjectId(doc_id)},
                {'$set': data}
            )
        
        return '', 204  # No content response
        
    except Exception as e:
        logger.error(f"Auto-save error: {str(e)}")
        return '', 500

@app.route('/add-chapter', methods=['GET'])
def add_chapter_new():
    try:
        # Get the current chapter count from the request
        chapter_count = int(request.args.get('count', 0))
        chapter_index = chapter_count + 1
        
        # Get the current document ID if it exists
        doc_id = request.args.get('doc_id')
        
        # Create a new chapter in the document if doc_id exists
        if doc_id:
            mongo.db.documents.update_one(
                {'_id': ObjectId(doc_id)},
                {'$push': {'chapters': {
                    'title': f'Chapter {chapter_index}',
                    'content': '',
                    'subchapters': []
                }}}
            )
        
        return render_template('chapter_section.html', 
                            chapter_index=chapter_index,
                            chapter_number=chapter_index,
                            chapter_title=f'Chapter {chapter_index}')
    except Exception as e:
        logger.error(f"Error adding chapter: {str(e)}")
        return '', 500

@app.route('/add-subchapter/<chapter_index>', methods=['GET'])
def add_subchapter(chapter_index):
    try:
        # Get the current subchapter count from the request
        subchapter_count = int(request.args.get('count', 0))
        subchapter_index = subchapter_count + 1
        
        # Get the current document ID if it exists
        doc_id = request.args.get('doc_id')
        
        # Add subchapter to the document if doc_id exists
        if doc_id:
            mongo.db.documents.update_one(
                {'_id': ObjectId(doc_id)},
                {'$push': {f'chapters.{int(chapter_index)-1}.subchapters': {
                    'title': f'Subchapter {subchapter_index}',
                    'content': ''
                }}}
            )
        
        return render_template('subchapter_section.html',
                            chapter_index=chapter_index,
                            subchapter_index=subchapter_index,
                            chapter_number=chapter_index,
                            subchapter_number=subchapter_index,
                            subchapter_title=f'Subchapter {subchapter_index}')
    except Exception as e:
        logger.error(f"Error adding subchapter: {str(e)}")
        return '', 500

@app.route('/remove-chapter/<chapter_index>', methods=['DELETE'])
def remove_chapter(chapter_index):
    try:
        # Get the current document ID if it exists
        doc_id = request.args.get('doc_id')
        
        # Remove chapter from the document if doc_id exists
        if doc_id:
            mongo.db.documents.update_one(
                {'_id': ObjectId(doc_id)},
                {'$unset': {f'chapters.{int(chapter_index)-1}': 1}}
            )
            mongo.db.documents.update_one(
                {'_id': ObjectId(doc_id)},
                {'$pull': {'chapters': None}}
            )
        
        return '', 204
    except Exception as e:
        logger.error(f"Error removing chapter: {str(e)}")
        return '', 500

@app.route('/remove-subchapter/<chapter_index>/<subchapter_index>', methods=['DELETE'])
def remove_subchapter(chapter_index, subchapter_index):
    try:
        # Get the current document ID if it exists
        doc_id = request.args.get('doc_id')
        
        # Remove subchapter from the document if doc_id exists
        if doc_id:
            mongo.db.documents.update_one(
                {'_id': ObjectId(doc_id)},
                {'$unset': {f'chapters.{int(chapter_index)-1}.subchapters.{int(subchapter_index)-1}': 1}}
            )
            mongo.db.documents.update_one(
                {'_id': ObjectId(doc_id)},
                {'$pull': {f'chapters.{int(chapter_index)-1}.subchapters': None}}
            )
        
        return '', 204
    except Exception as e:
        logger.error(f"Error removing subchapter: {str(e)}")
        return '', 500

if __name__ == '__main__':
    logger.info('Starting Flask application')
    app.run(host='0.0.0.0', debug=True, port=8000)