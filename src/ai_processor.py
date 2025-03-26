import os
import logging
import base64
import io
import time
from pathlib import Path
from pdf2image import convert_from_path
import anthropic
import config

logger = logging.getLogger(__name__)

def process_document(pdf_path):
    """
    Process a document using Anthropic Claude API to extract important tax information

    Args:
        pdf_path: Path to the PDF file

    Returns:
        dict: Extracted document data
    """
    try:
        # Convert PDF to image with retries
        logger.info(f"Converting PDF to image: {pdf_path}")
        images = None
        pdf_conversion_retries = 3

        for attempt in range(pdf_conversion_retries):
            try:
                images = convert_from_path(pdf_path, first_page=1, last_page=1)
                break
            except Exception as e:
                if attempt < pdf_conversion_retries - 1:
                    logger.warning(f"PDF conversion failed (attempt {attempt+1}/{pdf_conversion_retries}). Retrying: {str(e)}")
                    time.sleep(1)
                else:
                    logger.error(f"PDF conversion failed after {pdf_conversion_retries} attempts")
                    raise

        # Encode image to base64
        buffered = io.BytesIO()
        images[0].save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Initialize Anthropic client
        client = anthropic.Anthropic()

        # Prepare prompt for document analysis
        prompt = """
        Please analyze this financial document and extract the following information:

        1. Document type (e.g., W-2, 1099-INT, 1099-R, Investment Statement, Account Summary, etc.)
        2. Statement period or tax year
        3. Financial institution name (if applicable)
        4. Account number (last 4 digits or masked, if applicable)

        Format your response exactly as follows, with each item on a new line:
        Document type: [type]
        Period/Year: [period]
        Institution: [name]
        Account number: [number]
        """

        logger.info(f"Sending document to Anthropic Claude for analysis: {pdf_path}")

        # Call Anthropic Claude API with error handling
        response = None
        for attempt in range(config.API_MAX_RETRIES):
            try:
                response = client.messages.create(
                    model=config.ANTHROPIC_MODEL,
                    max_tokens=config.MAX_TOKENS,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": image_base64
                                    }
                                }
                            ]
                        }
                    ]
                )
                break
            except Exception as api_error:
                if attempt < config.API_MAX_RETRIES - 1:
                    # Calculate backoff time (1s, 2s, 4s...)
                    backoff = 2 ** attempt
                    logger.warning(f"API call failed (attempt {attempt+1}/{config.API_MAX_RETRIES}). Retrying in {backoff}s: {str(api_error)}")
                    time.sleep(backoff)
                else:
                    logger.error(f"API call failed after {config.API_MAX_RETRIES} attempts")
                    raise

        # Extract text from response
        extracted_text = response.content[0].text
        logger.info(f"Received Claude response for {pdf_path}")

        # Parse the extracted text
        document_data = parse_ai_response(extracted_text)
        logger.info(f"Extracted data: {document_data}")

        return document_data

    except Exception as e:
        logger.error(f"Error processing document {pdf_path}: {str(e)}")
        raise

def parse_ai_response(text):
    """
    Parse the AI response into a structured dictionary

    Args:
        text: Text response from Claude

    Returns:
        dict: Structured document data
    """
    data = {
        'document_type': '',
        'period_year': '',
        'institution': '',
        'account_number': '',
        'raw_ai_response': text  # Store the raw response for debugging
    }

    # Parse line by line
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Extract document type
        if "document type:" in line.lower():
            data['document_type'] = line.split(":", 1)[1].strip()

        # Extract period/year
        elif "period" in line.lower() or "year" in line.lower():
            data['period_year'] = line.split(":", 1)[1].strip()

        # Extract institution
        elif "institution" in line.lower() or "payer" in line.lower():
            data['institution'] = line.split(":", 1)[1].strip()

        # Extract account number
        elif "account number" in line.lower():
            data['account_number'] = line.split(":", 1)[1].strip()

    return data

