# FILE: backend/app/services/payment_service.py
# DESCRIPTION: Payment processing utilities (stub — extend with Razorpay/Stripe)

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def process_payment(
    order_id: str,
    amount: float,
    customer_id: str,
    method: str = "cash",
) -> dict[str, Any]:
    """
    Stub for payment processing.
    Replace with real Razorpay / Stripe integration when needed.
    """
    logger.info("Processing payment for order %s: amount=%.2f method=%s", order_id, amount, method)
    return {
        "payment_id": f"pay_{order_id}",
        "order_id": order_id,
        "amount": amount,
        "method": method,
        "status": "pending_at_counter",
    }
