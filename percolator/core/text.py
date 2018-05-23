from uuid import uuid4
import tempfile
import shutil
import json
import requests

from percolator.conf import settings


from .exceptions import TextExtractionError, TextExtractionTimeout


def extract_text(file):
    headers = {
        'Accept': 'application/json',
        'Content-Disposition': f'attachment; filename={uuid4()}',
    }

    try:
        tika_response = requests.put(
            f'{settings.TIKA_URL}/rmeta/text',
            data=file,
            headers=headers,
            verify=False,
            timeout=settings.TIKA_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        raise TextExtractionTimeout

    try:
        tika_data = tika_response.json()
        content = tika_data[0]['X-TIKA:content'].strip()
    except (IndexError, AttributeError):  # Tika could not extract any text
        raise TextExtractionError
    except json.decoder.JSONDecodeError:  # Tika's response was not valid JSON
        return ''
    except KeyError:  # Tika could not detect any text content
        return ''

    return content


def extract_text_from_url(url):
    """
    Streams the content from an URL into a temporary file, and sends it to Tika
    for text extraction.
    """
    with tempfile.TemporaryFile() as f:
        with requests.get(url, stream=True) as r:
            shutil.copyfileobj(r.raw, f)
        f.seek(0)
        return extract_text(f)
