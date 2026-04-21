import smtplib

def send_email(name):
    sender = "your_email@gmail.com"
    password = "your_app_password"  # NOT your normal password
    receiver = "your_email@gmail.com"

    message = f"Subject: Attendance Alert\n\n{name} marked attendance."

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, message)
    except Exception as e:
        print("Email failed:", e)