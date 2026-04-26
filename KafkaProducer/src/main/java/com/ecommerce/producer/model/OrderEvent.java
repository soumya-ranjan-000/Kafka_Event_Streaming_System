package com.ecommerce.producer.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class OrderEvent {
    private String eventId;
    private String orderId;
    private String customerId;
    private String productId;
    private Integer quantity;
    private BigDecimal price;
    private String status;
    private LocalDateTime timestamp;
}
