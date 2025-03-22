from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
import os

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/chapters_db")
mongo = PyMongo(app)

@app.route('/')
def index():
    chapters = list(mongo.db.chapters.find())
    return render_template('index.html', chapters=chapters)

@app.route('/chapter/<chapter_id>')
def get_chapter(chapter_id):
    chapter = mongo.db.chapters.find_one({'_id': ObjectId(chapter_id)})
    if chapter:
        return render_template('chapter.html', chapter=chapter)
    return '', 404

@app.route('/api/chapters', methods=['GET'])
def get_chapters():
    chapters = list(mongo.db.chapters.find())
    return render_template('chapters_list.html', chapters=chapters)

@app.route('/api/chapters', methods=['POST'])
def add_chapter():
    try:
        title = request.form.get('title')
        if not title:
            return '', 400
        
        result = mongo.db.chapters.insert_one({
            'title': title,
            'paragraphs': []
        })
        
        # Return just the new chapter HTML
        chapter = mongo.db.chapters.find_one({'_id': result.inserted_id})
        return render_template('chapter_item.html', chapter=chapter)
    except Exception as e:
        return '', 400

@app.route('/api/chapters/<chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    mongo.db.chapters.delete_one({'_id': ObjectId(chapter_id)})
    return '', 204

@app.route('/api/chapters/<chapter_id>/paragraphs', methods=['POST'])
def add_paragraph(chapter_id):
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
            
        result = mongo.db.chapters.update_one(
            {'_id': ObjectId(chapter_id)},
            {'$push': {'paragraphs': {'content': data['content']}}}
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/chapters/<chapter_id>/paragraphs/<paragraph_index>', methods=['PUT'])
def update_paragraph(chapter_id, paragraph_index):
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400
            
        result = mongo.db.chapters.update_one(
            {'_id': ObjectId(chapter_id)},
            {'$set': {f'paragraphs.{paragraph_index}.content': data['content']}}
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/chapters/<chapter_id>/paragraphs/<paragraph_index>', methods=['DELETE'])
def delete_paragraph(chapter_id, paragraph_index):
    try:
        result = mongo.db.chapters.update_one(
            {'_id': ObjectId(chapter_id)},
            {'$unset': {f'paragraphs.{paragraph_index}': ""}}
        )
        result = mongo.db.chapters.update_one(
            {'_id': ObjectId(chapter_id)},
            {'$pull': {'paragraphs': None}}
        )
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000) 