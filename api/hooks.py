import logging
import json

SENSITIVE_HEADERS = {"authorization", "proxy-authorization", "cookie", "set-cookie"}
SENSITIVE_BODY_KEYS = {"access_token", "refresh_token", "password", "secret"}


logger = logging.getLogger(__name__)

def truncate(text: str, limit: int) -> str:
    return text if len(text) < limit else f"{text[:limit]}[trancated...]"


def mask_headers(headers: dict) -> dict:
    return {k: "***" if k.lower() in SENSITIVE_HEADERS else v for k, v in headers.items()}


def mask_body(body):
    if not body: return body

    try:
        data = json.loads(body)
    except(TypeError, json.JSONDecodeError, UnicodeDecodeError):
        return body

    if isinstance(data, dict):
        return {k: "***" if k.lower() in SENSITIVE_BODY_KEYS else v for k, v in data.items()}
    return data

def request_response_logger(response, *args, **kwargs):
    request = response.request
    logger.info(
            "ЗАПРОС:::%s %s | header=%s | body=%s",
            request.method,
            request.url,
            mask_headers(request.headers),
            mask_body(request.body)
            )

    logger.info(
            "ОТВЕТ:::%s | headers=%s | body=%s",
            response.status_code,
            mask_headers(response.headers),
            truncate(str(mask_body(response.text)), 300)
            )

    return response
