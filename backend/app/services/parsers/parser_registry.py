from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ParsedActivationRequest(BaseModel):
    fingerprint: str
    hostname: Optional[str] = None
    username: Optional[str] = None
    os: Optional[str] = None
    os_version: Optional[str] = None
    architecture: Optional[str] = None
    cpu: Optional[str] = None
    ram: Optional[str] = None
    bios: Optional[str] = None
    mac_address: Optional[str] = None
    windows_sid: Optional[str] = None
    current_build: Optional[int] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    
    # Metadata from request
    product_id: Optional[str] = None
    request_type: str = "ACTIVATION"
    hardware_tokens: Optional[Any] = None

class ActivationRequestParser(ABC):
    @abstractmethod
    def can_parse(self, file_content: bytes, filename: str) -> bool:
        pass

    @abstractmethod
    def parse(self, file_content: bytes) -> ParsedActivationRequest:
        pass

class MockWfaParser(ActivationRequestParser):
    def can_parse(self, file_content: bytes, filename: str) -> bool:
        return filename.endswith(".wfareq") or filename.endswith(".json")

    def parse(self, file_content: bytes) -> ParsedActivationRequest:
        import json
        try:
            data = json.loads(file_content.decode('utf-8'))
            return ParsedActivationRequest(
                fingerprint=data.get("fingerprint") or data.get("machine_fingerprint", "MOCK-FINGERPRINT-1234"),
                hostname=data.get("hostname", "MOCK-HOSTNAME"),
                username=data.get("username", "mockuser"),
                os=data.get("os") or data.get("os_info", "Windows"),
                os_version=data.get("os_version", "11"),
                architecture=data.get("architecture", "x64"),
                cpu=data.get("cpu", "Intel Core i7"),
                ram=data.get("ram", "16GB"),
                bios=data.get("bios", "Mock BIOS"),
                mac_address=data.get("mac_address", "00:00:00:00:00:00"),
                windows_sid=data.get("windows_sid", "S-1-5-21-XXX"),
                current_build=data.get("current_build", 100),
                timezone=data.get("timezone", "UTC"),
                locale=data.get("locale", "en-US"),
                product_id=data.get("product_id"),
                request_type=data.get("request_type", "ACTIVATION"),
                hardware_tokens=data.get("hardware_tokens") or data.get("tokens", {})
            )
        except Exception as e:
            # Fallback mock for non-JSON or invalid files
            print("Parser error:", e)
            return ParsedActivationRequest(fingerprint="MOCK-FALLBACK-FINGERPRINT")

class ParserRegistry:
    def __init__(self):
        self._parsers = []

    def register(self, parser: ActivationRequestParser):
        self._parsers.append(parser)

    def get_parser(self, file_content: bytes, filename: str) -> Optional[ActivationRequestParser]:
        for parser in self._parsers:
            if parser.can_parse(file_content, filename):
                return parser
        return None

parser_registry = ParserRegistry()
parser_registry.register(MockWfaParser())
