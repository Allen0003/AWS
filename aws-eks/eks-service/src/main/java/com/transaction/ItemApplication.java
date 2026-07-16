package com.transaction;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
@EnableJpaRepositories(basePackages = "com.transaction.domain.repository")
@EntityScan(basePackages = "com.transaction.domain.entity")
public class ItemApplication {

    public static void main(String[] args) {

        SpringApplication.run(ItemApplication.class, args);
    }





}

