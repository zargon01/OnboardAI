import os
import json
import re
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
import pytesseract
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename
from bson import ObjectId

# Tesseract OCR Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Flask Application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MongoDB Configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/document_processing'
mongo = PyMongo(app)

# Regex Patterns
regex_patterns = {
    "Name": r"Name \(Block Letters- As specified on Passport or Pan Card\):\s*(.*?)\n",
    "Permanent Address": {
        "Street Address": r"2\. Permanent Address:\s*3\.1 Street Address:\s*(.*?)\n",
        "City": r"2\. Permanent Address:.*?3\.2 City:\s*(.*?)\s*3\.3",
        "State": r"2\. Permanent Address:.*?3\.3 State:\s*(.*?)\n",
        "Zip Code": r"2\. Permanent Address:.*?3\.4 Zip Code:\s*(\d+)\n",
        "Country": r"2\. Permanent Address:.*?3\.5 Country:\s*(.*?)\n"
    },
    "Current Address": {
        "Street Address": r"3\. Current Address:\s*3\.1 Street Address:\s*(.*?)\n",
        "City": r"3\. Current Address:.*?3\.2 City:\s*(.*?)\s*3\.3",
        "State": r"3\. Current Address:.*?3\.3 State:\s*(.*?)\n",
        "Zip Code": r"3\. Current Address:.*?3\.4 Zip Code:\s*(\d+)\n",
        "Country": r"3\. Current Address:.*?3\.5 Country:\s*(.*?)\n"
    },
    "Date of Birth": r"Date of Birth:\s*(\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{4})",
    "Age": r"Age:\s*(\d+)",
    "Gender": r"Gender:\s*(\w+)",
    "Mobile": r"Mobile:\s*(\d{10})",
    "Email ID": r"Email ID:\s*([\w.-]+@[\w.-]+)\b",
    "Emergency Contact": {
        "Name": r"Name of Emergency Contact:\s*(.*?)\n",
        "Number": r"Emergency Contact's Number:\s*(\d{10})"
    },
    "Available for Relocation": r"Available for Relocation:\s*(Yes|No|Y|N|y|n)?",
    "EDUCATIONAL QUALIFICATION": r"Sr No\\.\s*(\d+)\s*Name of the School/ University:\s*(.*?)\s*Qualification:\s*(.*?)\s*% or CGPA:\s*(\d+(\.\d+)?)\s*Pass out Year:\s*(\d{4})"
}

def process_document(file_path, regex_patterns):
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == ".pdf":
        images = convert_from_path(file_path)
        extracted_text = "\n".join([pytesseract.image_to_string(image, lang="eng") for image in images])
    elif file_ext in [".jpg", ".jpeg", ".png"]:
        extracted_text = pytesseract.image_to_string(file_path, lang="eng")
    else:
        raise ValueError("Unsupported file type. Please provide a PDF or image.")

    entities = {
        "Name": None,
        "Permanent Address": {
            "Street Address": None,
            "City": None,
            "State": None,
            "Zip Code": None,
            "Country": None
        },
        "Current Address": {
            "Street Address": None,
            "City": None,
            "State": None,
            "Zip Code": None,
            "Country": None
        },
        "Date of Birth": None,
        "Age": None,
        "Gender": None,
        "Mobile": None,
        "Email ID": None,
        "Emergency Contact": {
            "Name": None,
            "Number": None
        },
        "Available for Relocation": None,
        "Educational Qualification": []
    }

    for entity_name, pattern in regex_patterns.items():
        if isinstance(pattern, dict):  # Handle nested fields
            for sub_field, sub_pattern in pattern.items():
                match = re.search(sub_pattern, extracted_text, re.MULTILINE | re.DOTALL)
                if match:
                    entities[entity_name][sub_field] = match.group(1).strip() if match.group(1) else None
        else:
            match = re.search(pattern, extracted_text, re.DOTALL | re.MULTILINE)
            if match:
                entities[entity_name] = match.group(1).strip() if match.group(1) else None

    return entities

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'files' not in request.files:
            logger.error("No files part in the request")
            return jsonify({"error": "No files provided"}), 400

        uploaded_files = request.files.getlist('files')
        if not uploaded_files:
            logger.error("No files uploaded")
            return jsonify({"error": "No files uploaded"}), 400

        results = []
        for uploaded_file in uploaded_files:
            # Secure filename and get extension
            filename = secure_filename(uploaded_file.filename)
            file_ext = os.path.splitext(filename)[1].lower()

            # Validate file type
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            if file_ext not in allowed_extensions:
                logger.warning(f"Unsupported file type: {filename}")
                return jsonify({"error": f"Unsupported file type: {filename}"}), 400

            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            try:
                processed_data = process_document(file_path, regex_patterns)
                
                result = mongo.db.processed_files.insert_one(processed_data)
                processed_data["_id"] = str(result.inserted_id)
                results.append(processed_data)

                os.remove(file_path)

            except Exception as process_error:
                logger.error(f"Error processing file {filename}: {str(process_error)}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                return jsonify({
                    "error": f"Error processing file {filename}: {str(process_error)}"
                }), 500

        return jsonify({
            "message": f"Successfully processed {len(results)} file(s)",
            "results": results
        })

    except Exception as e:
        logger.error(f"Unexpected upload error: {str(e)}")
        return jsonify({"error": "Unexpected error during upload"}), 500


@app.route('/records', methods=['GET'])
def get_all_records():
    records = list(mongo.db.processed_files.find())
    for record in records:
        record["_id"] = str(record["_id"])
    return jsonify({"records": records})

@app.route('/search', methods=['GET'])
def search_records():
    name = request.args.get('name', '')
    email = request.args.get('email', '')

    query = {}
    if name:
        query["Name"] = {"$regex": name, "$options": "i"}
    if email:
        query["Email ID"] = {"$regex": email, "$options": "i"}

    records = list(mongo.db.processed_files.find(query))
    for record in records:
        record["_id"] = str(record["_id"])

    return jsonify({"records": records})


@app.route('/records/<record_id>', methods=['GET'])
def get_record_details(record_id):
    record = mongo.db.processed_files.find_one({"_id": ObjectId(record_id)})
    if not record:
        return jsonify({"error": "Record not found"}), 404
    record["_id"] = str(record["_id"])
    return jsonify(record)

if __name__ == '__main__':
    app.run(debug=True)
