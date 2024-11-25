import sys
from pathlib import Path


class AppConfig:
    if getattr(sys, "frozen", False):
        # this is for when the app is packaged with pyinstaller
        BASE_PATH = Path(sys.executable).parent
    else:
        BASE_PATH = Path(__file__).parent

    RESOURCES = BASE_PATH.parent / "resources"

    IMAGES = RESOURCES / "images"

    HAZARD_IMAGES = IMAGES / "hazard_diamonds"

    SOFAB_LOGO = IMAGES / "sofab_logo.png"

    FLAME = IMAGES / "Flame.png"

    OUTPUT_DIR = BASE_PATH / "outputs"
