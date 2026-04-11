package com.lazypay.domain.users;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.CompoundIndex;
import org.springframework.data.mongodb.core.index.CompoundIndexes;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document("users")
@CompoundIndexes({ @CompoundIndex(name = "status_idx", def = "{'status': 1}") })
public class User {
    @Id
    private ObjectId id;
    @NotBlank
    private String name;
    @Email
    @Indexed(unique = true)
    private String email;
    @PositiveOrZero
    private double creditLimit;
    @NotNull
    private UserStatus status = UserStatus.ACTIVE;
    private Instant createdAt = Instant.now();
    private Instant updatedAt = Instant.now();

    public ObjectId getId() { return id; }
    public void setId(ObjectId id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public double getCreditLimit() { return creditLimit; }
    public void setCreditLimit(double creditLimit) { this.creditLimit = creditLimit; }
    public UserStatus getStatus() { return status; }
    public void setStatus(UserStatus status) { this.status = status; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
}


