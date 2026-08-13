import ipaddress
import socket
from urllib.parse import urlparse

from ..errors import UnsafeEndpointError


BLOCKED_HOSTS = {"169.254.169.254", "metadata.google.internal"}


def validate_endpoint(url: str, *, allow_local: bool = False) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ({"https"} | ({"http"} if allow_local else set())):
        raise UnsafeEndpointError("custom endpoint must use HTTPS")
    if not parsed.hostname or parsed.username or parsed.password:
        raise UnsafeEndpointError("endpoint host is invalid")
    host = parsed.hostname.lower().rstrip(".")
    if host in BLOCKED_HOSTS:
        raise UnsafeEndpointError("metadata endpoints are forbidden")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or 443)}
    except socket.gaierror as exc:
        raise UnsafeEndpointError("endpoint host cannot be resolved") from exc
    for raw in addresses:
        ip = ipaddress.ip_address(raw)
        if not allow_local and (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved):
            raise UnsafeEndpointError("private and local endpoints are forbidden")
        if allow_local and not (ip.is_loopback or ip.is_private):
            raise UnsafeEndpointError("Ollama endpoint must be local or explicitly private")
    return url.rstrip("/")

