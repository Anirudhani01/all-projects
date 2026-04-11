package com.lazypay.domain.merchants;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document("merchants")
public class Merchant {
    @Id
    private ObjectId id;
    @Indexed(unique = true)
    @NotBlank
    private String name;
    @DecimalMin("0.0")
    @DecimalMax("100.0")
    private double currentFeePct;
    private Instant createdAt = Instant.now();
    private Instant updatedAt = Instant.now();

    public ObjectId getId() { return id; }
    public void setId(ObjectId id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public double getCurrentFeePct() { return currentFeePct; }
    public void setCurrentFeePct(double currentFeePct) { this.currentFeePct = currentFeePct; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
}


