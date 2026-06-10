from typing import Any

async def get_current_user() -> dict[str, Any]:
    """
    Asynchronous mock dependency that returns a placeholder user structure.
    Used to unblock other API endpoint authentication dependencies during local testing.
    """
    return {
        "uuid": "00000000-0000-0000-0000-000000000001",
        "email": "test@company.com",
        "role": "Staff"
    }
