# Tax Deduction Calculator

A Spring Boot application to extract and calculate tax deduction amounts from PDF documents.

## Prerequisites

- Java 17 or higher
- Gradle 8.x or higher
- Tesseract OCR

### Tesseract OCR Installation

#### macOS (Apple Silicon)
```bash
brew install tesseract
brew install tesseract-lang
```

#### macOS (Intel)
```bash
brew install tesseract
brew install tesseract-lang
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-fra
```

#### Windows
1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install with French language data included

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/salaire-morsang.git
cd salaire-morsang
```

2. Build the application:
```bash
./gradlew build
```

## Configuration

The application uses the following default settings:
- Port: 8080
- Maximum file size: 20MB

To modify these settings, edit the `src/main/resources/application.yml` file.

## Running the Application

To start the application:
```bash
./gradlew bootRun
```

The application will be available at: http://localhost:8080

## Usage

1. Open your browser and navigate to http://localhost:8080
2. Drag and drop your PDF file or click "Choose File"
3. The application will:
   - Extract text from the PDF
   - Search for deduction amounts
   - Display the total and breakdown by page

## Features

- Modern and responsive web interface
- Asynchronous file processing
- Text extraction with Tesseract OCR
- Multilingual support (French)
- Real-time results display
- Error handling and file validation

## Project Structure

```
src/
├── main/
│   ├── kotlin/
│   │   └── com/
│   │       └── salairemorsang/
│   │           ├── controller/
│   │           │   └── PdfController.kt
│   │           ├── model/
│   │           │   └── Models.kt
│   │           ├── service/
│   │           │   └── PdfProcessingService.kt
│   │           └── SalaireMorsangApplication.kt
│   └── resources/
│       ├── static/
│       ├── templates/
│       │   └── index.html
│       └── application.yml
└── test/
    └── kotlin/
        └── com/
            └── salairemorsang/
                └── SalaireMorsangApplicationTests.kt
```

## Technologies Used

- Spring Boot 3.2.3
- Kotlin 1.9.22
- PDFBox 3.0.1
- Tesseract OCR 5.8.0
- Thymeleaf
- Bootstrap 5.3.2
- Coroutines

## Development

### Development Prerequisites

- IntelliJ IDEA (recommended) or VS Code
- Kotlin Plugin
- Spring Boot Plugin

### Testing

To run the tests:
```bash
./gradlew test
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing

Contributions are welcome! Please feel free to:
1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Support

If you encounter any issues or have questions, please:
1. Check the [issues](https://github.com/your-username/salaire-morsang/issues)
2. Create a new issue if needed 