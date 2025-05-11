# Tax Deduction Finder

A web application that processes PDF files to find and sum up tax deduction amounts using OCR (Optical Character Recognition). It looks for amounts near the text "Mont" in your PDF files.

## Features

- Modern web interface with drag-and-drop file upload
- Real-time PDF processing
- Detailed results showing amounts by page
- Support for French number formats
- Automatic file cleanup after processing

## Requirements

- Python 3.6 or higher
- Tesseract OCR engine
- Required Python packages (install using `pip install -r requirements.txt`):
  - pytesseract
  - pdf2image
  - Pillow
  - Flask
  - Werkzeug

## Installation

1. Install Tesseract OCR:
   - On macOS:
     ```bash
     brew install tesseract
     brew install tesseract-lang  # For additional languages
     ```
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install tesseract-ocr
     sudo apt-get install tesseract-ocr-fra  # For French language support
     ```
   - On Windows:
     Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the web server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Use the web interface to:
   - Drag and drop your PDF file
   - Or click to select a file
   - View the processing results
   - See amounts by page
   - Get the total amount

## Development

The application consists of:
- `app.py`: Flask web server and PDF processing logic
- `templates/index.html`: Web interface
- `uploads/`: Temporary storage for uploaded files (automatically cleaned)

## Output Format

The results will show:
- The name of the processed file
- The total amount found
- A breakdown of amounts by page number

All amounts are displayed in euros (€) with two decimal places. 