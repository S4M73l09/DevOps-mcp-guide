import base64
import hashlib
import json
from typing import Any


from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)



def canonical_json(value: Any) -> bytes:
    """Serialize data deterministically before hashing or signing."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")



def content_hash(value: Any) -> str:
    """Return a SHA-256 hash for structured data."""
    return hashlib.sha256(canonical_json(value)).hexdigest()


def create_receipt(
    *,
    action: str,
    target: str,
    actor: str,
    environment: str,
    input_data: Any,
    output_data: Any,
    private_key: Ed25519PrivateKey,
    key_id: str | None = None,
) -> dict[str, Any]:
    """Create a signed receipt for a simulated action."""
    payload = {
        "action": action,
        "actor": actor,
        "environment": environment,
        "target": target,
        "input_hash": content_hash(input_data),
        "output_hash": content_hash(output_data),
    }

    if key_id is not None:
        payload["key_id"] = key_id


    signature = private_key.sign(canonical_json(payload))


    return {
        **payload,
        "signature": base64.b64encode(signature).decode("ascii"),

    }


def verify_receipt(
    receipt: dict[str, Any],
    public_key: Ed25519PublicKey,
) -> bool:
    """Verify the signature of a receipt."""
    signature_text = receipt.get("signature")


    if not isinstance(signature_text, str):
        return False

    
    payload = {
        key: value
        for key, value in receipt.items()
        if key != "signature"
    }


    try:
        signature = base64.b64decode(signature_text)
        public_key.verify(signature, canonical_json(payload))
    except Exception:
        return False


    return True
