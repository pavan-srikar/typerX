from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pynput.keyboard import Controller, Key
import threading
import time
import logging
import platform
import os
import pyscreenshot as ImageGrab

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)

# Initialize variables
keyboard = Controller()
stop_flag = threading.Event()
typing_speed = 25  # Default typing speed (characters per second)
active_devices = {}

# Function to generate a unique device ID based on system info
def generate_device_id():
    device_name = platform.node()
    device_os = platform.system()
    return f"{device_name} ({device_os})"

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    device_id = generate_device_id()
    if device_id not in active_devices:
        active_devices[device_id] = device_id
    device_list = "\n".join([f"{i+1}. {device}" for i, device in enumerate(active_devices.values())])
    await update.message.reply_text(
        f"Welcome to TyperX by 卩卂ᐯ卂几 !\n\n"
        "Commands:\n"
        "/select <device_id> - Select a device\n"
        "/speed <number> - Set typing speed (characters per second)\n"
        "/text <message> - Start typing the provided text\n"
        "/stop - Stop typing\n"
        "/screenshot - Capture and send a screenshot\n\n"
        f"Available Devices:\n{device_list}"
    )

# /select command handler
async def select_device(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        device_id = int(context.args[0])
        if 1 <= device_id <= len(active_devices):
            selected_device = list(active_devices.values())[device_id - 1]
            await update.message.reply_text(f"Device '{selected_device}' selected.")
        else:
            await update.message.reply_text("Invalid device ID. Please select a valid device.")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid device ID. Example: /select 1")

# /speed command handler
async def set_speed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global typing_speed
    try:
        speed = float(context.args[0])
        if speed <= 0:
            raise ValueError("Speed must be greater than zero.")
        typing_speed = speed
        await update.message.reply_text(f"Typing speed set to {typing_speed} characters per second.")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid speed. Example: /speed 25")

# /text command handler
async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = " ".join(context.args)
        if not text:
            await update.message.reply_text("Please provide text to type. Example: /text Hello World")
            return
        formatted_text = text.replace(";", ";\n").replace("//", "\n//")
        stop_flag.clear()
        threading.Thread(target=type_text, args=(formatted_text, typing_speed)).start()
        await update.message.reply_text("Text received and typing started.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# /stop command handler
async def stop_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stop_flag.set()
    await update.message.reply_text("Typing stopped.")

# /screenshot command handler
async def capture_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        screenshot_path = "/tmp/screenshot.png"
        ImageGrab.grab().save(screenshot_path)
        with open(screenshot_path, "rb") as screenshot_file:
            await update.message.reply_photo(photo=screenshot_file)
        os.remove(screenshot_path)
    except Exception as e:
        await update.message.reply_text(f"Error capturing screenshot: {str(e)}")

# Function to simulate typing
def type_text(text, speed):
    delay = 1.0 / speed
    for char in text:
        if stop_flag.is_set():
            break
        if char == '\n':
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        else:
            keyboard.type(char)
        time.sleep(delay)

# Generic handler for all other messages
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.debug(f"Unrecognized message: {update.message.text}")
    await update.message.reply_text("I don't recognize this command. Type /help for assistance.")

# Main function to run the bot
def main():
    token = "7429953156:AAFtwfuLzUGqh_lBBkMOLCcINUzxb5DkwmI"  # Replace with your bot's token
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("select", select_device))
    application.add_handler(CommandHandler("speed", set_speed))
    application.add_handler(CommandHandler("text", send_text))
    application.add_handler(CommandHandler("stop", stop_typing))
    application.add_handler(CommandHandler("screenshot", capture_screenshot))
    application.add_handler(MessageHandler(filters.ALL, handle_all_messages))
    
    # Start the bot
    logging.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
