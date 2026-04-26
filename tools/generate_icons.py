# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pillow>=12.2.0",
# ]
# ///

import os
from PIL import Image

def generate_icons():
    img_path = "..\\vscode-extension\\logo.png"
    if not os.path.exists(img_path):
        print(f"Error: {img_path} not found")
        return

    img = Image.open(img_path)

    # 1. Generate Windows ICO
    ico_path = "dist/sindlish.ico"
    os.makedirs("dist", exist_ok=True)
    img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Created {ico_path}")

    # 2. Generate Inno Setup BMPs
    wizard_img = img.resize((164, 314), Image.Resampling.LANCZOS)
    wizard_img.save("dist/wizard.bmp")
    small_img = img.resize((55, 55), Image.Resampling.LANCZOS)
    small_img.save("dist/wizard_small.bmp")

    # 3. Generate macOS ICNS
    icns_path = "dist/sindlish.icns"
    img.save(icns_path, format='ICNS')
    print(f"Created {icns_path}")

    # 4. Generate Linux PNG (High Res)
    linux_png = "dist/sindlish_icon.png"
    img.resize((512, 512), Image.Resampling.LANCZOS).save(linux_png)
    print(f"Created {linux_png}")

if __name__ == "__main__":
    generate_icons()
