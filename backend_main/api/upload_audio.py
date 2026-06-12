# from fastapi import APIRouter, UploadFile, File, HTTPException
# import os
# import subprocess
# import requests
# from fastapi import APIRouter

# router = APIRouter()

# @router.post("/")
# async def upload_audio(
#     audio: UploadFile = File(...)
# ):
#     try:
#         if not audio:
#             raise HTTPException(
#             status_code=400,
#             detail="No audio uploaded"
#             )

#         os.makedirs("temp", exist_ok=True)
    
#         webm_path = os.path.join(
#             "temp",
#             audio.filename
#         )
    
#         # Save uploaded webm file
#         with open(webm_path, "wb") as f:
#             f.write(await audio.read())
    
#         wav_path = webm_path.replace(".webm", ".wav")
    
#         # Convert webm → wav
#         subprocess.run(
#             [
#                 "ffmpeg",
#                 "-y",
#                 "-i",
#                 webm_path,
#                 wav_path
#             ],
#             check=True
#         )
    
#         # Send WAV file to transcription API
#         with open(wav_path, "rb") as f:
#             files = {
#                 "audio": (
#                     os.path.basename(wav_path),
#                     f,
#                     "audio/wav"
#                 )
#             }
#             print("sending converted audio file")
#             response = requests.post(
#                 "http://127.0.0.1:8000/audio/transcribe",
#                 files=files
#             )
#             print("resturnig response")
#             print(response.json())
#             return {
#                 "success": True,
#                 "transcription_response": response.json()
#             }
#     except Exception as e:

#         return {
#             "success": False,
#             "error": str(e)
#         }
#     finally:
#         # Delete temp files
#         if webm_path and os.path.exists(webm_path):
#             os.remove(webm_path)

#         if wav_path and os.path.exists(wav_path):
#             os.remove(wav_path)