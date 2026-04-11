package com.lazypay.dto;

import com.lazypay.domain.users.UserStatus;
import jakarta.validation.constraints.PositiveOrZero;

public record UpdateUserRequest(String name, @PositiveOrZero Double creditLimit, UserStatus status) {}



