from app.db.repository import get_incidents, get_service_requests
from app.core.logger import logger


def get_open_incidents():
    logger.info("tool=get_open_incidents | source=get_incidents()")

    incidents = get_incidents()
    logger.info("tool=get_open_incidents | raw_count=%s", len(incidents))

    open_incidents = [
        i for i in incidents
        if i.status.lower() != "closed"
    ]
    logger.info("tool=get_open_incidents | filtered_count=%s", len(open_incidents))

    return open_incidents


def get_open_service_requests():
    logger.info("tool=get_open_service_requests | source=get_service_requests()")

    requests = get_service_requests()
    logger.info("tool=get_open_service_requests | raw_count=%s", len(requests))

    open_requests = [
        r for r in requests
        if r.status.lower() != "closed"
    ]
    logger.info("tool=get_open_service_requests | filtered_count=%s", len(open_requests))

    return open_requests
