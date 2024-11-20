from flask import Flask, render_template, request, jsonify
import os
import json
import re

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to extract messages from a .txt file
def extract_messages_from_text(text_file):
    messages = []
    current_date = ""
    current_time = ""
    current_sender = ""
    current_message = ""  # Initialize current_message to store multi-line messages

    # Open the file using UTF-8 encoding to properly handle characters
    with open(text_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        # Normalize space characters by replacing non-breaking spaces with regular spaces
        line = line.replace('\u202F', ' ')  # Replace non-breaking space with normal space

        # Regular expression to match the message format (date, time, sender, and message)
        match = re.match(r"(\d{2}/\d{2}/\d{2}), (\d{1,2}:\d{2} (?:am|pm)) - (.*?): (.*)", line.strip())

        # If the line matches the message format (date, time, sender, message)
        if match:
            date, time, sender, message = match.groups()

            # If there's a previous message, store it first
            if current_message:
                messages.append({
                    "time": f"{current_date}, {current_time}",
                    "sender": current_sender,
                    "message": current_message.strip()
                })

            # Update current variables with the new message details
            current_date = date
            current_time = time
            current_sender = sender
            current_message = message

        else:
            # If the line doesn't match a valid message format (likely continuation of previous message)
            if current_message:
                current_message += " " + line.strip()  # Append the continued part of the message

    # Append the last message if there is one
    if current_message:
        messages.append({
            "time": f"{current_date}, {current_time}",
            "sender": current_sender,
            "message": current_message.strip()
        })

    return messages

@app.route('/')
def index():
    return render_template('index.html')  # Renders the HTML page

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Process the file to convert to JSON
        messages = extract_messages_from_text(filename)

        return jsonify({"messages": messages})

    return jsonify({"error": "No file uploaded"}), 400

if __name__ == '__main__':
    app.run(debug=True)
