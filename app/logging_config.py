"""Logs em JSON no stdout, com request_id em cada linha."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import TextIO

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

# Atributos padrão do LogRecord; o que não estiver aqui é "extra" e vai para o JSON.
_STANDARD_ATTRS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {
    "message",
    "asctime",
    "taskName",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        for key, value in record.__dict__.items():
            if key not in _STANDARD_ATTRS:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class _StdoutHandler(logging.StreamHandler):  # type: ignore[type-arg]
    """Resolve sys.stdout a cada escrita, para seguir redirecionamentos (ex.: testes)."""

    def __init__(self) -> None:
        super().__init__(sys.stdout)

    @property
    def stream(self) -> TextIO:
        return sys.stdout

    @stream.setter
    def stream(self, _value: object) -> None:
        pass


def configure_logging(level: str = "INFO") -> None:
    handler = _StdoutHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
    # O access log do uvicorn não carrega request_id; o middleware da app o substitui.
    logging.getLogger("uvicorn.access").disabled = True
