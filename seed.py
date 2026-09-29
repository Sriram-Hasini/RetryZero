from memory import retain_memory, close_memory


INCIDENTS = [

    """
Incident ID: INC-1001
Date: 2026-08-02
Service: payments-api
Error: HTTP 504 Gateway Timeout

Problem:
Checkout requests were timing out during periods of high traffic.

Attempted fix:
Restarted the payments-api pods.

Outcome:
FAILED.

Reason:
The service restarted successfully, but the timeout returned within 6 minutes.
The underlying database connection pool was exhausted.
""",

    """
Incident ID: INC-1002
Date: 2026-08-08
Service: payments-api
Error: HTTP 504 Gateway Timeout

Problem:
Checkout requests were timing out.

Attempted fix:
Increased application replicas from 4 to 8.

Outcome:
FAILED.

Reason:
Additional replicas increased database connection pressure.
Timeouts continued.
""",

    """
Incident ID: INC-1003
Date: 2026-08-15
Service: payments-api
Error: HTTP 504 Gateway Timeout

Problem:
Checkout requests were timing out.

Attempted fix:
Increased the database connection pool from 50 to 100 and reduced idle connection lifetime.

Outcome:
WORKED.

Result:
Timeout rate returned to normal and remained stable during the traffic spike.
""",

    """
Incident ID: INC-1004
Date: 2026-08-22
Service: payments-api
Error: HTTP 504 Gateway Timeout

Problem:
Checkout requests were timing out again during a traffic spike.

Attempted fix:
Restarted payments-api.

Outcome:
FAILED.

Reason:
The restart temporarily reduced errors but the same connection exhaustion problem returned.
""",

    """
Incident ID: INC-1005
Date: 2026-08-28
Service: payments-api
Error: HTTP 504 Gateway Timeout

Problem:
Checkout latency increased dramatically.

Attempted fix:
Scaled payments-api from 6 replicas to 12.

Outcome:
FAILED.

Reason:
Database connection utilization increased further.
Scaling the application did not resolve the database bottleneck.
""",

    """
Incident ID: INC-1006
Date: 2026-09-03
Service: payments-api
Error: HTTP 504 Gateway Timeout

Problem:
High checkout traffic caused database connection exhaustion.

Attempted fix:
Adjusted database connection pool configuration and enabled connection recycling.

Outcome:
WORKED.

Result:
Checkout success rate returned to 99.8%.
""",

    """
Incident ID: INC-1007
Date: 2026-09-10
Service: payments-api
Error: HTTP 504 Gateway Timeout

Problem:
Checkout requests exceeded the upstream timeout.

Attempted fix:
Restarted the application.

Outcome:
FAILED.

Reason:
The restart only provided temporary relief.
Connection exhaustion returned shortly afterward.
""",

    """
Incident ID: INC-1008
Date: 2026-09-17
Service: payments-api
Error: HTTP 504 Gateway Timeout

Problem:
Payment requests timed out after a sudden traffic increase.

Attempted fix:
Increased application replicas.

Outcome:
FAILED.

Reason:
More replicas created more database connections and increased pressure on the database.
""",

    """
Incident ID: INC-1009
Date: 2026-09-20
Service: payments-api
Error: HTTP 504 Gateway Timeout

Problem:
Payment requests timed out.

Attempted fix:
Increased database connection capacity and tuned connection recycling.

Outcome:
WORKED.

Result:
Timeouts disappeared and database utilization remained within safe limits.
"""
]


def seed_hindsight():

    print("Starting RetryZero memory seeding...\n")

    for index, incident in enumerate(INCIDENTS, start=1):

        try:
            retain_memory(incident)
            print(f"[OK] Incident {index} stored")

        except Exception as error:
            print(f"[ERROR] Incident {index}: {error}")

    print("\nSeeding complete.")


if __name__ == "__main__":
    try:
        seed_hindsight()
    finally:
        close_memory()