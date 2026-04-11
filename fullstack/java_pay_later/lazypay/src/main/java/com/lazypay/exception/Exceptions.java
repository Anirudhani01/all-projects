package com.lazypay.exception;

import org.bson.types.ObjectId;

public class Exceptions {
    public static class UserNotFound extends RuntimeException {
        public UserNotFound(ObjectId id) { super("User not found: " + id); }
    }
    public static class MerchantNotFound extends RuntimeException {
        public MerchantNotFound(ObjectId id) { super("Merchant not found: " + id); }
    }
    public static class DuplicateEntity extends RuntimeException {
        public DuplicateEntity(String msg) { super(msg); }
    }
    public static class CreditLimitExceeded extends RuntimeException {
        public CreditLimitExceeded(ObjectId userId, double amount, double available) {
            super("Credit limit exceeded for user=" + userId + " amount=" + amount + " available=" + available);
        }
    }
    public static class InvalidAmount extends RuntimeException {
        public InvalidAmount(double amount) { super("Invalid amount: " + amount); }
    }
    public static class DuplicateRequest extends RuntimeException {
        public DuplicateRequest(String key) { super("Duplicate request: " + key); }
    }
}


