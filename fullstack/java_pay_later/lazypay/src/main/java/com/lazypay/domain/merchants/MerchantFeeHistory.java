package com.lazypay.domain.merchants;

import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.CompoundIndex;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document("merchant_fee_history")
@CompoundIndex(name = "merchant_eff_desc", def = "{'merchantId': 1, 'effectiveFrom': -1}")
public class MerchantFeeHistory {
    @Id
    private ObjectId id;
    @Indexed
    private ObjectId merchantId;
    private double feePct;
    private Instant effectiveFrom;
    private String changedBy;
    private Instant createdAt = Instant.now();

    public ObjectId getId() { return id; }
    public void setId(ObjectId id) { this.id = id; }
    public ObjectId getMerchantId() { return merchantId; }
    public void setMerchantId(ObjectId merchantId) { this.merchantId = merchantId; }
    public double getFeePct() { return feePct; }
    public void setFeePct(double feePct) { this.feePct = feePct; }
    public Instant getEffectiveFrom() { return effectiveFrom; }
    public void setEffectiveFrom(Instant effectiveFrom) { this.effectiveFrom = effectiveFrom; }
    public String getChangedBy() { return changedBy; }
    public void setChangedBy(String changedBy) { this.changedBy = changedBy; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}


