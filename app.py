import os
from flask import Flask, render_template, request, jsonify, flash
from werkzeug.utils import secure_filename
import pytesseract
from pdf2image import convert_from_path
from decimal import Decimal
import re
import tempfile
from multiprocessing import Pool, cpu_count
from functools import partial

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

def process_page(args):
    page_num, image = args
    try:
        # Extract text using OCR
        text = pytesseract.image_to_string(image, lang='fra')
        
        # Extract amounts from the text
        amounts = extract_amounts_from_text(text)
        return [(page_num + 1, amount) for amount in amounts]
    except Exception as e:
        print(f"Error processing page {page_num + 1}: {str(e)}")
        return []

def process_pdf(file_path):
    try:
        # Convert PDF pages to images
        images = convert_from_path(file_path)
        
        # Create a pool of workers
        num_workers = max(1, cpu_count() - 1)  # Leave one CPU free
        with Pool(processes=num_workers) as pool:
            # Process pages in parallel
            results = pool.map(process_page, enumerate(images))
        
        # Flatten results
        amounts_found = [item for sublist in results for item in sublist]
        
        total_amount = sum(amount for _, amount in amounts_found)
        
        return {
            'file_name': os.path.basename(file_path),
            'total_amount': float(total_amount),
            'amounts_found': [(page, float(amount)) for page, amount in amounts_found]
        }, None
    
    except Exception as e:
        return None, str(e)

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