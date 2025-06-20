from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def index():
  # Use RENDER_EXTERNAL_URL if available, otherwise a generic message
  # RENDER_EXTERNAL_URL is set automatically by Render for web services.
  render_url = os.environ.get('RENDER_EXTERNAL_URL', 'Your Render service URL (not set as env var)')
  return f"Bot is Alive! Render Service URL: {render_url}"

def run():
  # Use the PORT environment variable provided by Render.
  # Render automatically sets the 'PORT' env var for web services.
  port = int(os.environ.get('PORT', 8080)) # Default to 8080 for local testing
  app.run(host='0.0.0.0', port=port)

def keep_alive():
  t = Thread(target=run)
  t.start()

# IMPORTANT: Remove this line `keep_alive()` from here in Stay_Alive.py
# It should only be called once, from main.py, as your Render Start Command
# will run main.py, and main.py will then initiate both the Telegram bot
# and the Flask web server.
# If you keep this here, it might cause issues or unnecessary threads.
