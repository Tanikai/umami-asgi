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
    # currently not used -> asdict() outputs "None" if not set, has to be prevented if this field is used
    # data: Optional[dict] = None


@dataclass
class UmamiRequest:
    payload: UmamiPayload
    type: str = "event"  # currently the only type available
