package com.ecommerce.producer.service;

import com.ecommerce.producer.model.OrderEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Service;

import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    @Value("${app.kafka.order.topic:orders-topic}")
    private String orderTopic;

    public void publishOrderEvent(OrderEvent orderEvent) {
        log.info("Attempting to publish order event to topic {}: {}", orderTopic, orderEvent);
        
        CompletableFuture<SendResult<String, OrderEvent>> future = kafkaTemplate.send(orderTopic, orderEvent.getOrderId(), orderEvent);
        
        future.whenComplete((result, ex) -> {
            if (ex == null) {
                log.info("Successfully sent order event=[{}] with offset=[{}]", orderEvent.getOrderId(), result.getRecordMetadata().offset());
            } else {
                log.error("Unable to send order event=[{}] due to : {}", orderEvent.getOrderId(), ex.getMessage());
            }
        });
    }
}
