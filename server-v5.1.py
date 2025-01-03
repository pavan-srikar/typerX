# /mnt/data/text_receiver.py

from flask import Flask, request, jsonify, render_template_string
from pynput.keyboard import Controller, Key
import threading
import time
import logging

print('''
 _____                    __  __
|_   _|   _ _ __   ___ _ _\ \/ /
  | || | | | '_ \ / _ \ '__\  / 
  | || |_| | |_) |  __/ |  /  \ 
  |_| \__, | .__/ \___|_| /_/\_\ by pavan 
      |___/|_|                  
''')

app = Flask(__name__)
keyboard = Controller()
stop_flag = threading.Event()

logging.basicConfig(level=logging.DEBUG)

HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>typerX</title>
    <script>
        async function sendText(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            const response = await fetch('/send-text', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            document.getElementById('response-message').innerText = JSON.stringify(result);
        }

        async function stopTyping(event) {
            event.preventDefault();
            const response = await fetch('/stop-typing', {
                method: 'POST'
            });
            const result = await response.json();
            document.getElementById('response-message').innerText = JSON.stringify(result);
        }

        async function clearAndPasteText(event) {
            event.preventDefault();
            const textArea = document.getElementById('text');
            const clipboardText = await navigator.clipboard.readText();
            textArea.value = clipboardText;
        }
    </script>
</head>
<body>
    <h2>typerX_by_Pavan</h2>
    <h1>Send Text to Laptop</h1>
    <form onsubmit="sendText(event)" style="display: inline;">
        <label for="text">Text:</label><br>
        <textarea id="text" name="text" rows="10" cols="50" required></textarea><br>
        <button onclick="clearAndPasteText(event)">Clear and Paste New Text</button><br><br>
        <label for="speed">Typing Speed (characters per second):</label><br>
        <input type="number" id="speed" name="speed" min="1" value="25" required><br><br>
        <button type="submit">Send</button>
    </form>
    <form onsubmit="stopTyping(event)" style="display: inline;">
        <button type="submit">Stop Typing</button>
    </form>
    <p id="response-message"></p>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/send-text', methods=['POST'])
def send_text():
    text = request.form.get('text')
    speed = request.form.get('speed')
    app.logger.debug(f"Received text: {text}")
    app.logger.debug(f"Received speed: {speed}")
    if text and speed:
        typing_speed = float(speed)
        stop_flag.clear()  # Clear the stop flag before starting typing
        threading.Thread(target=type_text, args=(text, typing_speed)).start()
        return jsonify({"status": "success", "message": "Text received and being typed."})
    return jsonify({"status": "error", "message": "Text or speed not provided."}), 400

@app.route('/stop-typing', methods=['POST'])
def stop_typing():
    stop_flag.set()  # Set the stop flag to stop typing
    app.logger.debug("Typing stopped.")
    return jsonify({"status": "success", "message": "Typing stopped."})

def type_text(text, speed):
    delay = 1.0 / speed
    app.logger.debug(f"Typing text: {text} with delay: {delay}")
    for char in text:
        if stop_flag.is_set():
            app.logger.debug("Stop flag set. Breaking typing loop.")
            break
        if char == '\n':
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        elif char == '\r':
            continue
        else:
            keyboard.type(char)
        time.sleep(delay)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
