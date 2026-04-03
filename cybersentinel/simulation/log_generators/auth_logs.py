"""Auth Service log generator — login, logout, 2FA, session events."""
from datetime import datetime
from faker import Faker

fake = Faker()

VALID_EVENT_TYPES = {"success", "failure", "logout", "2fa", "lockout"}


def generate_auth_log(event_type: str = "success") -> str:
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"Invalid event_type '{event_type}'. Must be one of {VALID_EVENT_TYPES}")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = fake.ipv4()
    user = fake.user_name()

    templates = {
        "success": f"{ts} [AUTH] INFO  user={user} ip={ip} event=login status=success session_id={fake.uuid4()[:8]}",
        "failure": f"{ts} [AUTH] WARN  user={user} ip={ip} event=login status=failed reason=invalid_password attempt={fake.random_int(1, 5)}",
        "logout":  f"{ts} [AUTH] INFO  user={user} ip={ip} event=logout session_duration={fake.random_int(60, 3600)}s",
        "2fa":     f"{ts} [AUTH] INFO  user={user} ip={ip} event=2fa_challenge status=success method=totp",
        "lockout": f"{ts} [AUTH] ERROR user={user} ip={ip} event=account_lockout reason=too_many_failures attempts=5",
    }
    return templates[event_type]
