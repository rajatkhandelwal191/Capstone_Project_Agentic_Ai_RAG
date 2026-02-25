from app.db.db import get_connection
from app.schemas.models import Incident, ServiceRequest


def get_incidents():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM incidents")
    rows = cur.fetchall()

    conn.close()

    return [
        Incident(
            id=r[0],
            title=r[1],
            severity=r[2],
            team=r[3],
            status=r[4],
            created_at=r[5]
        )
        for r in rows
    ]


def get_service_requests():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM service_requests")
    rows = cur.fetchall()

    conn.close()

    return [
        ServiceRequest(
            id=r[0],
            department=r[1],
            request_type=r[2],
            status=r[3],
            created_at=r[4]
        )
        for r in rows
    ]
