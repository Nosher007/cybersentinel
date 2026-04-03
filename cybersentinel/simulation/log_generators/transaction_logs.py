"""Transaction Engine log generator — transfers, payments, probes, scraping."""
from datetime import datetime
from faker import Faker

fake = Faker()

VALID_TRANSACTION_TYPES = {"transfer", "payment", "probe", "scrape"}


def generate_transaction_log(
    transaction_type: str = "transfer",
    amount: float | None = None,
) -> str:
    if transaction_type not in VALID_TRANSACTION_TYPES:
        raise ValueError(
            f"Invalid transaction_type '{transaction_type}'. Must be one of {VALID_TRANSACTION_TYPES}"
        )
    if amount is not None and amount <= 0:
        raise ValueError(f"amount must be > 0, got {amount}")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txn_id = f"txn_id={fake.uuid4()[:8]}"
    user = fake.user_name()

    if transaction_type == "probe":
        amt = amount or fake.random_element([1, 2, 3, 5])
        status = "success"
        return (f"{ts} [TXN-ENGINE] INFO  user={user} type=transfer {txn_id} "
                f"amount=${amt:.2f} status={status} duration={fake.random_int(10,80)}ms")

    elif transaction_type == "transfer":
        amt = amount or round(fake.random_number(digits=4) + fake.random.uniform(0, 99), 2)
        status = fake.random_element(["success", "success", "success", "flagged"])
        return (f"{ts} [TXN-ENGINE] INFO  user={user} type=transfer {txn_id} "
                f"amount=${amt:,.2f} status={status} duration={fake.random_int(50,300)}ms")

    elif transaction_type == "payment":
        amt = amount or round(fake.random_number(digits=3) + fake.random.uniform(0, 99), 2)
        status = fake.random_element(["success", "failed", "pending"])
        return (f"{ts} [TXN-ENGINE] INFO  user={user} type=payment {txn_id} "
                f"amount=${amt:,.2f} status={status} duration={fake.random_int(30,200)}ms")

    else:  # scrape
        endpoint = fake.random_element(["/api/v1/balance", "/api/v1/history", "/api/v1/users"])
        return (f"{ts} [TXN-ENGINE] WARN  user={user} type=bulk_query {txn_id} "
                f"endpoint={endpoint} requests={fake.random_int(50,500)} status=flagged")
