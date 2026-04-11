package com.lazypay.dto;

import com.lazypay.domain.transactions.Currency;
import jakarta.validation.constraints.Positive;
import org.bson.types.ObjectId;

public record PurchaseRequest(ObjectId userId, ObjectId merchantId, @Positive double amount, Currency currency, String idempotencyKey) {}



