from PIL import Image
import sys
import os

def resize_image(input_path, output_path, target_size):
    try:
        print("Opening the image...")
        with Image.open(input_path) as img:
            print("Image opened successfully.")

            print("Resizing the image...")
            img.thumbnail(target_size)

            print("Saving the resized image...")
            img.save(output_path)

            print(f"Image resized successfully and saved to {output_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check if the correct number of command-line arguments are provided
    if len(sys.argv) != 5:
        print("Usage: python resize_image.py input_image_path output_image_path target_width target_height")
        sys.exit(1)

    # Get command-line arguments
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    target_width = int(sys.argv[3])
    target_height = int(sys.argv[4])

    # Define the target size as a tuple (width, height)
    target_size = (target_width, target_height)

    # Perform the image resizing
    print("Starting image resizing process...")
    resize_image(input_path, output_path, target_size)
