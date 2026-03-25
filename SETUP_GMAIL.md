import smtplib
from email.message import EmailMessage
import os

GMAIL_USER = "smartdrip19@gmail.com"
GMAIL_PASSWORD = "auuu terx ocrh uvca"

def send_waste_report(waste_type, latitude, longitude, pdf_path):

    receiver_email = "viswamecse@gmail.com"

    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = receiver_email
    msg["Subject"] = "Smart Waste Report"

    maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

    body = f"""
Waste Type: {waste_type}import smtplib
from email.message import EmailMessage
import os

GMAIL_USER = "smartdrip19@gmail.com"
GMAIL_PASSWORD = "auuu terx ocrh uvca"  # Correct app password

def send_waste_report(waste_type, latitude, longitude, pdf_path=None):
    receiver_email = "viswamecse@gmail.com"

    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = receiver_email
    msg["Subject"] = "Smart Waste Report"

    maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    body = f"""
Waste Type: {waste_type}

Location:
{maps_link}
"""
    msg.set_content(body)

    # Attach PDF if exists
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(pdf_path)
            )

    print("Sending To:", receiver_email)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        print("Mail Sent Successfully ✅")
    except Exception as e:
        print("Failed to send mail ❌", e)


Location:
{maps_link}
"""

    msg.set_content(body)

    # Attach PDF
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="Waste_Report.pdf"
            )

    print("Sending To:", receiver_email)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)

    print("Mail Sent Successfully")
