from app.db.repository import get_incidents, get_service_requests


def get_open_incidents():

    incidents = get_incidents()

    return [
        i for i in incidents
        if i.status.lower() != "closed"
    ]


def get_open_service_requests():

    requests = get_service_requests()

    return [
        r for r in requests
        if r.status.lower() != "closed"
    ]
