## me trying to make sense of it

## Things we know are wrong or we havent looked at. Potential issues
    - Backend gunicorn conf
    - K8. No thoughts put into it. No resources, cores, monitoring.. nothing.
    - Nginx configuration

# Profiling docker locally - DB and FASTPI on containers. No gunicorn or uvicorn specific config.
    - 4 cores. 6gb RAM. Postgres and Gunicorn sharing them
    - Read tests
        - peat at ~180rps
        - +2k users with increasing response time but no errors from backend. Only timeouts on frontend.
        - To improve: profile what queries seem to be taken most time and cache them. (REDIS)
    - Write tests
        - peat at ~140rps
        - ~1.2k users with increasing response time but no errors from backend. Only timeouts on frontend
        - To improve: General profiling to see where we spend more time. Maybe ratelimit to avoid writes to take over the system?
    - Read/Write tests
        - peak at ~120rps.

# Locally but with caching (caching greatly imporove reads 180->370 but at a cost in writes 140->70 (this can be due to added data serialization ebtween DB-Cache))
    - Read tests
        - peak at ~370rps
        - 3k users timeouts but able to hold +300rps
        - To improve: profile queries taking longer time. Cache efficiently.
    - Write tests
        - peak at ~65rps
        - ~1.2k users with increasing response time but no errors from backend. Only timeouts on frontend
        - To improve: Caching slow the writes down a lot. Profile see where we spend time.
    - Read/Write
        - peak at ~90rps