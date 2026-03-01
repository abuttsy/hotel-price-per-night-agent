import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailManager:
    def __init__(self, sender_email: str, sender_password: str, receiver_email: str = "ultimatefamilyhotels@gmail.com"):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email

    def send_price_alert(self, hotel_name: str, old_price: float, new_price: float):
        """
        Sends an email alert when a significant price swing is detected.
        """
        if old_price is None:
            return

        percent_change = ((new_price - old_price) / old_price) * 100

        # Check if change is 20% or more (positive or negative)
        if abs(percent_change) < 20:
            return

        subject = f"Price Alert: {hotel_name} - {percent_change:.1f}% change"
        body = (
            f"A significant price change has been detected for {hotel_name}.\n\n"
            f"Old Price: {old_price:.2f} EUR\n"
            f"New Price: {new_price:.2f} EUR\n"
            f"Change: {percent_change:.1f}%\n"
        )

        self._send_email(subject, body)

    def _send_email(self, subject: str, body: str):
        if not self.sender_email or not self.sender_password:
            print("Email credentials not set. Skipping email alert.")
            return

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Using Gmail's SMTP server as an example
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.receiver_email, text)
            server.quit()
            print(f"Email alert sent to {self.receiver_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
