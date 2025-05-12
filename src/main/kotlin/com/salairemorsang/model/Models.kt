package com.salairemorsang.model

data class ProcessResult(
    val fileName: String,
    val totalAmount: Double,
    val amountsFound: List<PageAmount>
)

data class PageAmount(
    val page: Int,
    val amount: Double
)

data class ErrorResponse(
    val error: String
) 