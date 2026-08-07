from email_mkt.sending.rate_limiter import RateLimiter


def test_rate_limiter_builds_with_positive_interval() -> None:
    limiter = RateLimiter(requests_per_second=4)
    assert limiter.min_interval == 0.25

