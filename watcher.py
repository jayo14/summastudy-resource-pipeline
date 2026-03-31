import time
import logging
import sys
import shutil
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from classifier import classify
from uploader import upload_to_summa

# Configuration
WATCH_FOLDER = Path.home() / "SummaIncoming"
PROCESSED_FOLDER = Path.home() / "SummaProcessed"
LOG_FILE = Path(__file__).parent / "pipeline.log"
SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

# Ensure folders exist
WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("watcher")

class SummaHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            self.process(event.src_path)

    def process(self, file_path):
        path = Path(file_path)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return

        logger.info(f"Detected: {path.name}")
        time.sleep(2) # Prevent reading incomplete writes

        try:
            # 1. Classify
            course = classify(str(path))
            
            # 2. Rename format: <COURSE>*RESOURCE*<TIMESTAMP>.pdf
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{course}*RESOURCE*{timestamp}.pdf"
            processed_path = PROCESSED_FOLDER / new_filename

            # 3. Upload
            if upload_to_summa(str(path), course=course):
                # 4. Move
                shutil.move(str(path), str(processed_path))
                logger.info(f"Moved to processed: {new_filename}")
            else:
                logger.error(f"Failed to upload {path.name}")

        except Exception as e:
            logger.error(f"Error handling {path.name}: {str(e)}")

def run():
    observer = Observer()
    observer.schedule(SummaHandler(), str(WATCH_FOLDER), recursive=False)
    logger.info(f"Watching: {WATCH_FOLDER}")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    run()

# Assumptions:
# - Renaming to .pdf is mandatory even for images per prompt spec.
# - Log location is pipeline.log in project root.
