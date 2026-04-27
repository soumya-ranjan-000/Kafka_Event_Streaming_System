package com.ecommerce.producer.controller;

import com.ecommerce.producer.model.OrderEvent;
import com.ecommerce.producer.model.OrderRequest;
import com.ecommerce.producer.model.OrderResponse;
import com.ecommerce.producer.service.OrderService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.UUID;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Orders", description = "Endpoints for managing e-commerce orders")
public class OrderController {

    private final OrderService orderService;

    @PostMapping
    @Operation(summary = "Create a new order", description = "Publishes an order event to Kafka for processing")
    public ResponseEntity<OrderResponse> createOrder(@Valid @RequestBody OrderRequest orderRequest) {
        log.info("Received order request: {}", orderRequest);
        
        // Generate a unique order ID
        String orderId = UUID.randomUUID().toString();
        String eventId = UUID.randomUUID().toString();
        
        // Map request to event
        OrderEvent orderEvent = OrderEvent.builder()
                .eventId(eventId)
                .orderId(orderId)
                .customerId(orderRequest.getCustomerId())
                .productId(orderRequest.getProductId())
                .quantity(orderRequest.getQuantity())
                .price(orderRequest.getPrice())
                .status("CREATED")
                .timestamp(LocalDateTime.now())
                .build();
                
        // Publish to Kafka
        orderService.publishOrderEvent(orderEvent);
        
        // Return response
        OrderResponse response = OrderResponse.builder()
                .orderId(orderId)
                .message("Order event published successfully")
                .status("SUCCESS")
                .build();
                
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}
