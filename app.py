from flask import Flask, request, render_template_string
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Завантажте аудіофайл для транскрибування 👇</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
            }
            .container {
                max-width: 600px;
                margin: auto;
            }
            .upload {
                background: #f4f4f4;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .upload h2 {
                margin-top: 0;
            }
            .custom-file-input {
                display: none;
            }
            .custom-file-label {
                margin-bottom: 10px;
                display: inline-block;
                padding: 6px 12px;
                cursor: pointer;
            }
        </style>
        <script>
            function updateFileName() {
                var input = document.getElementById('fileInput');
                var label = document.getElementById('fileLabel');
                label.textContent = input.files.length > 0 ? input.files[0].name : 'Вибрати файл';
            }
        </script>
      </head>
      <body>
        <div class="container">
          <div class="upload">
            <h2>Завантажте аудіофайл для транскрибування 👇</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
              <label class="custom-file-label" id="fileLabel" for="fileInput">Вибрати файл</label>
              <input type="file" name="file" id="fileInput" class="custom-file-input" accept="audio/*" onchange="updateFileName()">
              <button type="submit">Транскрибувати запис 🤖</button>
            </form>
          </div>
        </div>
      </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Створюємо директорію, якщо не існує
            file.save(filepath)
            print("Step 1: File uploaded successfully")
            
            # Відкриваємо завантажений аудіофайл
            with open(filepath, "rb") as audio_file:
                print("Step 2: Audio file opened successfully")
                
                # Відправляємо запит на створення транскрипції
                transcription_response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
                print("Step 3: Transcription response received")
            
            # Витягуємо текстовий вміст з відповіді
            response_text = transcription_response
            print("Step 4: Transcription text extracted")
            
            # Розподіл тексту по ролях
            def split_roles(transcription):
                print("Step 5: Splitting transcription text into roles")
                roles = ["Співрозмовник", "Респондент"]
                result = []
                lines = transcription.split(". ")
                for i, line in enumerate(lines):
                    role = roles[i % 2]  # Змінюємо роль для кожної другої репліки
                    time_stamp = f"{i//3600:02}:{(i%3600)//60:02}:{i%60:02}"  # Форматування часу
                    result.append(f"<b>{role} ({time_stamp}):</b> {line.strip()}")
                print("Step 6: Roles split completed")
                return "<br>".join(result)
            
            formatted_transcription = split_roles(response_text)
            
            # HTML шаблон для виводу результатів
            html_template = """
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <title>Transcription Result</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 40px;
                    }
                    .container {
                        max-width: 600px;
                        margin: auto;
                    }
                    .transcription {
                        background: #f4f4f4;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
                    .transcription h2 {
                        margin-top: 0;
                    }
                </style>
              </head>
              <body>
                <div class="container">
                  <div class="transcription">
                    <h2>Transcription Result</h2>
                    <p>{{ transcription_text | safe }}</p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            print("Step 7: Rendering HTML template")
            return render_template_string(html_template, transcription_text=formatted_transcription)
    except Exception as e:
        print(f"Error encountered: {e}")
        return render_template_string("<p>Error: {{ error }}</p>", error=str(e))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
