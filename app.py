from fastapi import FastAPI, UploadFile, File, Response, Header, HTTPException
import subprocess
import tempfile
import os
import uvicorn

app = FastAPI()

@app.post("/converter")
async def converter_audio(file: UploadFile = File(...), x_api_key: str = Header(None)):
    # Puxa a senha definida no Easypanel (se não tiver lá, a senha padrão será 'minha-senha-secreta')
    expected_api_key = os.getenv("API_KEY", "minha-senha-secreta")
    
    if x_api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Acesso negado. Chave da API (x-api-key) invalida ou ausente.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(await file.read())
        temp_video_path = temp_video.name
        
    temp_audio_path = temp_video_path.replace(".mp4", ".mp3")
    
    try:
        comando = [
            "ffmpeg", "-y", "-i", temp_video_path,
            "-vn", "-ar", "16000", "-ac", "1", "-b:a", "32k",
            temp_audio_path
        ]
        subprocess.run(comando, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        with open(temp_audio_path, "rb") as f:
            audio_data = f.read()
            
        return Response(content=audio_data, media_type="audio/mpeg")
        
    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
