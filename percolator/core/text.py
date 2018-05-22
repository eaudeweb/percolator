from uuid import uuid4
from percolator.conf import settings

import requests

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

    tika_data = tika_response.json()
    try:
        content = tika_data[0]['X-TIKA:content'].strip()
    except (IndexError, AttributeError):
        raise TextExtractionError
    except KeyError:  # Tika could not detect any text content
        return ''

    return content
