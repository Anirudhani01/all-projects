package com.lazypay.domain.transactions;

import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.CompoundIndex;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document("idempotency_keys")
@CompoundIndex(name = "scope_key", def = "{'scope': 1, 'key': 1}", unique = true)
public class IdempotencyKey {
    @Id
    private ObjectId id;
    private String scope; // userId or global
    private String key;
    private String responseHash;
    private Instant createdAt = Instant.now();
    @Indexed(expireAfterSeconds = 259200)
    private Instant ttlExpiresAt; // alternative TTL

    public IdempotencyKey() {}

    public IdempotencyKey(ObjectId id, String scope, String key, String responseHash, Instant createdAt, Instant ttlExpiresAt) {
        this.id = id; this.scope = scope; this.key = key; this.responseHash = responseHash; this.createdAt = createdAt; this.ttlExpiresAt = ttlExpiresAt;
    }

    public ObjectId getId() { return id; }
    public void setId(ObjectId id) { this.id = id; }
    public String getScope() { return scope; }
    public void setScope(String scope) { this.scope = scope; }
    public String getKey() { return key; }
    public void setKey(String key) { this.key = key; }
    public String getResponseHash() { return responseHash; }
    public void setResponseHash(String responseHash) { this.responseHash = responseHash; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
    public Instant getTtlExpiresAt() { return ttlExpiresAt; }
    public void setTtlExpiresAt(Instant ttlExpiresAt) { this.ttlExpiresAt = ttlExpiresAt; }
}


