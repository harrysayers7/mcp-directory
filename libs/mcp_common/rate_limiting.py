"""
Rate limiting utilities for MCP servers.
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass
from collections import defaultdict, deque

from .exceptions import RateLimitError


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests: int
    window: int  # in seconds
    burst: Optional[int] = None  # burst allowance


class RateLimiter:
    """Rate limiter implementation."""
    
    def __init__(self, config: RateLimitConfig):
        """Initialize rate limiter."""
        self.config = config
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.burst_used: Dict[str, int] = defaultdict(int)
    
    def allow_request(self, key: str = "default") -> bool:
        """Check if a request is allowed."""
        now = time.time()
        window_start = now - self.config.window
        
        # Clean old requests
        requests = self.requests[key]
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Check if we're within the rate limit
        if len(requests) < self.config.requests:
            requests.append(now)
            return True
        
        # Check burst allowance
        if self.config.burst and self.burst_used[key] < self.config.burst:
            self.burst_used[key] += 1
            requests.append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, key: str = "default") -> int:
        """Get remaining requests in current window."""
        now = time.time()
        window_start = now - self.config.window
        
        # Clean old requests
        requests = self.requests[key]
        while requests and requests[0] < window_start:
            requests.popleft()
        
        remaining = self.config.requests - len(requests)
        if self.config.burst:
            remaining += max(0, self.config.burst - self.burst_used[key])
        
        return max(0, remaining)
    
    def get_reset_time(self, key: str = "default") -> float:
        """Get time when the rate limit resets."""
        if not self.requests[key]:
            return time.time()
        
        oldest_request = min(self.requests[key])
        return oldest_request + self.config.window
    
    def check_rate_limit(self, key: str = "default") -> None:
        """Check rate limit and raise exception if exceeded."""
        if not self.allow_request(key):
            reset_time = self.get_reset_time(key)
            retry_after = max(0, int(reset_time - time.time()))
            
            raise RateLimitError(
                f"Rate limit exceeded",
                limit=self.config.requests,
                window=self.config.window,
                retry_after=retry_after
            )
