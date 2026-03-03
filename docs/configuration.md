# Configuration

> Back to [README](../README.md)

---

bdfinance uses [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration. Settings can be passed as constructor arguments or loaded from environment variables.

---

## ClientConfig

Controls HTTP client behaviour, retries, rate limiting, and proxy settings.

**Environment variable prefix:** `BDFINANCE_`

```python
from bdfinance import ClientConfig

config = ClientConfig(
    timeout=60.0,
    max_retries=5,
    rate_limit=20,
    enable_cache=True,
    proxy_url="http://proxy:8080",
)
```

### All Options

| Field | Env Variable | Type | Default | Description |
|-------|-------------|------|---------|-------------|
| `max_connections` | `BDFINANCE_MAX_CONNECTIONS` | `int` | `100` | Maximum number of HTTP connections |
| `max_keepalive_connections` | `BDFINANCE_MAX_KEEPALIVE_CONNECTIONS` | `int` | `20` | Maximum keepalive connections |
| `timeout` | `BDFINANCE_TIMEOUT` | `float` | `30.0` | Request timeout in seconds |
| `max_retries` | `BDFINANCE_MAX_RETRIES` | `int` | `3` | Maximum retry attempts |
| `retry_backoff_factor` | `BDFINANCE_RETRY_BACKOFF_FACTOR` | `float` | `1.0` | Exponential backoff multiplier |
| `retry_min_wait` | `BDFINANCE_RETRY_MIN_WAIT` | `float` | `1.0` | Minimum wait between retries (seconds) |
| `retry_max_wait` | `BDFINANCE_RETRY_MAX_WAIT` | `float` | `10.0` | Maximum wait between retries (seconds) |
| `rate_limit` | `BDFINANCE_RATE_LIMIT` | `int` | `10` | Maximum concurrent requests (semaphore) |
| `enable_cache` | `BDFINANCE_ENABLE_CACHE` | `bool` | `True` | Enable response caching |
| `proxy_url` | `BDFINANCE_PROXY_URL` | `str \| None` | `None` | HTTP proxy URL |
| `proxy_username` | `BDFINANCE_PROXY_USERNAME` | `str \| None` | `None` | Proxy username |
| `proxy_password` | `BDFINANCE_PROXY_PASSWORD` | `str \| None` | `None` | Proxy password |
| `dse_url` | `BDFINANCE_DSE_URL` | `str` | `https://dsebd.org/` | DSE primary URL |
| `dse_alt_url` | `BDFINANCE_DSE_ALT_URL` | `str` | `https://dsebd.com.bd/` | DSE alternate URL (fallback) |

### URL Fallback

When a request to the primary DSE URL returns a 5xx status code, the HTTP client automatically retries using the alternate URL (`dse_alt_url`).

### Retry Behaviour

The client uses [tenacity](https://tenacity.readthedocs.io/) for retries with exponential backoff:

- Retries on `httpx.HTTPError` and `asyncio.TimeoutError`
- Stops after `max_retries` attempts
- Wait time: `retry_backoff_factor * 2^attempt`, clamped between `retry_min_wait` and `retry_max_wait`

---

## CacheConfig

Controls the caching layer. See [Caching](caching.md) for architecture details.

**Environment variable prefix:** `BDFINANCE_CACHE_`

```python
from bdfinance import CacheConfig

cache_config = CacheConfig(
    backend="redis",
    ttl=600,
    redis_url="redis://localhost:6379/1",
)
```

### All Options

| Field | Env Variable | Type | Default | Description |
|-------|-------------|------|---------|-------------|
| `backend` | `BDFINANCE_CACHE_BACKEND` | `"memory" \| "redis"` | `"memory"` | Cache backend type |
| `ttl` | `BDFINANCE_CACHE_TTL` | `int` | `300` | Default TTL in seconds (5 minutes) |
| `max_size` | `BDFINANCE_CACHE_MAX_SIZE` | `int` | `1000` | Max entries for memory backend |
| `redis_url` | `BDFINANCE_CACHE_REDIS_URL` | `str` | `redis://localhost:6379/0` | Redis connection URL |
| `redis_encoding` | `BDFINANCE_CACHE_REDIS_ENCODING` | `str` | `utf-8` | Redis encoding |

---

## Environment Variable Example

```bash
export BDFINANCE_TIMEOUT=60
export BDFINANCE_MAX_RETRIES=5
export BDFINANCE_RATE_LIMIT=20
export BDFINANCE_ENABLE_CACHE=true
export BDFINANCE_CACHE_BACKEND=redis
export BDFINANCE_CACHE_TTL=600
export BDFINANCE_CACHE_REDIS_URL=redis://my-redis:6379/0
```

These are picked up automatically when `ClientConfig()` and `CacheConfig()` are instantiated without arguments.

---

> **See also:** [Client & Ticker](client.md) · [Caching](caching.md)
