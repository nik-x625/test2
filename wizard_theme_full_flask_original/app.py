from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import json
import os
from datetime import datetime
import tempfile
import uuid
from werkzeug.utils import secure_filename
import re
from weasyprint import HTML, CSS
import io

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://mongo:27017/sow_wizard")
mongo = PyMongo(app)

# Custom Jinja2 filters
@app.template_filter('json')
def json_filter(s):
    return json.dumps(s)

@app.template_filter('regex_findall')
def regex_findall(pattern, string):
    return re.findall(pattern, string)

@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    return dict(now=now)

# Initialize database with default templates
@app.before_first_request
def initialize_db():
    if mongo.db.templates.count_documents({}) == 0:
        # Business Proposal Template
        proposal_template = {
            "name": "Business Proposal",
            "description": "A comprehensive business proposal with executive summary, solution details, pricing, and terms.",
            "icon": "file-invoice",
            "sections": [
                {
                    "id": "executive-summary",
                    "title": "Executive Summary",
                    "required": True,
                    "description": "Overview of the proposal and key benefits",
                    "content": "<p>This proposal is submitted by <span class=\"placeholder\" data-field=\"company_name\">Company Name</span> to <span class=\"placeholder\" data-field=\"client_name\">Client Name</span>.</p><p><span class=\"placeholder\" data-field=\"summary\">Provide a brief overview of the proposal...</span></p><p><strong>Key Benefits:</strong></p><p><span class=\"placeholder\" data-field=\"key_benefits\">List the main benefits of your proposal...</span></p>"
                },
                {
                    "id": "company-background",
                    "title": "Company Background",
                    "required": False,
                    "description": "Information about your company",
                    "content": "<p><span class=\"placeholder\" data-field=\"company_description\">Describe your company...</span></p><p><strong>Years in Business:</strong> <span class=\"placeholder\" data-field=\"years_in_business\">Number of years</span></p>"
                },
                {
                    "id": "problem-statement",
                    "title": "Problem Statement",
                    "required": False,
                    "description": "Description of the client's challenges",
                    "content": "<p><span class=\"placeholder\" data-field=\"problem_description\">Describe the client's challenges...</span></p>"
                },
                {
                    "id": "proposed-solution",
                    "title": "Proposed Solution",
                    "required": True,
                    "description": "Your solution to the client's problems",
                    "content": "<p><span class=\"placeholder\" data-field=\"solution_description\">Describe your proposed solution...</span></p><p><strong>Key Features:</strong></p><p><span class=\"placeholder\" data-field=\"key_features\">List the key features of your solution...</span></p>"
                },
                {
                    "id": "methodology",
                    "title": "Methodology",
                    "required": False,
                    "description": "How you will implement the solution",
                    "content": "<p><span class=\"placeholder\" data-field=\"methodology_description\">Describe your methodology...</span></p>"
                },
                {
                    "id": "timeline",
                    "title": "Timeline",
                    "required": False,
                    "description": "Project schedule and milestones",
                    "content": "<p><strong>Start Date:</strong> <span class=\"placeholder\" data-field=\"start_date\">Start Date</span></p><p><strong>End Date:</strong> <span class=\"placeholder\" data-field=\"end_date\">End Date</span></p><p><strong>Milestones:</strong></p><p><span class=\"placeholder\" data-field=\"milestones\">List key project milestones...</span></p>"
                },
                {
                    "id": "pricing",
                    "title": "Pricing",
                    "required": True,
                    "description": "Cost breakdown and payment terms",
                    "content": "<p><strong>Total Cost:</strong> <span class=\"placeholder\" data-field=\"total_cost\">$0.00</span></p><p><strong>Payment Terms:</strong> <span class=\"placeholder\" data-field=\"payment_terms\">Net 30</span></p><p><strong>Payment Schedule:</strong></p><p><span class=\"placeholder\" data-field=\"payment_schedule\">Describe the payment schedule...</span></p>"
                },
                {
                    "id": "team",
                    "title": "Team",
                    "required": False,
                    "description": "Key personnel who will work on the project",
                    "content": "<p><span class=\"placeholder\" data-field=\"team_description\">Describe the key team members who will work on this project...</span></p>"
                },
                {
                    "id": "terms",
                    "title": "Terms and Conditions",
                    "required": True,
                    "description": "Legal terms of the proposal",
                    "content": "<p><span class=\"placeholder\" data-field=\"terms_conditions\">Standard terms and conditions apply...</span></p>"
                }
            ]
        }
        
        # Statement of Work Template
        sow_template = {
            "name": "Statement of Work",
            "description": "Detailed SoW template with project scope, deliverables, timeline, and acceptance criteria.",
            "icon": "file-contract",
            "sections": [
                {
                    "id": "introduction",
                    "title": "Introduction",
                    "required": True,
                    "description": "Overview of the project and parties involved",
                    "content": "<p>This Statement of Work (\"SOW\") is entered into between <span class=\"placeholder\" data-field=\"company_name\">Company Name</span> and <span class=\"placeholder\" data-field=\"client_name\">Client Name</span>.</p><p><span class=\"placeholder\" data-field=\"project_overview\">Provide a brief overview of the project...</span></p>"
                },
                {
                    "id": "scope",
                    "title": "Scope of Work",
                    "required": True,
                    "description": "Detailed description of work to be performed",
                    "content": "<p><span class=\"placeholder\" data-field=\"scope_description\">Describe the scope of work...</span></p><p><strong>In Scope:</strong></p><p><span class=\"placeholder\" data-field=\"in_scope\">List items that are in scope...</span></p><p><strong>Out of Scope:</strong></p><p><span class=\"placeholder\" data-field=\"out_of_scope\">List items that are out of scope...</span></p>"
                },
                {
                    "id": "deliverables",
                    "title": "Deliverables",
                    "required": True,
                    "description": "Specific outputs to be provided",
                    "content": "<p><span class=\"placeholder\" data-field=\"deliverables_description\">List all deliverables...</span></p>"
                },
                {
                    "id": "timeline",
                    "title": "Timeline",
                    "required": True,
                    "description": "Project schedule and milestones",
                    "content": "<p><strong>Start Date:</strong> <span class=\"placeholder\" data-field=\"start_date\">Start Date</span></p><p><strong>End Date:</strong> <span class=\"placeholder\" data-field=\"end_date\">End Date</span></p><p><strong>Milestones:</strong></p><p><span class=\"placeholder\" data-field=\"milestones\">List key project milestones...</span></p>"
                },
                {
                    "id": "acceptance-criteria",
                    "title": "Acceptance Criteria",
                    "required": True,
                    "description": "Standards for deliverable approval",
                    "content": "<p><span class=\"placeholder\" data-field=\"acceptance_criteria\">Describe the acceptance criteria...</span></p>"
                },
                {
                    "id": "responsibilities",
                    "title": "Responsibilities",
                    "required": False,
                    "description": "Client and vendor responsibilities",
                    "content": "<p><strong>Company Responsibilities:</strong></p><p><span class=\"placeholder\" data-field=\"company_responsibilities\">List company responsibilities...</span></p><p><strong>Client Responsibilities:</strong></p><p><span class=\"placeholder\" data-field=\"client_responsibilities\">List client responsibilities...</span></p>"
                },
                {
                    "id": "assumptions",
                    "title": "Assumptions",
                    "required": False,
                    "description": "Project assumptions and dependencies",
                    "content": "<p><span class=\"placeholder\" data-field=\"assumptions\">List project assumptions and dependencies...</span></p>"
                },
                {
                    "id": "terms",
                    "title": "Terms and Conditions",
                    "required": True,
                    "description": "Legal terms of the agreement",
                    "content": "<p><span class=\"placeholder\" data-field=\"terms_conditions\">Standard terms and conditions apply...</span></p>"
                }
            ]
        }
        
        # Service Contract Template
        contract_template = {
            "name": "Service Contract",
            "description": "Legal service contract with terms and conditions, service details, and payment schedules.",
            "icon": "file-signature",
            "sections": [
                {
                    "id": "parties",
                    "title": "Parties",
                    "required": True,
                    "description": "Identification of the contracting parties",
                    "content": "<p>This Service Agreement (\"Agreement\") is made and entered into as of <span class=\"placeholder\" data-field=\"effective_date\">Effective Date</span>, by and between <span class=\"placeholder\" data-field=\"company_name\">Company Name</span> (\"Provider\") and <span class=\"placeholder\" data-field=\"client_name\">Client Name</span> (\"Client\").</p>"
                },
                {
                    "id": "services",
                    "title": "Services",
                    "required": True,
                    "description": "Description of services to be provided",
                    "content": "<p><span class=\"placeholder\" data-field=\"services_description\">Describe the services to be provided...</span></p>"
                },
                {
                    "id": "term",
                    "title": "Term",
                    "required": True,
                    "description": "Duration of the contract",
                    "content": "<p>This Agreement shall commence on <span class=\"placeholder\" data-field=\"start_date\">Start Date</span> and continue until <span class=\"placeholder\" data-field=\"end_date\">End Date</span>, unless earlier terminated as provided herein.</p>"
                },
                {
                    "id": "compensation",
                    "title": "Compensation",
                    "required": True,
                    "description": "Payment terms and schedule",
                    "content": "<p><strong>Total Compensation:</strong> <span class=\"placeholder\" data-field=\"total_compensation\">$0.00</span></p><p><strong>Payment Terms:</strong> <span class=\"placeholder\" data-field=\"payment_terms\">Net 30</span></p><p><strong>Payment Schedule:</strong></p><p><span class=\"placeholder\" data-field=\"payment_schedule\">Describe the payment schedule...</span></p>"
                },
                {
                    "id": "intellectual-property",
                    "title": "Intellectual Property",
                    "required": True,
                    "description": "Ownership of work products",
                    "content": "<p><span class=\"placeholder\" data-field=\"ip_terms\">Describe intellectual property terms...</span></p>"
                },
                {
                    "id": "confidentiality",
                    "title": "Confidentiality",
                    "required": True,
                    "description": "Protection of confidential information",
                    "content": "<p><span class=\"placeholder\" data-field=\"confidentiality_terms\">Describe confidentiality terms...</span></p>"
                },
                {
                    "id": "termination",
                    "title": "Termination",
                    "required": True,
                    "description": "Conditions for ending the contract",
                    "content": "<p><span class=\"placeholder\" data-field=\"termination_terms\">Describe termination terms...</span></p>"
                },
                {
                    "id": "liability",
                    "title": "Liability",
                    "required": True,
                    "description": "Limitation of liability provisions",
                    "content": "<p><span class=\"placeholder\" data-field=\"liability_terms\">Describe liability terms...</span></p>"
                }
            ]
        }
        
        # Insert templates
        mongo.db.templates.insert_many([proposal_template, sow_template, contract_template])
        
        # Create documents collection
        if 'documents' not in mongo.db.list_collection_names():
            mongo.db.create_collection('documents')

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

