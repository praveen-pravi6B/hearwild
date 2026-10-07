from pathlib import Path
import subprocess

import birdnet
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TouchGrass API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

print("Loading BirdNET V3 ONNX...")

model = birdnet.load(
    "acoustic",
    "3.0",
    "onnx",
)

print("BirdNET loaded!")


@app.get("/")
def root():
    return {
        "name": "TouchGrass API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post("/identify")
async def identify(file: UploadFile = File(...)):
    webm_file = UPLOAD_DIR / "input.webm"
    wav_file = UPLOAD_DIR / "input.wav"

    contents = await file.read()
    webm_file.write_bytes(contents)

    print(f"Received: {file.filename}")
    print(f"Size: {len(contents)} bytes")

    # Convert browser WebM/Opus → WAV
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(webm_file),
            "-ar",
            "48000",
            "-ac",
            "1",
            str(wav_file),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    print("Audio converted to WAV")

    # Run BirdNET
    predictions = model.predict(
        str(wav_file),
        n_workers=1,
        batch_size=1,
    )

    df = predictions.to_dataframe()

    # BirdNET may return no predictions for silence,
    # background noise, or an unrecognizable recording.
    if df.empty:
        print("No bird prediction returned")

        return {
            "bird": None,
            "scientific_name": None,
            "confidence": 0.0,
            "confidence_level": "unknown",
            "message": (
                "We couldn't identify a bird in this recording."
            ),
        }

    best_prediction = df.loc[df["confidence"].idxmax()]

    species = best_prediction["species_name"]
    confidence = float(best_prediction["confidence"])

    if "_" in species:
        scientific_name, common_name = species.split("_", 1)
    else:
        scientific_name = species
        common_name = species

    if confidence >= 0.70:
        confidence_level = "confident"
    elif confidence >= 0.40:
        confidence_level = "possible"
    else:
        confidence_level = "unknown"

    return {
        "bird": common_name,
        "scientific_name": scientific_name,
        "confidence": confidence,
        "confidence_level": confidence_level,
    }
