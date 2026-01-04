class MpesaService:
    @staticmethod
    def trigger_stk_push(phone, amount):
        """
        Triggers an M-PESA STK Push.
        For now, this is a mock integration.
        """
        payload = {
            "phone": phone,
            "amount": amount,
            "transaction_type": "CustomerPayBillOnline",
            "reference": "ROOTS_MEMBERSHIP",
            "description": "Roots Party Membership"
        }
        print(f"--- M-PESA STK PUSH ---")
        print(f"To: {phone}")
        print(f"Amount: KES {amount}")
        print(f"Payload: {payload}")
        print(f"-----------------------")
        return True
