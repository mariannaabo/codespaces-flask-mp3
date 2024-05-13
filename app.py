from flask import Flask, jsonify, Response
from dotenv import load_dotenv
from openai import OpenAI
import json
import os

load_dotenv()

app = Flask(__name__)

# SECRET_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI()

@app.route('/')
def index():
    try:
        # Відкриваємо аудіофайл, який розміщений поруч з app.py
        with open("sample.mp3", "rb") as audio_file:
            transcription_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        # Виводимо повну відповідь для аналізу
        # Конвертуємо відповідь у строку JSON з кодуванням UTF-8
        response_text = json.dumps(transcription_response, ensure_ascii=False)
        return Response(response_text, content_type='application/json; charset=utf-8')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
