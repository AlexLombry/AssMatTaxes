import os
from flask import Flask, render_template, request, jsonify, flash
from werkzeug.utils import secure_filename
import pytesseract
from pdf2image import convert_from_path
from decimal import Decimal
import re
import tempfile

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_amounts_from_text(text):
    amount_pattern = re.compile(r'[0-9]+[ ,]*[0-9]*\.[0-9]+')
    amounts = []
    
    lines = text.split('\n')
    for line in lines:
        if 'Mont' in line:
            matches = amount_pattern.findall(line)
            for match in matches:
                clean_value = match.replace(' ', '').replace(',', '.')
                try:
                    amount = Decimal(clean_value)
                    amounts.append(amount)
                except:
                    continue
    
    return amounts

def process_pdf(file_path):
    amounts_found = []
    
    try:
        # Convert PDF pages to images
        images = convert_from_path(file_path)
        
        for page_num, image in enumerate(images):
            # Extract text using OCR
            text = pytesseract.image_to_string(image, lang='fra')
            
            # Extract amounts from the text
            page_amounts = extract_amounts_from_text(text)
            for amount in page_amounts:
                amounts_found.append((page_num + 1, amount))
    
    except Exception as e:
        return None, str(e)
    
    total_amount = sum(amount for _, amount in amounts_found)
    
    return {
        'file_name': os.path.basename(file_path),
        'total_amount': float(total_amount),
        'amounts_found': [(page, float(amount)) for page, amount in amounts_found]
    }, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result, error = process_pdf(filepath)
        
        # Clean up the uploaded file
        os.remove(filepath)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify(result)
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True) 