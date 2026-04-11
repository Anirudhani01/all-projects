package com.lazypay.domain.users;

import jakarta.validation.constraints.PositiveOrZero;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.Version;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document("user_balances")
public class UserBalance {
    @Id
    private ObjectId id;
    @Indexed(unique = true)
    private ObjectId userId;
    @PositiveOrZero
    private double outstandingAmount = 0.0;
    private double totalPurchases = 0.0;
    private double totalPayments = 0.0;
    @Version
    private Long version; // optimistic concurrency
    private Instant updatedAt = Instant.now();

    public ObjectId getId() { return id; }
    public void setId(ObjectId id) { this.id = id; }
    public ObjectId getUserId() { return userId; }
    public void setUserId(ObjectId userId) { this.userId = userId; }
    public double getOutstandingAmount() { return outstandingAmount; }
    public void setOutstandingAmount(double outstandingAmount) { this.outstandingAmount = outstandingAmount; }
    public double getTotalPurchases() { return totalPurchases; }
    public void setTotalPurchases(double totalPurchases) { this.totalPurchases = totalPurchases; }
    public double getTotalPayments() { return totalPayments; }
    public void setTotalPayments(double totalPayments) { this.totalPayments = totalPayments; }
    public Long getVersion() { return version; }
    public void setVersion(Long version) { this.version = version; }
    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
}


