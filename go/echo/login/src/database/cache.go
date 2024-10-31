package database

import (
	"context"
	"log"
	"time"

	"github.com/go-redis/cache/v8"
	"github.com/go-redis/redis/v8"
)

type Cache struct {
	cache              *cache.Cache
	refreshTokenExpire int
}

func NewCache(redisServer string, refreshTokenExpire int) *Cache {
	tokenCache := cache.New(&cache.Options{
		Redis:      redis.NewClient(&redis.Options{Addr: redisServer}),
		LocalCache: cache.NewTinyLFU(1000, (time.Duration)(refreshTokenExpire)*time.Minute),
	})
	return &Cache{cache: tokenCache, refreshTokenExpire: refreshTokenExpire}
}

func (c *Cache) Set(key string, value interface{}) {
	item := cache.Item{
		Ctx:   context.TODO(),
		Key:   key,
		Value: value,
		TTL:   (time.Duration)(c.refreshTokenExpire) * time.Minute,
	}
	if err := c.cache.Set(&item); err != nil {
		log.Panicf("failed to set a refresh token in Cache server: %v", err)
	}
}
func (c *Cache) Get(key string) (string, bool) {
	ctx := context.TODO()
	var value string
	if err := c.cache.Get(ctx, key, &value); err != nil {
		log.Printf("failed to get a refresh token from Cache server: %v", err)
		return value, false
	}
	return value, true
}

func (c *Cache) Delete(key string) {
	if err := c.cache.Delete(context.TODO(), key); err != nil {
		log.Printf("failed to delete a refresh token from Cache server: %v", err)
	}
}
