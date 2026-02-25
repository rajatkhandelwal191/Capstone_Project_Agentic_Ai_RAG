from app.db.db import get_connection

def seed():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM incidents")
    cur.execute("DELETE FROM service_requests")

    incidents = [

("INC1234567","Database latency spike","P1","Database","Open","2026-02-20"),
("INC1234568","Router failure APAC","P1","Network","Investigating","2026-02-21"),
("INC1234569","Payment API timeout","P2","Backend","In Progress","2026-02-22"),
("INC1234570","Disk usage alert","P3","Infra","Open","2026-02-22"),
("INC1234571","Firewall rule mismatch","P2","Security","Pending","2026-02-23"),
("INC1234572","Kubernetes pod crash","P2","Cloud","Open","2026-02-23"),
("INC1234573","VPN authentication issue","P3","Network","Open","2026-02-24"),
("INC1234574","Memory leak detected","P2","Backend","Investigating","2026-02-24"),
("INC1234575","DNS resolution delay","P3","Network","Open","2026-02-24"),
("INC1234576","Database replication lag","P1","Database","Open","2026-02-25"),
]

    requests =  [

("RITM1234567","HR","Access Provision","Open","2026-02-21"),
("RITM1234568","Finance","Report Generation","Closed","2026-02-20"),
("RITM1234569","Networking","VPN Access","Open","2026-02-22"),
("RITM1234570","Engineering","New Environment Setup","In Progress","2026-02-23"),
("RITM1234571","Security","Firewall Access","Open","2026-02-23"),
("RITM1234572","Cloud","Storage Expansion","Pending","2026-02-24")
]

    cur.executemany(
        "INSERT INTO incidents VALUES (?, ?, ?, ?, ?, ?)", incidents
    )

    cur.executemany(
        "INSERT INTO service_requests VALUES (?, ?, ?, ?, ?)", requests
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed()