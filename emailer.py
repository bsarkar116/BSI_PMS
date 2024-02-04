import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
PORT = 587
EMAIL = os.environ.get("EM_USER")  # DH1, DH2, AH22
PASSWORD = os.environ.get("EM_PASS")

context = ssl.create_default_context()


def send_email(u, e, passw, i):
    text = ""
    if i == 1:
        body = """\
                        Hello """ + str(u) + """, 

                        Please use the following credentials to login to PMS.

                        User: """ + str(u) + """
                        Password: """ + str(passw) + """


                        Thanks
                        """
        message = MIMEMultipart()
        message["From"] = EMAIL
        message["To"] = e
        message["Subject"] = "Welcome to PMS!!"
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()
    elif i == 2:
        body = """\
                        Hello """ + str(u) + """, 

                        Your login password has been reset. 
                        Please use the following credentials to login to PMS.

                        User: """ + str(u) + """
                        Password: """ + str(passw) + """


                        Thanks
                        """
        message = MIMEMultipart()
        message["From"] = EMAIL
        message["To"] = e
        message["Subject"] = "PMS Password Reset!!"
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()
    elif i == 3:
        body = """\
                        Hello """ + str(u) + """, 

                        Your login password has been rotated to meet new policy requirements.
                        Please use the following credentials to login to PMS.

                        User: """ + str(u) + """
                        Password: """ + str(passw) + """


                        Thanks
                        """
        message = MIMEMultipart()
        message["From"] = EMAIL
        message["To"] = e
        message["Subject"] = "PMS Password Reset!!"
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()

    with smtplib.SMTP(SMTP_SERVER, PORT) as server:
        server.starttls(context=context)  # Secure the connection
        server.login(EMAIL, PASSWORD)

        server.sendmail(EMAIL, e, text)
