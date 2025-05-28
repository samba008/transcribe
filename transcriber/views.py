import os
from django.shortcuts import render
from .forms import UploadForm
import whisperx
import torch
from deep_translator import GoogleTranslator

# Your Hugging Face Token
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


# replace with your token

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
                # Load WhisperX model
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model = whisperx.load_model("large-v2", device)

                # Transcribe audio
                result = model.transcribe(file_path)

                # Align whisper output
                model_a, metadata = whisperx.load_align_model(
                    language_code=result["language"], device=device
                )
                result = whisperx.align(
                    result["segments"], model_a, metadata,
                    file_path, device, return_char_alignments=False
                )

                # Speaker diarization
                diarize_model = whisperx.DiarizationPipeline(
                    use_auth_token=HF_TOKEN, device=device
                )
                diarize_segments = diarize_model(file_path)

                # Assign speakers to segments
                result = whisperx.assign_word_speakers(diarize_segments, result)

                # Build transcription with speaker labels
                transcription = ""
                for segment in result["segments"]:
                    speaker = segment.get("speaker", "Speaker")
                    text = segment["text"]
                    transcription += f"[{speaker}]: {text}\n"

                # Translate to Telugu
                try:
                    telugu_translation = GoogleTranslator(
                        source='auto', target='te'
                    ).translate(transcription)
                except Exception as e:
                    telugu_translation = f"Translation error: {e}"

            except Exception as e:
                error_message = str(e)

    else:
        form = UploadForm()

    return render(request, 'transcriber/index.html', {
        'form': form,
        'transcription': transcription,
        'translation': telugu_translation,
        'error_message': error_message,
    })
