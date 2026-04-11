package com.lazypay.repository;

import com.lazypay.domain.merchants.Merchant;
import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;

public interface MerchantRepository extends MongoRepository<Merchant, ObjectId> {
    Optional<Merchant> findByName(String name);
}


