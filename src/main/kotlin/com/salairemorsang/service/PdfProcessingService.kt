package com.salairemorsang.service

import com.salairemorsang.model.PageAmount
import com.salairemorsang.model.ProcessResult
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withContext
import net.sourceforge.tess4j.Tesseract
import net.sourceforge.tess4j.TesseractException
import org.apache.pdfbox.Loader
import org.apache.pdfbox.pdmodel.PDDocument
import org.apache.pdfbox.rendering.PDFRenderer
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.web.multipart.MultipartFile
import java.awt.image.BufferedImage
import java.io.File
import java.math.BigDecimal
import java.util.regex.Pattern

@Service
class PdfProcessingService {
    private val logger = LoggerFactory.getLogger(PdfProcessingService::class.java)
    
    init {
        // Set library path for Tesseract
        val os = System.getProperty("os.name").lowercase()
        val isAppleSilicon = System.getProperty("os.arch").contains("aarch64")
        
        val libraryPath = when {
            os.contains("mac") && isAppleSilicon -> "/opt/homebrew/lib"
            os.contains("mac") -> "/usr/local/lib"
            os.contains("linux") -> "/usr/lib"
            os.contains("windows") -> "C:\\Program Files\\Tesseract-OCR"
            else -> throw IllegalStateException("Unsupported operating system: $os")
        }
        
        logger.info("Setting library path to: $libraryPath")
        System.setProperty("jna.library.path", libraryPath)
        System.setProperty("jna.platform.library.path", libraryPath)
    }
    
    private val tesseract: Tesseract by lazy {
        try {
            val isAppleSilicon = System.getProperty("os.arch").contains("aarch64")
            val tessdataPath = when {
                System.getProperty("os.name").lowercase().contains("mac") && isAppleSilicon -> "/opt/homebrew/share/tessdata"
                System.getProperty("os.name").lowercase().contains("mac") -> "/usr/local/share/tessdata"
                System.getProperty("os.name").lowercase().contains("linux") -> "/usr/share/tessdata"
                System.getProperty("os.name").lowercase().contains("windows") -> "C:\\Program Files\\Tesseract-OCR\\tessdata"
                else -> throw IllegalStateException("Unsupported operating system")
            }
            
            logger.info("Initializing Tesseract with tessdata path: $tessdataPath")
            
            Tesseract().apply {
                setDatapath(tessdataPath)
                setLanguage("fra")
                setPageSegMode(1) // Automatic page segmentation with OSD
                setOcrEngineMode(1) // Use LSTM OCR Engine
            }
        } catch (e: Exception) {
            logger.error("Failed to initialize Tesseract: ${e.message}")
            throw IllegalStateException("""
                Tesseract OCR is not properly installed. Please install it using:
                
                For macOS (Apple Silicon):
                brew install tesseract
                brew install tesseract-lang
                
                For macOS (Intel):
                brew install tesseract
                brew install tesseract-lang
                
                For Ubuntu/Debian:
                sudo apt-get install tesseract-ocr
                sudo apt-get install tesseract-ocr-fra
                
                For Windows:
                Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
                
                After installation, make sure the tessdata directory is in the correct location:
                - macOS (Apple Silicon): /opt/homebrew/share/tessdata
                - macOS (Intel): /usr/local/share/tessdata
                - Linux: /usr/share/tessdata
                - Windows: C:\Program Files\Tesseract-OCR\tessdata
                
                Also verify that the library path is correct:
                - macOS (Apple Silicon): /opt/homebrew/lib
                - macOS (Intel): /usr/local/lib
                - Linux: /usr/lib
                - Windows: C:\Program Files\Tesseract-OCR
                
                Current system properties:
                - os.name: ${System.getProperty("os.name")}
                - os.arch: ${System.getProperty("os.arch")}
                - jna.library.path: ${System.getProperty("jna.library.path")}
                - jna.platform.library.path: ${System.getProperty("jna.platform.library.path")}
            """.trimIndent(), e)
        }
    }

    private val amountPattern: Pattern = Pattern.compile("[0-9]+[ ,]*[0-9]*\\.[0-9]+")

    suspend fun processPdf(file: MultipartFile): ProcessResult = withContext(Dispatchers.IO) {
        val tempFile = File.createTempFile("upload", ".pdf")
        var document: PDDocument? = null
        
        try {
            file.transferTo(tempFile)
            logger.info("Processing PDF file: ${file.originalFilename}")
            
            // Load PDF with memory mapping disabled to avoid recursion issues
            document = Loader.loadPDF(tempFile, "org.apache.pdfbox.io.RandomAccessRead")
            val renderer = PDFRenderer(document)

            val amounts = coroutineScope {
                (0 until document.numberOfPages).map { pageNum ->
                    async {
                        try {
                            logger.debug("Processing page ${pageNum + 1}")
                            val image = renderer.renderImageWithDPI(pageNum, 300f)
                            processPage(pageNum, image)
                        } catch (e: Exception) {
                            logger.error("Error processing page ${pageNum + 1}: ${e.message}")
                            emptyList()
                        }
                    }
                }.map { it.await() }.flatten()
            }

            logger.info("Found ${amounts.size} amounts in the document")
            
            ProcessResult(
                fileName = file.originalFilename ?: "unknown",
                totalAmount = amounts.sumOf { it.amount },
                amountsFound = amounts
            )
        } catch (e: Exception) {
            logger.error("Error processing PDF: ${e.message}", e)
            throw e
        } finally {
            document?.close()
            tempFile.delete()
        }
    }

    private suspend fun processPage(pageNum: Int, image: BufferedImage): List<PageAmount> = withContext(Dispatchers.IO) {
        try {
            val text = tesseract.doOCR(image)
            val amounts = extractAmounts(text)
            logger.debug("Found ${amounts.size} amounts on page ${pageNum + 1}")
            amounts.map { amount ->
                PageAmount(pageNum + 1, amount)
            }
        } catch (e: TesseractException) {
            logger.error("Tesseract error processing page ${pageNum + 1}: ${e.message}")
            emptyList()
        } catch (e: Exception) {
            logger.error("Error processing page ${pageNum + 1}: ${e.message}")
            emptyList()
        }
    }

    private fun extractAmounts(text: String): List<Double> {
        return text.split("\n")
            .filter { it.contains("Mont") }
            .flatMap { line ->
                val matcher = amountPattern.matcher(line)
                val matches = mutableListOf<String>()
                while (matcher.find()) {
                    matches.add(matcher.group())
                }
                matches.map { amount ->
                    amount.replace(" ", "").replace(",", ".")
                }.mapNotNull { amount ->
                    try {
                        amount.toDouble()
                    } catch (e: NumberFormatException) {
                        logger.warn("Failed to parse amount: $amount")
                        null
                    }
                }
            }
    }
} 