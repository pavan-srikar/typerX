from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pynput.keyboard import Controller, Key
import threading
import time
import logging
import platform
import os

print('''
 _____                    __  __
|_   _|   _ _ __   ___ _ _\ \/ /
  | || | | | '_ \ / _ \ '__\  / 
  | || |_| | |_) |  __/ |  /  \ 
  |_| \__, | .__/ \___|_| /_/\_\ by pavan 
      |___/|_|                  
''')

keyboard = Controller()
stop_flag = threading.Event()
typing_speed = 25  # Default typing speed (characters per second)

# Device storage to track active devices
active_devices = {}

logging.basicConfig(level=logging.DEBUG)

# Function to generate a unique device ID based on system info
def generate_device_id():
    device_name = platform.node()
    device_os = platform.system()
    return f"{device_name} ({device_os})"

# Start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    device_id = generate_device_id()

    # Register the device if not already in the active devices list
    if device_id not in active_devices:
        active_devices[device_id] = device_id

    device_list = "\n".join([f"{i+1} {device}" for i, device in enumerate(active_devices.values())])

    await update.message.reply_text(
        f'Welcome to TyperX by Pavan!\n'
        'Commands:\n'
        '/select <device_id> - Select a device\n'
        '/speed <number> - Set typing speed (characters per second)\n'
        '/text <message> - Start typing the provided text\n'
        '/stop - Stop typing\n'
        'Default typing speed is 25 characters per second.\n\n'
        f'Available Devices:\n{device_list}\n'
    )

# Command to select a device
async def select_device(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        device_id = int(context.args[0])  # Get the device_id from the command argument
        if 1 <= device_id <= len(active_devices):
            selected_device = list(active_devices.values())[device_id - 1]
            await update.message.reply_text(f"Device '{selected_device}' selected.")
            # Here, you can implement logic to target the selected device for typing
        else:
            await update.message.reply_text("Invalid device ID. Please select a valid device.")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid device ID. Example: /select 1")

# Command to set the typing speed
async def set_speed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global typing_speed
    try:
        speed = float(context.args[0])  # Get the speed from the command argument
        if speed <= 0:
            raise ValueError("Speed must be greater than zero.")
        typing_speed = speed
        await update.message.reply_text(f"Typing speed set to {typing_speed} characters per second.")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid speed. Example: /speed 25")

# Command to start typing the provided text
async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global typing_speed
    try:
        text = " ".join(context.args)  # Join all arguments as the text to type
        if not text:
            await update.message.reply_text("Please provide text to type. Example: /text Hello World")
            return
        logging.debug(f"Received text: {text}")
        logging.debug(f"Typing speed: {typing_speed}")
        
        # Add line breaks after comments (//) and semicolons (;)
        formatted_text = text.replace(";", ";\n").replace("//", "\n//")
        
        stop_flag.clear()  # Clear the stop flag before starting typing
        threading.Thread(target=type_text, args=(formatted_text, typing_speed)).start()
        await update.message.reply_text("Text received and typing started.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Command to stop typing
async def stop_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stop_flag.set()  # Set the stop flag to stop typing
    await update.message.reply_text("Typing stopped.")

# Function to simulate typing
def type_text(text, speed):
    delay = 1.0 / speed
    logging.debug(f"Typing text: {text} with delay: {delay}")
    for char in text:
        if stop_flag.is_set():
            logging.debug("Stop flag set. Breaking typing loop.")
            break
        if char == '\n':
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        elif char == '\r':
            continue
        else:
            keyboard.type(char)
        time.sleep(delay)

# Main function to initialize and run the bot
def main():
    # Initialize the bot
    application = Application.builder().token("YOUR_TOKEN_NIGGA").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("select", select_device))
    application.add_handler(CommandHandler("speed", set_speed))
    application.add_handler(CommandHandler("text", send_text))
    application.add_handler(CommandHandler("stop", stop_typing))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
