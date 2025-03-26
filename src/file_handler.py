import os
import shutil
import time
from pathlib import Path
import logging
import config
from src.utils import save_metadata, clean_filename

logger = logging.getLogger(__name__)

def get_source_documents():
    """Get all PDF files from source directory"""
    return list(config.SOURCE_DIR.glob('*.pdf'))

def safe_copy_file(source, destination, max_retries=config.COPY_MAX_RETRIES):
    """Copy a file with retries"""
    for attempt in range(max_retries):
        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"File copy failed (attempt {attempt+1}/{max_retries}). Retrying: {str(e)}")
                time.sleep(1)  # Wait before retry
            else:
                logger.error(f"File copy failed after {max_retries} attempts")
                raise Exception(f"Failed to copy file after {max_retries} attempts: {str(e)}")

# Modify the organize_document function in file_handler.py

def organize_document(pdf_path, document_data, client_name):
    """
    Organize a document based on extracted data using client name

    Args:
        pdf_path: Path to the source PDF file
        document_data: Dictionary with extracted document data
        client_name: Client name provided by user

    Returns:
        dict: Processing result
    """
    try:
        # Extract key fields with fallbacks for missing data
        doc_type = document_data.get('document_type', 'unknown')
        period = document_data.get('period_year', 'unknown')
        institution = document_data.get('institution', 'unknown')

        # Clean up names for filesystem use
        from src.utils import clean_filename
        client_clean = clean_filename(client_name)
        doc_type_clean = clean_filename(doc_type)

        # Create directory structure: processed/[ClientName]/
        client_dir = config.PROCESSED_DIR / client_clean
        client_dir.mkdir(parents=True, exist_ok=True)

        # Create new filename: [ClientName]_[DocType]_[Period].pdf
        new_filename = f"{client_clean}_{doc_type_clean}_{period}.pdf"
        dest_path = client_dir / new_filename

        # Copy the file
        safe_copy_file(pdf_path, dest_path)
        logger.info(f"Organized document: {pdf_path} → {dest_path}")

        # Create metadata file
        metadata_path = dest_path.with_suffix('.json')

        # Add client name to metadata
        document_data['client_name'] = client_name
        save_metadata(metadata_path, document_data)

        return {
            'success': True,
            'original_path': str(pdf_path),
            'new_path': str(dest_path),
            'metadata': document_data
        }

    except Exception as e:
        logger.error(f"Error organizing file {pdf_path}: {str(e)}")
        return {
            'success': False,
            'original_path': str(pdf_path),
            'error': str(e)
        }

