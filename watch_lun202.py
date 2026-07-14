import os
import requests
import smtplib
from email.mime.text import MIMEText

NCT_ID = "NCT04614103"
API_URL = f"https://clinicaltrials.gov/api/v2/studies/{NCT_ID}"
STATUS_FILE = "last_status.txt"

EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_TO = os.environ.get("EMAIL_TO", EMAIL_USERNAME)


def get_current_status():
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["protocolSection"]["statusModule"]["overallStatus"]


def read_last_status():
    if not os.path.exists(STATUS_FILE):
        return None

    with open(STATUS_FILE, "r") as f:
        return f.read().strip() or None


def write_last_status(status):
    with open(STATUS_FILE, "w") as f:
        f.write(status)


def send_email(old_status, new_status):
    subject = f"LUN-202 status changed: {old_status} → {new_status}"

    body = f"""
The ClinicalTrials.gov status changed.

Study: {NCT_ID}

Old status:
{old_status}

New status:
{new_status}

{API_URL}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USERNAME
    msg["To"] = EMAIL_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        smtp.send_message(msg)


def main():
    current = get_current_status()
    previous = read_last_status()

    print("Current:", current)
    print("Previous:", previous)

    if previous is None:
        write_last_status(current)
        print("Initial status saved.")
        return

    if current != previous:
        send_email(previous, current)
        write_last_status(current)
        print("Status changed.")
    else:
        print("No change.")


if __name__ == "__main__":
    main()
