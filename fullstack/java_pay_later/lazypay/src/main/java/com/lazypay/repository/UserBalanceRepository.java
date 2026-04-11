package com.lazypay.repository;

import com.lazypay.domain.users.UserBalance;
import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface UserBalanceRepository extends MongoRepository<UserBalance, ObjectId> {
    Optional<UserBalance> findByUserId(ObjectId userId);
}


