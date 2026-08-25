from functools import lru_cache


@lru_cache(maxsize=1)
def cached_recovery():

    from ml.recovery_prediction import predict_recovery

    return predict_recovery()


@lru_cache(maxsize=1)
def cached_risk():

    from ml.anomaly_detection import detect_anomalies

    return detect_anomalies()


@lru_cache(maxsize=1)
def cached_root_cause():

    from ml.root_cause import analyze_failure_reasons

    return analyze_failure_reasons()


@lru_cache(maxsize=1)
def cached_forecast():

    from ml.revenue_prediction import predict_next_days

    return predict_next_days(7)


def clear_cache():

    cached_recovery.cache_clear()
    cached_risk.cache_clear()
    cached_root_cause.cache_clear()
    cached_forecast.cache_clear()