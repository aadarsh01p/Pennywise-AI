import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import EMAIL_ADDRESS, EMAIL_PASSWORD


def send_email(to_email: str, subject: str, body: str):

    try:

        message = MIMEMultipart()

        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(
            MIMEText(body, "plain")
        )

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_ADDRESS,
            to_email,
            message.as_string()
        )

        server.quit()

        return True

    except Exception as e:

        print("Email Error:", e)

        return False