package com.lazypay.service;

import com.lazypay.domain.merchants.Merchant;
import com.lazypay.domain.transactions.*;
import com.lazypay.domain.users.User;
import com.lazypay.domain.users.UserBalance;
import com.lazypay.dto.PurchaseRequest;
import com.lazypay.exception.Exceptions.*;
import com.lazypay.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.time.temporal.ChronoUnit;

@Service
public class PurchaseService {
    private final TransactionRepository txRepo;
    private final UserRepository userRepo;
    private final UserBalanceRepository balRepo;
    private final MerchantRepository merchantRepo;
    private final IdempotencyKeyRepository idemRepo;

    public PurchaseService(TransactionRepository txRepo,
                           UserRepository userRepo,
                           UserBalanceRepository balRepo,
                           MerchantRepository merchantRepo,
                           IdempotencyKeyRepository idemRepo) {
        this.txRepo = txRepo;
        this.userRepo = userRepo;
        this.balRepo = balRepo;
        this.merchantRepo = merchantRepo;
        this.idemRepo = idemRepo;
    }

    @Transactional
    public Transaction purchase(PurchaseRequest req) {
        User user = userRepo.findById(req.userId()).orElseThrow(() -> new UserNotFound(req.userId()));
        UserBalance bal = balRepo.findByUserId(req.userId()).orElseThrow(() -> new RuntimeException("Balance not found"));
        Merchant merchant = merchantRepo.findById(req.merchantId()).orElseThrow(() -> new MerchantNotFound(req.merchantId()));

        double available = Math.max(0, user.getCreditLimit() - bal.getOutstandingAmount());
        if (req.amount() > available) throw new CreditLimitExceeded(req.userId(), req.amount(), available);

        if (req.idempotencyKey() != null) {
            idemRepo.findByScopeAndKey(req.userId().toHexString(), req.idempotencyKey())
                    .ifPresent(k -> { throw new DuplicateRequest(req.idempotencyKey()); });
            idemRepo.save(new IdempotencyKey(null, req.userId().toHexString(), req.idempotencyKey(), null, Instant.now(), Instant.now().plus(3, ChronoUnit.DAYS)));
        }

        double feePct = merchant.getCurrentFeePct();
        double fee = round(req.amount() * feePct / 100.0, 2);
        double payout = round(req.amount() - fee, 2);

        Transaction tx = new Transaction();
        tx.setType(TransactionType.PURCHASE);
        tx.setUserId(req.userId());
        tx.setMerchantId(req.merchantId());
        tx.setAmount(req.amount());
        tx.setCurrency(req.currency());
        tx.setStatus(TransactionStatus.APPROVED);
        tx.setAppliedFeePct(feePct);
        tx.setFeeAmount(fee);
        tx.setMerchantPayoutAmount(payout);
        tx.setBalanceBefore(bal.getOutstandingAmount());
        tx.setBalanceAfter(round(bal.getOutstandingAmount() + req.amount(), 2));
        tx.setIdempotencyKey(req.idempotencyKey());

        txRepo.save(tx);
        bal.setOutstandingAmount(bal.getOutstandingAmount() + req.amount());
        bal.setTotalPurchases(bal.getTotalPurchases() + req.amount());
        balRepo.save(bal); // version field enforces optimistic concurrency

        return tx;
    }

    private static double round(double value, int places) {
        return new BigDecimal(Double.toString(value)).setScale(places, RoundingMode.HALF_UP).doubleValue();
    }
}