@app.route('/api/sections/<template_id>')
def get_sections(template_id):
    template = mongo.db.templates.find_one({"_id": ObjectId(template_id)})
    if not template:
        return jsonify({"error": "Template not found"}), 404
    
    return jsonify({"sections": template['sections']})

@app.route('/api/section/<template_id>/<section_id>')
def get_section(template_id, section_id):
    template = mongo.db.templates.find_one({"_id": ObjectId(template_id)})
    if not template:
        return jsonify({"error": "Template not found"}), 404
    
    section = next((s for s in template['sections'] if s['id'] == section_id), None)
    if not section:
        return jsonify({"error": "Section not found"}), 404
    
    return render_template('section.html', section=section)

@app.route('/preview', methods=['POST'])
def preview():
    data = request.form.to_dict(flat=False)
    template_id = data.get('template_id', [''])[0]
    included_sections = data.get('included_sections', [])
    
    # Convert multi-value dict to single-value for fields
    field_values = {}
    for key, value in data.items():
        if key not in ['template_id', 'included_sections']:
            field_values[key] = value[0]
    
    template = mongo.db.templates.find_one({"_id": ObjectId(template_id)})
    if not template:
        return "Template not found", 404
    
    # Filter sections based on user selection
    sections = [s for s in template['sections'] if s['id'] in included_sections or s.get('required', False)]
    
    # Replace placeholders with user values
    for section in sections:
        content = section['content']
        for field, value in field_values.items():
            placeholder = f'<span class="placeholder" data-field="{field}">'
            if placeholder in content:
                replacement = f'<span class="filled-value">'
                content = content.replace(placeholder, replacement)
                # Replace the placeholder text with the user's input
                pattern = f'<span class="placeholder" data-field="{field}">([^<]+)</span>'
                content = re.sub(pattern, f'<span class="filled-value">{value}</span>', content)
        section['content'] = content
    
    template['_id'] = str(template['_id'])
    return render_template('preview.html', template=template, sections=sections, field_values=field_values)

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    data = request.form.to_dict(flat=False)
    template_id = data.get('template_id', [''])[0]
    included_sections = data.get('included_sections', [])
    
    # Convert multi-value dict to single-value for fields
    field_values = {}
    for key, value in data.items():
        if key not in ['template_id', 'included_sections']:
            field_values[key] = value[0]
    
    template = mongo.db.templates.find_one({"_id": ObjectId(template_id)})
    if not template:
        return "Template not found", 404
    
    # Filter sections based on user selection
    sections = [s for s in template['sections'] if s['id'] in included_sections or s.get('required', False)]
    
    # Replace placeholders with user values
    for section in sections:
        content = section['content']
        for field, value in field_values.items():
            placeholder = f'<span class="placeholder" data-field="{field}">'
            if placeholder in content:
                replacement = f'<span class="filled-value">'
                content = content.replace(placeholder, replacement)
                # Replace the placeholder text with the user's input
                pattern = f'<span class="placeholder" data-field="{field}">([^<]+)</span>'
                content = re.sub(pattern, f'<span class="filled-value">{value}</span>', content)
        section['content'] = content
    
    # Generate HTML for PDF
    html_content = render_template('pdf_template.html', template=template, sections=sections)
    
    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()
    
    # Save document to database
    document = {
        "template_id": template_id,
        "template_name": template['name'],
        "sections": sections,
        "field_values": field_values,
        "created_at": datetime.now()
    }
    mongo.db.documents.insert_one(document)
    
    # Create response
    pdf_io = io.BytesIO(pdf)
    pdf_io.seek(0)
    
    filename = f"{template['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return send_file(
        pdf_io,
        mimetype='application/pdf',
        as_attachment=True,
        attachment_filename=filename
    )

@app.route('/documents')
def documents():
    docs = list(mongo.db.documents.find().sort("created_at", -1))
    for doc in docs:
        doc['_id'] = str(doc['_id'])
        doc['created_at_formatted'] = doc['created_at'].strftime('%B %d, %Y')
    
    return render_template('documents.html', documents=docs)

@app.route('/document/<document_id>')
def view_document(document_id):
    document = mongo.db.documents.find_one({"_id": ObjectId(document_id)})
    if not document:
        return "Document not found", 404
    
    document['_id'] = str(document['_id'])
    return render_template('view_document.html', document=document)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
