import uuid


def generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


def generate_tracking_number():
    return f"TRK-{uuid.uuid4().hex[:12].upper()}"


def generate_payment_reference():
    return f"PAY-{uuid.uuid4().hex[:10].upper()}"
