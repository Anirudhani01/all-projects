
package com.lazypay.api;

import com.lazypay.domain.merchants.Merchant;
import com.lazypay.repository.MerchantRepository;
import jakarta.validation.Valid;
import org.bson.types.ObjectId;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/merchants")
public class MerchantsController {
    private final MerchantRepository merchantRepository;

    public MerchantsController(MerchantRepository merchantRepository) {
        this.merchantRepository = merchantRepository;
    }

    @PostMapping
    public ResponseEntity<Merchant> create(@Valid @RequestBody Merchant req) {
        Merchant saved = merchantRepository.save(req);
        return ResponseEntity.ok(saved);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Merchant> get(@PathVariable("id") ObjectId id) {
        return merchantRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}


