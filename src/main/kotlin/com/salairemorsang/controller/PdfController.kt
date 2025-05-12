package com.salairemorsang.controller

import com.salairemorsang.model.ErrorResponse
import com.salairemorsang.model.ProcessResult
import com.salairemorsang.service.PdfProcessingService
import org.springframework.http.ResponseEntity
import org.springframework.stereotype.Controller
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.ResponseBody
import org.springframework.web.multipart.MultipartFile

@Controller
class PdfController(private val pdfProcessingService: PdfProcessingService) {

    @GetMapping("/")
    fun index(): String = "index"

    @PostMapping("/upload")
    @ResponseBody
    suspend fun uploadFile(@RequestParam("file") file: MultipartFile): ResponseEntity<Any> {
        if (file.isEmpty) {
            return ResponseEntity.badRequest().body(ErrorResponse("No file uploaded"))
        }

        file.originalFilename?.endsWith(".pdf", ignoreCase = true)?.let {
            if (!it) {
                return ResponseEntity.badRequest().body(ErrorResponse("Only PDF files are allowed"))
            }
        }

        return try {
            val result = pdfProcessingService.processPdf(file)
            ResponseEntity.ok(result)
        } catch (e: Exception) {
            ResponseEntity.internalServerError().body(ErrorResponse("Error processing file: ${e.message}"))
        }
    }
} 