import os
from PIL import Image
import json

class ImageHelper:
    @staticmethod
    def generate_mac_icon(image_path: str) -> None:
        """
        Generate 12 sizes of Apple Icon Set from the given image and create a JSON file with the icon details.

        Parameters:
        image_path (str): The path to the source image.
        """
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        icon_details = []

        # Create the output directory if it doesn't exist
        output_dir = os.path.expanduser("~/Desktop/instant/img/output/Assets.xcassets/AppIcon.appiconset/")
        os.makedirs(output_dir, exist_ok=True)

        # Open the source image
        with Image.open(image_path) as img:
            for size in sizes:
                for scale in [1, 2]:
                    scaled_size = size * scale
                    filename = f"{scaled_size}-mac.png"
                    img_resized = img.resize((scaled_size, scaled_size), Image.LANCZOS)
                    img_resized.save(os.path.join(output_dir, filename))

                    icon_details.append({
                        "size": f"{size}x{size}",
                        "expected-size": str(scaled_size),
                        "filename": filename,
                        "folder": 'Assets.xcassets/AppIcon.appiconset/',
                        "idiom": "mac" if size < 1024 else "ios-marketing",
                        "scale": f"{scale}x"
                    })

        # Write the JSON file
        json_data = {"images": icon_details}
        with open(os.path.join(output_dir, "Contents.json"), "w") as json_file:
            json.dump(json_data, json_file, indent=4)