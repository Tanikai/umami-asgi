from dataclasses import dataclass
from typing import Optional


@dataclass
class UmamiPayload:
    """Dataclass for the payload of an Umami request. See https://umami.is/docs/api/sending-stats"""
    hostname: str
    language: str
    referrer: str
    screen: str
    title: str
    url: str
    website: str
    name: str
    data: Optional[dict] = None
