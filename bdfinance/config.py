"""Configuration classes for bdfinance package."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientConfig(BaseSettings):
    """Configuration for BDFinance HTTP client"""

    model_config = SettingsConfigDict(env_prefix="BDFINANCE_")

    # Connection settings
    max_connections: int = Field(default=100, description="Maximum number of connections")
    max_keepalive_connections: int = Field(default=20, description="Maximum keepalive connections")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")

    # Retry settings
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_backoff_factor: float = Field(default=1.0, description="Exponential backoff factor")
    retry_min_wait: float = Field(default=1.0, description="Minimum wait between retries")
    retry_max_wait: float = Field(default=10.0, description="Maximum wait between retries")

    # Rate limiting
    rate_limit: int = Field(default=10, description="Maximum requests per second")

    # Cache
    enable_cache: bool = Field(default=True, description="Enable response caching")

    # URLs
    dse_url: str = Field(default="https://dsebd.org/", description="DSE primary URL")
    dse_alt_url: str = Field(default="https://dsebd.com.bd/", description="DSE alternate URL")


class CacheConfig(BaseSettings):
    """Configuration for caching layer"""

    model_config = SettingsConfigDict(env_prefix="BDFINANCE_CACHE_")

    backend: Literal["memory", "redis"] = Field(default="memory", description="Cache backend type")
    ttl: int = Field(default=300, description="Cache TTL in seconds (5 minutes default)")
    max_size: int = Field(default=1000, description="Maximum cache size for memory backend")

    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_encoding: str = Field(default="utf-8", description="Redis encoding")
