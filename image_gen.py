import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import random

if __name__ == "__main__":
    # CONFIG
    excel_path = "test.xlsx"
    background_folder = "backgrounds"  # folder with images
    output_folder = "generated_realistic"

    os.makedirs(output_folder, exist_ok=True)

    # Load Excel
    df = pd.read_excel(excel_path)

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        font = ImageFont.load_default()

    # Get background images
    backgrounds = [f for f in os.listdir(background_folder) if f.endswith((".jpg", ".png"))]

    for i, row in df.iterrows():
        student_no = str(row["student_no"])

        # Pick random background
        bg_path = os.path.join(background_folder, random.choice(backgrounds))
        img = Image.open(bg_path).convert("RGB")

        draw = ImageDraw.Draw(img)

        # Position (bottom area)
        width, height = img.size
        x = random.randint(int(width * 0.2), int(width * 0.6))
        y = int(height * 0.85)

        # Add background strip (like real photos)
        draw.rectangle(
            [(0, height - 100), (width, height)],
            fill=(255, 255, 255)
        )

        # Draw text
        print(f"Drawing text: {student_no} - area: {x}, {y}")
        draw.text((x-width/4, y + 100), student_no, fill="black", font=font,)


        # Add slight rotation
        # img = img.rotate(random.uniform(-2, 2), expand=False)

        # Add slight blur (optional realism)
        if random.random() < 0.3:
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

        # Save
        img.save(f"{output_folder}/{student_no}.jpg")

    print("Realistic test images generated!")