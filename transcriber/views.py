import os
import requests
from django.shortcuts import render
from .forms import UploadForm
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-tiny"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def index(request):
    transcription = None
    telugu_translation = None
    error_message = None

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            media_file = request.FILES['media_file']
            media_dir = 'media'
            os.makedirs(media_dir, exist_ok=True)

            file_path = os.path.join(media_dir, media_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in media_file.chunks():
                    destination.write(chunk)

            try:
                with open(file_path, "rb") as f:
                    response = requests.post(API_URL, headers=HEADERS, data=f)
                    data = response.json()
                    transcription = data.get("text", "No transcription returned.")

                # Translate to Telugu
                try:
                    telugu_translation = GoogleTranslator(
                        source='auto', target='te'
                    ).translate(transcription)
                except Exception as e:
                    telugu_translation = f"Translation error: {e}"

                # Delete file to save space
                os.remove(file_path)

            except Exception as e:
                error_message = f"Transcription error: {e}"
    else:
        form = UploadForm()

    return render(request, 'transcriber/index.html', {
        'form': form,
        'transcription': transcription,
        'translation': telugu_translation,
        'error_message': error_message,
    })
