# api/audio.py

import os
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException

from services.sarvam_service import speech_to_text

router = APIRouter()


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...)
):

    try:

        suffix = os.path.splitext(audio.filename)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file.write(await audio.read())
            temp_path = temp_file.name

        transcript = speech_to_text(temp_path)

        os.remove(temp_path)

        return {
            "transcript": transcript
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )