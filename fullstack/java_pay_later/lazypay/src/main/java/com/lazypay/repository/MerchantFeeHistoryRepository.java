package com.lazypay.repository;

import com.lazypay.domain.merchants.MerchantFeeHistory;
import org.bson.types.ObjectId;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface MerchantFeeHistoryRepository extends MongoRepository<MerchantFeeHistory, ObjectId> {
    List<MerchantFeeHistory> findByMerchantIdOrderByEffectiveFromDesc(ObjectId merchantId);
}


