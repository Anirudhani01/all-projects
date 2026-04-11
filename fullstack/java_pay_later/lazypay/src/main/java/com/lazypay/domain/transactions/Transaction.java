package com.lazypay.domain.transactions;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.CompoundIndex;
import org.springframework.data.mongodb.core.index.CompoundIndexes;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.Map;

@Document("transactions")
@CompoundIndexes({
        @CompoundIndex(name = "user_created", def = "{'userId': 1, 'createdAt': -1}"),
        @CompoundIndex(name = "merchant_created", def = "{'merchantId': 1, 'createdAt': -1}"),
        @CompoundIndex(name = "type_created", def = "{'type': 1, 'createdAt': -1}"),
        @CompoundIndex(name = "user_idem", def = "{'userId': 1, 'idempotencyKey': 1}", unique = true, sparse = true)
})
public class Transaction {
    @Id
    private ObjectId id;
    @NotNull
    private TransactionType type;
    @Indexed
    @NotNull
    private ObjectId userId;
    private ObjectId merchantId; // nullable for PAYMENT
    @Positive
    private double amount;
    @NotNull
    private Currency currency = Currency.INR;
    @NotNull
    private TransactionStatus status;
    private Double appliedFeePct; // PURCHASE
    private Double feeAmount;     // PURCHASE
    private Double merchantPayoutAmount; // PURCHASE
    private Double balanceBefore;
    private Double balanceAfter;
    private String idempotencyKey;
    private String reason;
    private Instant createdAt = Instant.now();
    private Map<String, Object> metadata;

    public ObjectId getId() { return id; }
    public void setId(ObjectId id) { this.id = id; }
    public TransactionType getType() { return type; }
    public void setType(TransactionType type) { this.type = type; }
    public ObjectId getUserId() { return userId; }
    public void setUserId(ObjectId userId) { this.userId = userId; }
    public ObjectId getMerchantId() { return merchantId; }
    public void setMerchantId(ObjectId merchantId) { this.merchantId = merchantId; }
    public double getAmount() { return amount; }
    public void setAmount(double amount) { this.amount = amount; }
    public Currency getCurrency() { return currency; }
    public void setCurrency(Currency currency) { this.currency = currency; }
    public TransactionStatus getStatus() { return status; }
    public void setStatus(TransactionStatus status) { this.status = status; }
    public Double getAppliedFeePct() { return appliedFeePct; }
    public void setAppliedFeePct(Double appliedFeePct) { this.appliedFeePct = appliedFeePct; }
    public Double getFeeAmount() { return feeAmount; }
    public void setFeeAmount(Double feeAmount) { this.feeAmount = feeAmount; }
    public Double getMerchantPayoutAmount() { return merchantPayoutAmount; }
    public void setMerchantPayoutAmount(Double merchantPayoutAmount) { this.merchantPayoutAmount = merchantPayoutAmount; }
    public Double getBalanceBefore() { return balanceBefore; }
    public void setBalanceBefore(Double balanceBefore) { this.balanceBefore = balanceBefore; }
    public Double getBalanceAfter() { return balanceAfter; }
    public void setBalanceAfter(Double balanceAfter) { this.balanceAfter = balanceAfter; }
    public String getIdempotencyKey() { return idempotencyKey; }
    public void setIdempotencyKey(String idempotencyKey) { this.idempotencyKey = idempotencyKey; }
    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
    public Map<String, Object> getMetadata() { return metadata; }
    public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
}


