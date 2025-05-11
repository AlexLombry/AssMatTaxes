# Tax Deduction Finder

This Python application processes PDF files to find and sum up tax deduction amounts using OCR (Optical Character Recognition). It looks for amounts near the text "Mont" in your PDF files.

## Requirements

- Python 3.6 or higher
- Tesseract OCR engine
- Required Python packages (install using `pip install -r requirements.txt`):
  - pytesseract
  - pdf2image
  - Pillow

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

1. Place your PDF files in the same directory as the script
2. Run the script:
   ```bash
   python tax_deduction_finder.py
   ```

### Debug Mode

To enable debug mode, which shows detailed information about the processing:
```bash
python tax_deduction_finder.py --debug
# or
python tax_deduction_finder.py -v
```

Debug mode will show:
- Each page being processed
- Lines containing the keyword "Mont"
- Found amounts in matching lines
- Any conversion errors
- Number of amounts found per page

This is useful for verifying that the script is correctly identifying and processing the relevant lines in your PDFs.

The script will:
- Convert PDF pages to images
- Use OCR to extract text from the images
- Find amounts near the text "Mont"
- Display the amounts found on each page
- Show the total amount for each file
- Show the grand total across all files

## Output Format

The output will show:
- The name of each processed file
- The total amount found in each file
- A breakdown of amounts by page number
- A grand total across all processed files

All amounts are displayed in euros (€) with two decimal places. 