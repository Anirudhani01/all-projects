from fastapi import Form

class PaymentForm:
    def __init__(
        self,
        email: str = Form(...),
        payment_method: str = Form(...),
        card_number: str = Form(None),
        cvv: str = Form(None)
    ):
        self.email = email
        self.payment_method = payment_method
        self.card_number = card_number
        self.cvv = cvv
