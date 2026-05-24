import logging


logger = logging.getLogger(__name__)


class MpesaService:
    @staticmethod
    def trigger_stk_push(phone, amount, reference):
        """
        Triggers an M-PESA STK Push.
        For now, this is a mock integration.
        """
        payload = {
            "phone": phone,
            "amount": amount,
            "transaction_type": "CustomerPayBillOnline",
            "reference": reference,
            "description": "Roots Party Membership"
        }
        logger.info("Mock M-PESA STK push queued", extra={"reference": reference, "amount": str(amount)})
        return True
