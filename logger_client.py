import requests

def send_log(level, message):
    try:
        requests.post("http://localhost:4000/log", json={
            "level": level,
            "message": message
        }, timeout=1)
    except:
        pass   # Avoid crashing if log server is offline
