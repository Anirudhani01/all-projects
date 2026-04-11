package com.lazypay.api;

import com.lazypay.domain.users.User;
import com.lazypay.domain.users.UserBalance;
import com.lazypay.dto.CreateUserRequest;
import com.lazypay.repository.UserBalanceRepository;
import com.lazypay.repository.UserRepository;
import jakarta.validation.Valid;
import org.bson.types.ObjectId;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/users")
public class UsersController {
    private final UserRepository userRepository;
    private final UserBalanceRepository balanceRepository;

    public UsersController(UserRepository userRepository, UserBalanceRepository balanceRepository) {
        this.userRepository = userRepository;
        this.balanceRepository = balanceRepository;
    }

    @PostMapping
    public ResponseEntity<User> create(@Valid @RequestBody CreateUserRequest req) {
        User user = new User();
        user.setName(req.name());
        user.setEmail(req.email());
        user.setCreditLimit(req.creditLimit());
        User saved = userRepository.save(user);

        UserBalance bal = new UserBalance();
        bal.setUserId(saved.getId());
        balanceRepository.save(bal);

        return ResponseEntity.ok(saved);
    }

    @GetMapping("/{id}")
    public ResponseEntity<User> get(@PathVariable("id") ObjectId id) {
        return userRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}


