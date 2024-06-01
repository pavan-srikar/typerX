# /mnt/data/text_receiver.py

from flask import Flask, request, render_template_string
from pynput.keyboard import Controller
import threading
import time

app = Flask(__name__)
keyboard = Controller()

HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>Send Text</title>
</head>
<body>
    <h1>Send Text to Laptop</h1>
    <form action="/send-text" method="post">
        <label for="text">Text:</label><br>
        <textarea id="text" name="text" rows="10" cols="50" required></textarea><br>
        <label for="speed">Typing Speed (characters per second):</label><br>
        <input type="number" id="speed" name="speed" min="1" required><br><br>
        <button type="submit">Send</button>
    </form>
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
    if text and speed:
        typing_speed = float(speed)
        threading.Thread(target=type_text, args=(text, typing_speed)).start()
        return {"status": "success", "message": "Text received and being typed."}, 200
    return {"status": "error", "message": "Text or speed not provided."}, 400

def type_text(text, speed):
    delay = 1.0 / speed
    for char in text:
        keyboard.type(char)
        time.sleep(delay)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
