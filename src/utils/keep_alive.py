from flask import Flask
from threading import Thread

#Leave this, it is to keep bot online
#This keeps the discord bot online

app = Flask('')

@app.route('/')
def home():
  return "Hello, I am alive!"

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
  t = Thread(target=run)
  t.start()

