# /mnt/data/text_receiver.py

from flask import Flask, request, render_template_string
from pynput.keyboard import Controller
import threading

app = Flask(__name__)
keyboard = Controller()

HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>TyperX</title>
</head>
<body>
    <h1>Enter your code nigga</h1>
    <form action="/send-text" method="post">
        <label for="text">Text:</label>
        <input type="text" id="text" name="text" required>
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
    if text:
        threading.Thread(target=type_text, args=(text,)).start()
        return {"status": "success", "message": "Text received and being typed."}, 200
    return {"status": "error", "message": "No text provided."}, 400

def type_text(text):
    for char in text:
        keyboard.type(char)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
