import os
import json
import re
from datetime import datetime
import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory
import time

app = Flask(__name__, static_folder='static')

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Path for saved templates
TEMPLATES_FILE = os.path.join('data', 'saved_templates.json')

# Initialize templates file if it doesn't exist
if not os.path.exists(TEMPLATES_FILE):
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump([], f)

# Helper functions
def is_valid_email(email):
    """Validate email format using regex"""
    email_regex = r"^[a-zA-Z0-9_+&-]+(?:.[a-zA-Z0-9_+&-]+)*@(?:[a-zA-Z0-9-]+.)+[a-zA-Z]{2,7}$"
    return re.match(email_regex, email) is not None

def is_valid_date(date_str):
    """Validate date format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def format_date(date_str):
    """Format date string to MM/DD/YYYY"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%m/%d/%Y")

def read_templates():
    """Read templates from the JSON file"""
    try:
        with open(TEMPLATES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading templates: {e}")
        return []

def write_templates(templates):
    """Write templates to the JSON file"""
    try:
        with open(TEMPLATES_FILE, 'w') as f:
            json.dump(templates, f, indent=2)
            return True
    except Exception as e:
        print(f"Error writing templates: {e}")
        return False

def generate_personalized_email(user_data):
    """Generate email content based on occasion and user data"""
    name = user_data.get('email', '').split('@')[0]  # Extract name from email
    occasion = user_data.get('occasion', '').lower()
    sender_name = user_data.get('senderName', 'Your Name')

    email_template = ""

    if occasion == "birthday":
        email_template = f"""Dear {name},
Wishing you a very Happy Birthday! May this special day bring you lots of happiness, love, and wonderful memories.
Best wishes,
{sender_name}"""

    elif occasion == "leave":
        start_date = format_date(user_data.get('startDate', ''))
        end_date = format_date(user_data.get('endDate', ''))

        email_template = f"""Dear {name},
I hope you are doing well. I wanted to inform you that I will be on leave from {start_date} to {end_date}. Please let me know if you need any urgent assistance before my leave.
Best regards,
{sender_name}"""

    elif occasion == "alert":
        alert_message = user_data.get('alertMessage', '')

        email_template = f"""Dear {name},
This is an important alert: {alert_message}. Please make sure to take the necessary actions immediately.
Kind regards,
{sender_name}"""

    elif occasion == "festival":
        festival_name = user_data.get('festivalName', '')

        email_template = f"""Dear {name},
Wishing you a joyful and prosperous {festival_name}. May the festival bring happiness, peace, and good health to you and your loved ones.
Warm regards,
{sender_name}"""

    elif occasion == "holiday":
        holiday_start = format_date(user_data.get('holidayStartDate', ''))
        holiday_end = format_date(user_data.get('holidayEndDate', ''))

        email_template = f"""Dear {name},
Happy Holidays! I hope you are enjoying a well-deserved break from {holiday_start} to {holiday_end}. Wishing you a peaceful and relaxing holiday season.
Best wishes,
{sender_name}"""

    elif occasion == "announcement":
        details = user_data.get('announcementDetails', '')

        email_template = f"""Dear {name},
We are excited to announce the following:
{details}
For more information, please contact ph no.- 9087654321
Best regards,
{sender_name}"""

    else:
        email_template = "Sorry, we don't have a template for this occasion."

    return email_template

# Routes
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/generate-email', methods=['POST'])
def generate_email():
    """Generate an email based on provided data (not directly sending here)"""
    try:
        data = request.json

        # Basic validation
        errors = {}
        email = data.get('email', '').strip()
        occasion = data.get('occasion', '')

        if not email:
            errors['email'] = 'Recipient\'s email is required'
        elif not is_valid_email(email):
            errors['email'] = 'Invalid email format'

        if not occasion:
            errors['occasion'] = 'Occasion is required'

        # Occasion-specific validations
        if occasion == 'leave':
            start_date = data.get('startDate', '')
            end_date = data.get('endDate', '')

            if not start_date or not is_valid_date(start_date):
                errors['startDate'] = 'Valid start date is required'

            if not end_date or not is_valid_date(end_date):
                errors['endDate'] = 'Valid end date is required'

            if start_date and end_date and is_valid_date(start_date) and is_valid_date(end_date):
                if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
                    errors['endDate']
