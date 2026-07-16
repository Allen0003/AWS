package com.transaction.controller;


import com.transaction.entity.Item;
import com.transaction.repository.ItemRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/api/data")

public class ItemController {
    @Autowired
    private ItemRepository itemRepository;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    private static final String REDIS_PREFIX = "item:";

    // 1. 寫入：同時寫入 DB 與 Redis
    @PostMapping
    public Item createItem(@RequestBody Item item) {

        Item savedItem = itemRepository.save(item);

        // 寫入 Redis (設定 10 分鐘過期)
        redisTemplate.opsForValue().set(REDIS_PREFIX + item.getId(), savedItem, 10, TimeUnit.MINUTES);

        System.out.println("成功寫入 DB 與 Redis: " + item.getId());
        return savedItem;
    }

    // 2. 讀取：先讀 Redis，沒有再讀 DB
    @GetMapping("/{id}")
    public Item getItem(@PathVariable String id) {
        String redisKey = REDIS_PREFIX + id;

        // Step 1: 嘗試從 Redis 讀取
        Item cachedItem = (Item) redisTemplate.opsForValue().get(redisKey);
        if (cachedItem != null) {
            System.out.println("=== Redis Cache Hit! 成功從快取取得 ===");
            return cachedItem;
        }

        System.out.println("=== Redis Cache Miss! 從 PostgreSQL 資料庫讀取 ===");

        // Step 2: Redis 沒中，從 PostgreSQL 讀取
        Item dbItem = itemRepository.findById(id).orElseThrow(
                () -> new RuntimeException("找不到該資料: " + id)
        );

        // Step 3: 回填至 Redis 供下次使用
        redisTemplate.opsForValue().set(redisKey, dbItem, 10, TimeUnit.MINUTES);

        return dbItem;
    }
}
