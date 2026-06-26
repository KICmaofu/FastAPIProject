from datetime import datetime, timedelta
from typing import Any, Optional
from collections import OrderedDict

class CacheItem:
    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl  # 秒
    
    def is_expired(self) -> bool:
        return (datetime.now() - self.created_at).total_seconds() > self.ttl

class SimpleCache:
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        if item.is_expired():
            del self.cache[key]
            return None
        
        # 移动到末尾表示最近使用
        self.cache.move_to_end(key)
        return item.value
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        # 如果缓存已满，删除最久未使用的项
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[key] = CacheItem(value, ttl)
        self.cache.move_to_end(key)
    
    def delete(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        self.cache.clear()
    
    def size(self) -> int:
        return len(self.cache)

# 创建全局缓存实例
query_cache = SimpleCache(max_size=500)

def cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    parts = []
    for arg in args:
        parts.append(str(arg))
    for key, value in sorted(kwargs.items()):
        parts.append(f"{key}={value}")
    return ":".join(parts)