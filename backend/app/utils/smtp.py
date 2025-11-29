import os
import smtplib
from email.message import EmailMessage

# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USER = os.getenv("SMTP_USER")
# SMTP_PASSWORD = os.getenv("SMTP_PASS")

# def send_reset_password_email(to_email: str, reset_link: str):
#     msg = EmailMessage()
#     msg['Subject'] = 'Password Reset Request'
#     msg['From'] = SMTP_USER
#     msg['To'] = to_email
#     msg.set_content(f'Truy cập vào liên kết sau để đặt lại mật khẩu tài khoản TDTU QA System của bạn:\n\n{reset_link}')

#     try:
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(SMTP_USER, SMTP_PASSWORD)
#             server.send_message(msg)
#     except Exception as e:
#         print(f"Failed to send email: {e}")
#         raise