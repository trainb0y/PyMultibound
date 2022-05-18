import logging, os, platform

# This is imported into paths.py, and is therefore the first thing ran on startup

logging.basicConfig(
    format="%(asctime)s: %(levelname)s - %(module)s - %(funcName)s: %(message)s",
    level=logging.DEBUG,
    filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), "PyMultibound.log"),
    filemode="w"
)

VERSION = "v1.1.0"
logging.info(f"PyMultibound Version: {VERSION}, Platform: {platform.system()}")