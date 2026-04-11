package com.lazypay.repository;

import com.lazypay.domain.transactions.IdempotencyKey;
import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface IdempotencyKeyRepository extends MongoRepository<IdempotencyKey, ObjectId> {
    Optional<IdempotencyKey> findByScopeAndKey(String scope, String key);
}


