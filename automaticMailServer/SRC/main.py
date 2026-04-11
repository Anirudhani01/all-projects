from flask import Flask
from flask_apscheduler import APScheduler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
import csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

app = Flask(__name__)

class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def send_emails():
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'emp.csv')
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name']
                to_email = row['email']
                salary = row['salary']
                task = row['task']

                msg = MIMEMultipart("alternative")
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = to_email
                msg['Subject'] = 'Your Task & Salary Details'

                html = f"""
                <html>
                  <head>
                    <style>
                      body {{
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        color: #333;
                      }}
                      table {{
                        border-collapse: collapse;
                        width: 100%;
                        max-width: 600px;
                      }}
                      th, td {{
                        text-align: left;
                        padding: 10px;
                        border: 1px solid #ddd;
                      }}
                      th {{
                        background-color: #f4f4f4;
                        color: #333;
                      }}
                      tr:nth-child(even) {{
                        background-color: #f9f9f9;
                      }}
                      .container {{
                        margin: 20px 0;
                      }}
                    </style>
                  </head>
                  <body>
                    <p>Good Afternoon <strong>{name}</strong>,</p>
                    <p>Here are your details for today:</p>
                    <div class="container">
                      <table>
                        <tr>
                          <th>Name</th>
                          <th>Salary (₹)</th>
                          <th>Task</th>
                        </tr>
                        <tr>
                          <td>{name}</td>
                          <td>{salary}</td>
                          <td>{task}</td>
                        </tr>
                      </table>
                    </div>
                    <p>Have a great day!<br><em>– HR Department</em></p>
                  </body>
                </html>
                """

                msg.attach(MIMEText(html, 'html'))

                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.send_message(msg)
                    server.quit()
                    print(f"✅ Email sent to {name} ({to_email})")
                except Exception as smtp_err:
                    print(f"❌ Failed to send to {to_email}: {smtp_err}")
    except Exception as e:
        print(f"❌ Error sending emails: {e}")

# Run daily at 4:00 PM
@scheduler.task('cron', id='daily_email_job', hour=17, minute=00)
def scheduled_job():
    print("⏰ Scheduled Task Triggered at 4:00 PM")
    send_emails()

@app.route("/")
def home():
    return "📧 Mail Server Running"

@app.route("/send-test")
def send_test_email():
    try:
        send_emails()
        return "📨 Test emails sent!"
    except Exception as e:
        return f"Internal Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
