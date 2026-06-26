from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import time

class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.clients = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - self.time_window
        
        # 清理过期的请求记录
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if timestamp >= window_start
        ]
        
        # 检查请求数量
        if len(self.clients[client_ip]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.clients[client_ip].append(now)
        return True
    
    def get_remaining(self, client_ip: str) -> int:
        now = time.time()
        window_start = now - self.time_window
        
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if timestamp >= window_start
        ]
        
        return self.max_requests - len(self.clients[client_ip])

# 创建全局限流实例
rate_limiter = RateLimiter()