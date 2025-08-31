package com.github.firulapp.core.dto;

import lombok.Data;

@Data
public class LoginResponseDto {
    private Long id;
    private String username;
    private String name;
    private String surname;
    private String email;
    private String token;
}
