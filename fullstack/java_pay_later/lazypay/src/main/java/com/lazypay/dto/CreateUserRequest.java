package com.lazypay.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.PositiveOrZero;

public record CreateUserRequest(@NotBlank String name, @Email String email, @PositiveOrZero double creditLimit) {}



