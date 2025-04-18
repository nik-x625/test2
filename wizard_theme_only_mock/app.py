from flask import Flask, render_template, request, jsonify, send_file
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import json
import os
from weasyprint import HTML
from datetime import datetime
import tempfile

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/sow_wizard"
mongo = PyMongo(app)

# Initialize database with default templates if empty
@app.before_first_request
def initialize_db():
    if mongo.db.templates.count_documents({}) == 0:
        default_template = {
            "name": "Standard SoW Template",
            "sections": [
                {
                    "id": "introduction",
                    "title": "Introduction",
                    "required": True,
                    "content": "<p>This Statement of Work (\"SOW\") is entered into between <span class=\"placeholder\" data-field=\"company_name\">Company Name</span> and <span class=\"placeholder\" data-field=\"client_name\">Client Name</span>.</p>"
                },
                {
                    "id": "scope",
                    "title": "Scope of Work",
                    "required": False,
                    "content": "<p>The scope of this project includes:</p><ul><li><span class=\"placeholder\" data-field=\"scope_item_1\">Scope item 1</span></li><li><span class=\"placeholder\" data-field=\"scope_item_2\">Scope item 2</span></li></ul>"
                },
                {
                    "id": "deliverables",
                    "title": "Deliverables",
                    "required": False,
                    "content": "<p>The following deliverables will be provided:</p><ul><li><span class=\"placeholder\" data-field=\"deliverable_1\">Deliverable 1</span></li><li><span class=\"placeholder\" data-field=\"deliverable_2\">Deliverable 2</span></li></ul>"
                },
                {
                    "id": "timeline",
                    "title": "Timeline",
                    "required": False,
                    "content": "<p>The project will be completed according to the following timeline:</p><p>Start Date: <span class=\"placeholder\" data-field=\"start_date\">Start Date</span></p><p>End Date: <span class=\"placeholder\" data-field=\"end_date\">End Date</span></p>"
                },
                {
                    "id": "pricing",
                    "title": "Pricing",
                    "required": False,
                    "content": "<p>The total cost for this project is <span class=\"placeholder\" data-field=\"total_cost\">$0.00</span>.</p><p>Payment terms: <span class=\"placeholder\" data-field=\"payment_terms\">Net 30</span></p>"
                },
                {
                    "id": "terms",
                    "title": "Terms and Conditions",
                    "required": True,
                    "content": "<p>This agreement is subject to the following terms and conditions:</p><p><span class=\"placeholder\" data-field=\"terms\">Standard terms and conditions apply.</span></p>"
                }
            ]
        }
        mongo.db.templates.insert_one(default_template)

@app.route('/')
def index():
    templates = list(mongo.db.templates.find())
    for template in templates:
        template['_id'] = str(template['_id'])
    return render_template('index.html', templates=templates)

@app.route('/wizard/<template_id>')
def wizard(template_id):
    template = mongo.db.templates.find_one({"_id": ObjectId(template_id)})
    if not template:
        return "Template not found", 404
    
    template['_id'] = str(template['_id'])
    return render_template('wizard.html', template=template)

@app.route('/section/<template_id>/<section_id>')
def get_section(template_id, section_id):
    template = mongo.db.templates.find_one({"_id": ObjectId(template_id)})
    if not template:
        return "Template not found", 404
    
    section = next((s for s in template['sections'] if s['id'] == section_id), None)
    if not section:
        return "Section not found", 404
    
    return render_template('section.html', section=section)

@app.route('/preview', methods=['POST'])
def preview():
    data = request.form
    template_id = data.get('template_id')
    included_sections = data.getlist('included_sections')
    field_values = {k: v for k, v in data.items() if k not in ['template_id', 'included_sections']}
    
    template = mongo.db.templates.find_one({"_id": ObjectId(template_id)})
    if not template:
        return "Template not found", 404
    
    # Filter sections based on user selection
    sections = [s for s in template['sections'] if s['id'] in included_sections or s.get('required', False)]
    
    # Replace placeholders with user values
    for section in sections:
        for field, value in field_values.items():
            section['content'] = section['content'].replace(
                f'<span class="placeholder" data-field="{field}">{field.replace("_", " ").title()}</span>',
                f'<span class="filled-value">{value}</span>'
            )
    
    return render_template('preview.html', template=template, sections=sections)

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    data = request.form
    template_id = data.get('template_id')
    included_sections = data.getlist('included_sections')
    field_values = {k: v for k, v in data.items() if k not in ['template_id', 'included_sections']}
    
    template = mongo.db.templates.find_one({"_id": ObjectId(template_id)})
    if not template:
        return "Template not found", 404
    
    # Filter sections based on user selection
    sections = [s for s in template['sections'] if s['id'] in included_sections or s.get('required', False)]
    
    # Replace placeholders with user values
    for section in sections:
        for field, value in field_values.items():
            section['content'] = section['content'].replace(
                f'<span class="placeholder" data-field="{field}">{field.replace("_", " ").title()}</span>',
                f'<span class="filled-value">{value}</span>'
            )
    
    # Generate HTML for PDF
    html_content = render_template('pdf_template.html', template=template, sections=sections)
    
    # Create a temporary file for the PDF
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    pdf_path = temp_file.name
    temp_file.close()
    
    # Generate PDF
    HTML(string=html_content).write_pdf(pdf_path)
    
    # Save document to database
    document = {
        "template_id": template_id,
        "title": f"{template['name']} - {datetime.now().strftime('%Y-%m-%d')}",
        "sections": sections,
        "field_values": field_values,
        "created_at": datetime.now()
    }
    mongo.db.documents.insert_one(document)
    
    return send_file(pdf_path, as_attachment=True, download_name=f"SoW_{datetime.now().strftime('%Y%m%d')}.pdf")

if __name__ == '__main__':
    app.run(debug=True)
