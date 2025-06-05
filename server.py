#!/usr/bin/env python3
import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs

class ContactFormHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/send-email':
            try:
                # Parse form data
                content_type = self.headers.get('Content-Type')
                if content_type and content_type.startswith('application/x-www-form-urlencoded'):
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    form_data = parse_qs(post_data)
                    
                    # Extract form fields
                    name = form_data.get('name', [''])[0]
                    email = form_data.get('email', [''])[0]
                    subject = form_data.get('subject', [''])[0]
                    message = form_data.get('message', [''])[0]
                    
                    # Send email
                    success = self.send_email(name, email, subject, message)
                    
                    # Send response
                    response = json.dumps({'success': success})
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response.encode())
                else:
                    self.send_error(400, "Invalid content type")
            except Exception as e:
                print(f"Error handling POST request: {e}")
                response = json.dumps({'success': False, 'error': str(e)})
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.encode())
        else:
            self.send_error(404, "Not found")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_email(self, name, email, subject, message):
        try:
            gmail_user = os.environ.get('GMAIL_USER')
            gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
            
            if not gmail_user or not gmail_password:
                print("Gmail credentials not found in environment variables")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = gmail_user
            msg['To'] = gmail_user  # Send to yourself
            msg['Subject'] = f"Portfolio Contact: {subject}"
            
            # Email body
            body = f"""
New message from portfolio contact form:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This message was sent from your portfolio website.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            text = msg.as_string()
            server.sendmail(gmail_user, gmail_user, text)
            server.quit()
            
            print(f"Email sent successfully from {name} ({email})")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), ContactFormHandler)
    print(f"Server running on port {port}")
    server.serve_forever()