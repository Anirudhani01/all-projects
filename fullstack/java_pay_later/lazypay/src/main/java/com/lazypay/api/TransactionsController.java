package com.lazypay.api;

import com.lazypay.domain.transactions.Transaction;
import com.lazypay.dto.PaymentRequest;
import com.lazypay.dto.PurchaseRequest;
import com.lazypay.service.PaymentService;
import com.lazypay.service.PurchaseService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/transactions")
public class TransactionsController {
    private final PurchaseService purchaseService;
    private final PaymentService paymentService;

    public TransactionsController(PurchaseService purchaseService, PaymentService paymentService) {
        this.purchaseService = purchaseService;
        this.paymentService = paymentService;
    }

    @PostMapping("/purchase")
    public Transaction purchase(@Valid @RequestBody PurchaseRequest req) {
        return purchaseService.purchase(req);
    }

    @PostMapping("/payment")
    public Transaction payment(@Valid @RequestBody PaymentRequest req) {
        return paymentService.payment(req);
    }
}


