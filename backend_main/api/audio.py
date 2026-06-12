# api/audio.py

import os
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException

from services.sarvam_service import speech_to_text
from services.audio_file_conversion_service import convert_webm_to_wav
router = APIRouter()


# @router.post("/transcribe")
# async def transcribe_audio(
#     audio: UploadFile = File(...)
# ):

#     try:
#         print("API GOT A HIT")
#         suffix = os.path.splitext(audio.filename)[1]

#         with tempfile.NamedTemporaryFile(
#             delete=False,
#             suffix=suffix
#         ) as temp_file:

#             temp_file.write(await audio.read())
#             temp_path = temp_file.name

#         transcript = speech_to_text(temp_path)

#         os.remove(temp_path)

#         return {
#             "transcript": transcript
#         }

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )





import uuid

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...)
):
    webm_path = None
    wav_path = None
    try:
        
        os.makedirs("temp", exist_ok=True)

        file_id = str(uuid.uuid4())

        webm_path = os.path.join(
            "temp",
            f"{file_id}.webm"
        )

        with open(webm_path, "wb") as f:
            f.write(await audio.read())


        wav_path = os.path.join(
            "temp",
            f"{file_id}.wav"
        )

        # Convert WEBM → WAV
        convert_webm_to_wav(
            webm_path,
            wav_path
        )


        # Convert WAV → Text
        transcript = speech_to_text(wav_path)

        return {
            "success": True,
            "transcript": transcript
        }

        
    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        # Delete temp files
        if webm_path and os.path.exists(webm_path):
            os.remove(webm_path)

        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)