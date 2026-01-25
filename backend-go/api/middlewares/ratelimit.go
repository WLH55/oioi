package middlewares

import (
	"sync"
	"time"

	"github.com/drama-generator/backend/pkg/response"
	"github.com/gin-gonic/gin"
)

type rateLimiter struct {
	mu       sync.Mutex
	requests map[string][]time.Time
	limit    int
	window   time.Duration
}

var limiter = &rateLimiter{
	requests: make(map[string][]time.Time),
	limit:    2000, // 每分钟最多 2000 次请求
	window:   time.Minute,
}

func RateLimitMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		ip := c.ClientIP()

		limiter.mu.Lock()
		defer limiter.mu.Unlock()

		now := time.Now()
		requests := limiter.requests[ip]

		var validRequests []time.Time
		for _, t := range requests {
			if now.Sub(t) < limiter.window {
				validRequests = append(validRequests, t)
			}
		}

		if len(validRequests) >= limiter.limit {
			response.Error(c, 429, "RATE_LIMIT_EXCEEDED", "请求过于频繁，请稍后再试")
			c.Abort()
			return
		}

		validRequests = append(validRequests, now)
		limiter.requests[ip] = validRequests

		c.Next()
	}
}
