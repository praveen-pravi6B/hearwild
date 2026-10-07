import subprocess
import tempfile
from pathlib import Path

import httpx
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import birdnet

from database import (
    add_discovery,
    get_flock,
    init_db,
)

app = FastAPI(title="HearWild API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MODEL = birdnet.load(
    "acoustic",
    "3.0",
    "onnx",
)


init_db()


@app.get("/health")
async def health():
    return {
        "status": "ok",
    }


async def get_bird_info(scientific_name: str):
    """
    Get a short bird description and image from Wikimedia Commons.
    """

    url = "https://commons.wikimedia.org/w/api.php"

    headers = {
        "User-Agent": (
            "HearWild/1.0 "
            "(open-source bird companion; "
            "https://github.com/praveen-pravi6B/hearwild)"
        ),
        "Accept": "application/json",
    }

    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": scientific_name,
        "gsrnamespace": 6,
        "gsrlimit": 1,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 960,
    }

    image_url = None
    description = None

    try:
        async with httpx.AsyncClient(
            timeout=10,
            headers=headers,
        ) as client:

            response = await client.get(
                url,
                params=params,
            )

            response.raise_for_status()

            data = response.json()

            pages = data.get("query", {}).get("pages", {})

            for page in pages.values():
                image_info = page.get("imageinfo", [{}])[0]

                image_url = (
                    image_info.get("thumburl")
                    or image_info.get("url")
                )

                metadata = image_info.get(
                    "extmetadata",
                    {},
                )

                description_value = metadata.get(
                    "ImageDescription"
                )

                if description_value:
                    description = (
                        description_value.get("value")
                        or ""
                    )

                break

    except Exception:
        pass

    return {
        "image_url": image_url,
        "description": clean_description(description),
    }


def clean_description(description):
    """
    Keep the flock description short and remove HTML.
    """

    if not description:
        return None

    import re

    description = re.sub(
        r"<[^>]+>",
        "",
        description,
    )

    description = re.sub(
        r"\s+",
        " ",
        description,
    ).strip()

    if not description:
        return None

    sentences = re.split(
        r"(?<=[.!?])\s+",
        description,
    )

    short_description = " ".join(
        sentences[:2]
    ).strip()

    if len(short_description) > 220:
        short_description = (
            short_description[:217].rsplit(
                " ",
                1,
            )[0]
            + "..."
        )

    return short_description


@app.get("/flock")
async def flock():
    """
    Return the user's flock.

    Existing birds without an image or description are
    backfilled from Wikimedia.
    """

    current_flock = get_flock()

    for bird in current_flock["birds"]:

        if (
            bird.get("image_url")
            and bird.get("description")
        ):
            continue

        info = await get_bird_info(
            bird["scientific_name"]
        )

        if not info["image_url"] and not info["description"]:
            continue

        from database import (
            update_bird_image,
            update_bird_description,
        )

        if (
            not bird.get("image_url")
            and info["image_url"]
        ):
            update_bird_image(
                bird["common_name"],
                info["image_url"],
            )

        if (
            not bird.get("description")
            and info["description"]
        ):
            update_bird_description(
                bird["common_name"],
                info["description"],
            )

    return get_flock()


async def convert_to_wav(
    input_path: str,
    output_path: str,
):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-ar",
            "48000",
            "-ac",
            "1",
            output_path,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def parse_species_name(species_name: str):
    """
    BirdNET returns species names in a form similar to:

        Strix aluco_Tawny Owl

    Convert that into:

        scientific name
        common name
    """

    if "_" in species_name:
        scientific_name, common_name = (
            species_name.split("_", 1)
        )
    else:
        scientific_name = species_name
        common_name = species_name

    return (
        common_name.strip(),
        scientific_name.strip(),
    )


@app.post("/identify")
async def identify(
    file: UploadFile = File(...),
):
    suffix = Path(
        file.filename or "recording.webm"
    ).suffix or ".webm"

    with tempfile.TemporaryDirectory() as temp_dir:

        input_path = (
            Path(temp_dir)
            / f"input{suffix}"
        )

        wav_path = (
            Path(temp_dir)
            / "audio.wav"
        )

        audio = await file.read()

        input_path.write_bytes(audio)

        try:
            await convert_to_wav(
                str(input_path),
                str(wav_path),
            )

            predictions = MODEL.predict(
                str(wav_path),
                n_workers=1,
                batch_size=1,
            )

            dataframe = predictions.to_dataframe()

        except Exception as error:
            return {
                "species": None,
                "scientific_name": None,
                "confidence": 0,
                "added_to_flock": False,
                "error": str(error),
            }

    if dataframe.empty:
        return {
            "species": None,
            "scientific_name": None,
            "confidence": 0,
            "added_to_flock": False,
        }

    best_prediction = dataframe.iloc[
        dataframe["confidence"].idxmax()
    ]

    species_name = str(
        best_prediction["species_name"]
    )

    confidence = float(
        best_prediction["confidence"]
    )

    common_name, scientific_name = (
        parse_species_name(species_name)
    )

    # Very low confidence.
    if confidence < 0.20:
        return {
            "species": common_name,
            "scientific_name": scientific_name,
            "confidence": confidence,
            "added_to_flock": False,
        }

    # Possible identification.
    if confidence < 0.70:
        return {
            "species": common_name,
            "scientific_name": scientific_name,
            "confidence": confidence,
            "added_to_flock": False,
        }

    # Confident identification.
    bird_info = await get_bird_info(
        scientific_name
    )

    flock = add_discovery(
        common_name=common_name,
        scientific_name=scientific_name,
        image_url=bird_info["image_url"],
        description=bird_info["description"],
    )

    return {
        "species": common_name,
        "scientific_name": scientific_name,
        "description": bird_info["description"],
        "confidence": confidence,
        "added_to_flock": True,
        "new_discovery": flock["new_discovery"],
        "xp_earned": flock["xp_earned"],
        "total_xp": flock["total_xp"],
        "level": flock["level"],
        "bird_xp": flock["bird_xp"],
        "times_identified": flock["times_identified"],
        "image_url": bird_info["image_url"],
    }
