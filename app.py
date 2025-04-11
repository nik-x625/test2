from flask import Flask, render_template, request, jsonify
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

@app.route('/test1')
def test1():
    logger.info('in test1')
    chapters = db_service.get_chapters()
    return render_template('test1.html', chapters=chapters)

@app.route('/test2')
def test2():
    logger.info('in test2')
    chapters = db_service.get_chapters()
    return render_template('test2.html', chapters=chapters)

@app.route('/test3')
def test3():
    logger.info('Accessing test3 page')
    # Mock data for demonstration
    entries = [
        {"title": "Geographic Distribution", "category": "Sales Content/General/Organization", "date": "Dec 13, 2019", "score": 100},
        {"title": "Customer Demographics", "category": "Market Research", "date": "Jan 15, 2020", "score": 95},
        {"title": "Product Usage Statistics", "category": "Analytics", "date": "Feb 20, 2020", "score": 88},
    ]
    return render_template('test3.html', entries=entries)

@app.route('/test4')
def test4():
    logger.info('Accessing test4 page')
    # Mock data for demonstration
    return render_template('test4.html')

@app.route('/get_some_html')
def get_some_html():
    logger.info('Accessing get_some_html page')
    # Mock data for demonstration
    return "some new content from server is here!"

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

@app.route('/delete-template/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    try:
        logger.info(f'Deleting template: {template_id}')
        result = mongo.db.templates.delete_one({'_id': ObjectId(template_id)})
        if result.deleted_count:
            logger.info(f'Successfully deleted template: {template_id}')
            return '', 204
        else:
            logger.warning(f'Template not found for deletion: {template_id}')
            return '', 404
    except Exception as e:
        logger.error(f'Error deleting template: {str(e)}', exc_info=True)
        return '', 500

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
        
        # Insert into MongoDB using database service
        result = db_service.create_template(template_data)
        # Fetch updated templates list after creation
        templates = db_service.get_all_templates()
        if result:
            # Successfully saved
            return render_template('templates.html', message="Template created successfully!")
        else:
            # Failed to save
            return render_template('template_form.html', error="Failed to create template. Please try again.")
            
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        return render_template('template_form.html', error="An error occurred. Please try again.")

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

if __name__ == '__main__':
    logger.info('Starting Flask application')
    app.run(host='0.0.0.0', debug=True, port=8000)