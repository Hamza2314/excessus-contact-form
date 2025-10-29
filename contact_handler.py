from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
CORS(app)  # Allow requests from your website

# Zoho SMTP settings

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.zoho.eu')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL = os.getenv('EMAIL', 'kontakt@excessus.de')
PASSWORD = os.getenv('PASSWORD')

def send_email(to_email, subject, body):
    """Helper function to send emails via Zoho"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/contact', methods=['POST'])
def handle_contact():
    """Handle contact form submissions"""
    try:
        # Get form data
        name = request.form.get('name')
        customer_email = request.form.get('email')
        message = request.form.get('message')
        
        # Validate data
        if not name or not customer_email or not message:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # 1. Send auto-reply to customer
        auto_reply_subject = "Ihre Nachricht wurde empfangen"
        auto_reply_body = f"""Hallo {name},

Vielen Dank für Ihre Nachricht!

Wir haben Ihre Anfrage erhalten und werden uns innerhalb von 24 Stunden bei Ihnen melden.

Mit freundlichen Grüßen,
Hamza Masri
Excessus

E-Mail: kontakt@excessus.de
Telefon: +49 163 3612150
Website: www.excessus.de
"""
        
        send_email(customer_email, auto_reply_subject, auto_reply_body)
        
        # 2. Send notification to yourself
        notification_subject = f"Neue Kontaktanfrage von {name}"
        notification_body = f"""Neue Nachricht von der Website:

Name: {name}
Email: {customer_email}
Nachricht: 
{message}

---
Gesendet über Excessus Kontaktformular
"""
        
        send_email(EMAIL, notification_subject, notification_body)
        
        return jsonify({"success": True, "message": "Email sent successfully"}), 200
        
    except Exception as e:
        print(f"Error handling contact form: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to make sure server is running"""
    return "Contact form handler is running! ✅"

@app.route('/', methods=['GET'])
def home():
    """Home page with simple form for testing"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Contact Form</title>
        <style>
            body { font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; }
            input, textarea { width: 100%; padding: 10px; margin: 10px 0; }
            button { padding: 10px 20px; background: black; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Test Contact Form</h1>
        <form action="/contact" method="POST">
            <input type="text" name="name" placeholder="Name" required>
            <input type="email" name="email" placeholder="Email" required>
            <textarea name="message" placeholder="Message" rows="5" required></textarea>
            <button type="submit">Send</button>
        </form>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)