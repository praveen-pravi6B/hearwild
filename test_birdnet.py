import sys
import birdnet


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_birdnet.py <audio-file>")
        print("Example: python test_birdnet.py bird_test.ogg")
        sys.exit(1)

    audio_file = sys.argv[1]

    print(f"Audio file: {audio_file}")
    print("Loading BirdNET V3 ONNX...")

    model = birdnet.load(
        "acoustic",
        "3.0",
        "onnx",
    )

    print("Model loaded successfully!")
    print("Running prediction...")

    predictions = model.predict(
        audio_file,
        n_workers=1,
        batch_size=1,
    )

    df = predictions.to_dataframe()

    # Get the highest-confidence prediction
    best_prediction = df.loc[df["confidence"].idxmax()]

    species = best_prediction["species_name"]
    confidence = float(best_prediction["confidence"])

    # BirdNET format:
    # Scientific name_Common name
    if "_" in species:
        scientific_name, common_name = species.split("_", 1)
    else:
        scientific_name = species
        common_name = species

    # TouchGrass confidence handling
    if confidence >= 0.70:
        confidence_level = "confident"
        challenge = (
            "Put your phone away and listen for another bird for 2 minutes."
        )
    elif confidence >= 0.40:
        confidence_level = "possible"
        challenge = (
            "Take a closer listen. You might have heard this bird."
        )
    else:
        confidence_level = "unknown"
        challenge = (
            "Put your phone away and listen carefully for another bird."
        )

    print("\n" + "=" * 40)
    print("TOUCHGRASS RESULT")
    print("=" * 40)

    print(f"Bird:          {common_name}")
    print(f"Scientific:    {scientific_name}")
    print(f"Confidence:    {confidence:.1%}")
    print(f"Confidence:    {confidence_level}")
    print(
        f"Time:          {best_prediction['start_time']:.1f}s - "
        f"{best_prediction['end_time']:.1f}s"
    )
    print(f"Challenge:     {challenge}")

    print("=" * 40)


if __name__ == "__main__":
    main()
