import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv
_ = load_dotenv()


def send_email(to_email, month, num_requests, charges):
    # Email credentials
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = f"Your Subscription Charges for {month}"

    body = f"""
    <html>
    <body>
        <table width="100%" cellspacing="0" cellpadding="0" border="0">
            <tr>
                <td align="left">
                    <img src="cid:logo" alt="Company Logo" width="100" height="50">
                </td>
            </tr>
        </table>
        <h2>Subscription Charges for {month}</h2>
        <p>Dear Patient,</p>
        <p>Here are the details of your subscription usage for {month}:</p>
        <ul>
            <li><strong>Number of Requests:</strong> {num_requests}</li>
            <li><strong>Charges:</strong> £{charges:.2f}</li>
        </ul>
        <p>Thank you for using our service!</p>
        <p>Best Regards,<br>Translaited ltd</p>
        <footer>
            <hr>
            <p><a href="https://translaited.com/">translaited.com</a></p>
        </footer>
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

     # Attach the logo image (ensure the logo image is accessible)
    with open(os.path.join('report_scanner', 'images','logo.jpg'), 'rb') as img_file:
        msg_image = MIMEImage(img_file.read())
        msg_image.add_header('Content-ID', '<logo>')
        msg.attach(msg_image)

    try:
        # Set up the SMTP server
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.ehlo()
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)  # Login to the email account
            text = msg.as_string()
            server.sendmail(sender_email, to_email, text)  # Send the email
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    

def send_report_notification(to_email, report_code, url):
    # Email credentials
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = f"Translaited Report"

    body = f"""
    <html>
    <body>
        <table width="100%" cellspacing="0" cellpadding="0" border="0">
            <tr>
                <td align="left">
                    <img src="cid:logo" alt="Company Logo" width="100" height="50">
                </td>
            </tr>
        </table>
        <h2>Translaited version of your report</h2>
        <p>Dear Patient,</p>
        <p>Your report is generated and is available at <a href="{url}">{url}</a>. You can access your report by clicking the given link. 
        Your verification code is <b>{report_code}</b>. Please don't share it with anyone.</p>
       
        <p>Thank you for using our service!</p>
        <p>Best Regards,<br>Translaited ltd</p>
        <footer>
            <hr>
            <p><a href="https://translaited.com/">translaited.com</a></p>
        </footer>
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

     # Attach the logo image (ensure the logo image is accessible)
    with open(os.path.join(os.path.join(str(Path(__file__).resolve().parent.parent)), 'images','logo.jpg'), 'rb') as img_file:
        msg_image = MIMEImage(img_file.read())
        msg_image.add_header('Content-ID', '<logo>')
        msg.attach(msg_image)

    try:
        # Set up the SMTP server
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.ehlo()
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)  # Login to the email account
            text = msg.as_string()
            server.sendmail(sender_email, to_email, text)  # Send the email
        return "Email sent successfully!"
    except Exception as e:
        print(e)
        return "Failed to send email"
    