import smtplib
from email.message import EmailMessage

def send_order_confirmation(email: str, amount: float):
    msg = EmailMessage()
    msg["Subject"] = "Order Confirmation - Thank You for Your Purchase!"
    msg["From"] = "anirudh07072003@example.com"  # Use your sender email
    msg["To"] = email

    msg.set_content(f"""
    Dear Customer,

    Thank you for your purchase!
    We have successfully received your order of ₹{amount:.2f}.

    If you chose card payment, your transaction is being processed securely.

    Regards,
    E-Comm Team
    """)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("anirudh07072003@gmail.com", "fgpl nyno sjsm avdg")
            server.send_message(msg)
        print("Email sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")
