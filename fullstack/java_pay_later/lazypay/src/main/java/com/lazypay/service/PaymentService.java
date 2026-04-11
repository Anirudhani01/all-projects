package com.lazypay.service;

import com.lazypay.domain.transactions.IdempotencyKey;
import com.lazypay.domain.transactions.Transaction;
import com.lazypay.domain.transactions.TransactionStatus;
import com.lazypay.domain.transactions.TransactionType;
import com.lazypay.domain.users.UserBalance;
import com.lazypay.dto.PaymentRequest;
import com.lazypay.exception.Exceptions.DuplicateRequest;
import com.lazypay.exception.Exceptions.InvalidAmount;
import com.lazypay.repository.IdempotencyKeyRepository;
import com.lazypay.repository.TransactionRepository;
import com.lazypay.repository.UserBalanceRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.temporal.ChronoUnit;

@Service
public class PaymentService {
    private final TransactionRepository txRepo;
    private final UserBalanceRepository balRepo;
    private final IdempotencyKeyRepository idemRepo;

    public PaymentService(TransactionRepository txRepo, UserBalanceRepository balRepo, IdempotencyKeyRepository idemRepo) {
        this.txRepo = txRepo;
        this.balRepo = balRepo;
        this.idemRepo = idemRepo;
    }

    @Transactional
    public Transaction payment(PaymentRequest req) {
        if (req.amount() <= 0) throw new InvalidAmount(req.amount());

        UserBalance bal = balRepo.findByUserId(req.userId()).orElseThrow(() -> new RuntimeException("Balance not found"));

        if (req.idempotencyKey() != null) {
            idemRepo.findByScopeAndKey(req.userId().toHexString(), req.idempotencyKey())
                    .ifPresent(k -> { throw new DuplicateRequest(req.idempotencyKey()); });
            idemRepo.save(new IdempotencyKey(null, req.userId().toHexString(), req.idempotencyKey(), null, Instant.now(), Instant.now().plus(3, ChronoUnit.DAYS)));
        }

        Transaction tx = new Transaction();
        tx.setType(TransactionType.PAYMENT);
        tx.setUserId(req.userId());
        tx.setAmount(req.amount());
        tx.setCurrency(req.currency());
        tx.setStatus(TransactionStatus.APPROVED);
        tx.setBalanceBefore(bal.getOutstandingAmount());
        double newOutstanding = Math.max(0, bal.getOutstandingAmount() - req.amount());
        tx.setBalanceAfter(newOutstanding);
        tx.setIdempotencyKey(req.idempotencyKey());

        txRepo.save(tx);
        bal.setOutstandingAmount(newOutstanding);
        bal.setTotalPayments(bal.getTotalPayments() + req.amount());
        balRepo.save(bal);

        return tx;
    }
}


