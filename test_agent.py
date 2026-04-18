import requests

print("Testing /agent/start")
resp = requests.post("http://127.0.0.1:8000/agent/start")
data = resp.json()
print("Start Response:", data)
session_id = data.get("session_id")

print("\nTesting /agent/answer")
if session_id:
    ans_resp = requests.post("http://127.0.0.1:8000/agent/answer", json={"session_id": session_id, "answer": "I am 30 years old from Rajasthan"})
    print("Answer Response:", ans_resp.json())

print("\nTesting /agent/checklist")
chk_resp = requests.get("http://127.0.0.1:8000/agent/checklist?query=kisan")
print("Checklist Response:", chk_resp.json())

