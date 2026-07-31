import json
import base64
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

from app.core.config import settings

def load_private_key() -> ed25519.Ed25519PrivateKey:
    if not settings.LICENSE_PRIVATE_KEY:
        raise ValueError("LICENSE_PRIVATE_KEY is not set in environment")
    
    # Strip quotes if they exist from the .env loading
    # Replace escaped newlines if they were loaded weirdly, but usually standard PEM formatting is enough
    key_str = settings.LICENSE_PRIVATE_KEY.strip('"').strip("'")
    if "\\n" in key_str:
        key_str = key_str.replace("\\n", "\n")
        
    key_data = key_str.encode('utf-8')
    
    return serialization.load_pem_private_key(
        key_data,
        password=None
    )

def load_public_key(public_key_pem: str) -> ed25519.Ed25519PublicKey:
    return serialization.load_pem_public_key(public_key_pem.encode('utf-8'))

def canonicalize_payload(payload: Dict[str, Any]) -> bytes:
    """
    Canonicalize the JSON payload for signing exactly as WFA expects:
    json.dumps(payload, separators=(",",":"), sort_keys=True)
    """
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

def sign_payload(payload: Dict[str, Any]) -> Tuple[bytes, str]:
    """
    Takes a payload dictionary, canonicalizes it, signs it using the Ed25519 private key,
    and returns the canonicalized payload bytes and the base64 encoded signature.
    """
    private_key = load_private_key()
    canonical_json = canonicalize_payload(payload)
    
    signature = private_key.sign(canonical_json)
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    
    return canonical_json, signature_b64

def verify_payload(payload: Dict[str, Any], signature_b64: str, public_key_pem: str) -> bool:
    """
    Verify the payload matches the given signature.
    Useful for testing.
    """
    try:
        public_key = load_public_key(public_key_pem)
        canonical_json = canonicalize_payload(payload)
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, canonical_json)
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False
