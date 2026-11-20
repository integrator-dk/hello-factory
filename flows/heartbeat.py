"""Test job for Factory's shared Prefect workers (ADR-0012): proves manifest -> Prefect -> container -> result."""
import os
import platform

from prefect import flow, get_run_logger


@flow(name="heartbeat", retries=1, retry_delay_seconds=30, timeout_seconds=120)
def heartbeat() -> dict:
    log = get_run_logger()
    info = {"solution": os.environ.get("FACTORY_SOLUTION", "hello-factory"),
            "version": os.environ.get("APP_VERSION", "dev"), "python": platform.python_version()}
    log.info("Heartbeat from %(solution)s %(version)s (Python %(python)s)", info)
    return info


if __name__ == "__main__":
    heartbeat()
