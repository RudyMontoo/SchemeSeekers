import requests
import wave
import struct

# Create dummy audio file (silence)
with wave.open("dummy.wav", "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(16000)
    for _ in range(16000): # 1 second of silence
        f.writeframes(struct.pack('h', 0))

print("Testing /voice/models")
print(requests.get("http://127.0.0.1:8000/voice/models").json())

print("Testing /voice/transcribe")
with open("dummy.wav", "rb") as f:
    resp = requests.post("http://127.0.0.1:8000/voice/transcribe", files={"file": f})
    print(resp.json())
