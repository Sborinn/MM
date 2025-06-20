# Stay_Alive.py
from flask import Flask
from threading import Thread
import os

app = Flask(__name__) # Use Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # Use the PORT environment variable provided by Render, default to 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) # Ensure it listens on 0.0.0.0 and the correct port

def keep_alive():
    t = Thread(target=run)
    t.start()
