package com.lazypay.repository;

import com.lazypay.domain.transactions.Transaction;
import org.bson.types.ObjectId;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface TransactionRepository extends MongoRepository<Transaction, ObjectId> {
    Page<Transaction> findByUserId(ObjectId userId, Pageable pageable);
}


