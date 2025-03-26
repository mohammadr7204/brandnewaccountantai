import logging
import json
from datetime import datetime
import re
from pathlib import Path
import time
import config

def setup_logging():
    """Set up logging configuration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = config.LOG_DIR / f"processing_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)

def save_metadata(path, data, max_retries=config.COPY_MAX_RETRIES):
    """Save metadata to JSON file with retries"""
    for attempt in range(max_retries):
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
            else:
                raise Exception(f"Failed to save metadata after {max_retries} attempts: {str(e)}")

def clean_filename(text):
    """Convert text to a clean filename"""
    if not text:
        return "unknown"

    # Replace spaces with underscores but preserve name format
    # Remove common suffixes like Jr., Sr., III, etc.
    text = re.sub(r'\s+(Jr\.?|Sr\.?|I{1,3}|IV|V)$', '', text)

    # Replace spaces with underscores
    cleaned = text.replace(' ', '_')

    # Remove special characters but keep apostrophes in names
    cleaned = re.sub(r'[^\w\'\-]', '', cleaned)

    # Replace multiple underscores with a single one
    cleaned = re.sub(r'_+', '_', cleaned)

    return cleaned

def save_checkpoint(processed_files):
    """Save checkpoint of processed files"""
    checkpoint_path = config.LOG_DIR / "processing_checkpoint.json"
    with open(checkpoint_path, 'w') as f:
        json.dump(processed_files, f)

def load_checkpoint():
    """Load checkpoint of processed files"""
    checkpoint_path = config.LOG_DIR / "processing_checkpoint.json"
    if checkpoint_path.exists():
        with open(checkpoint_path, 'r') as f:
            return json.load(f)
    return []

def save_failed_list(failed_docs):
    """Save list of failed documents"""
    if not failed_docs:
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    failed_path = config.LOG_DIR / f"failed_docs_{timestamp}.log"
    with open(failed_path, 'w') as f:
        f.write('\n'.join(failed_docs))
    return failed_path
