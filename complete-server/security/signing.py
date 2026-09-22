import base64
import hashlib
import os
from abc import ABC, abstractmethod
from pathlib import Path


from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)



class SigningProvider(ABC):
    """Provider responsible for loading and exposing signing keys."""


    @property
    @abstractmethod
    def private_key(self) -> Ed25519PrivateKey:
        ...

    @property
    def public_key(self) -> Ed25519PublicKey:
        return self.private_key.public_key()

    @property
    def key_id(self) -> str:
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return hashlib.sha256(public_bytes).hexdigest()[:16]


class EphemeralSigningProvider(SigningProvider):
    """Generate a new key every time the server starts."""


    def __init__(self) -> None:
        self._private_key = Ed25519PrivateKey.generate()


    @property
    def private_key(self) -> Ed25519PrivateKey:
        return self._private_key


class LocalSigningProvider(SigningProvider):
    """Load or create a private key in a local file."""


    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._private_key = self._load_or_create_key()


    @property
    def private_key(self) -> Ed25519PrivateKey:
        return self._private_key


    def _load_or_create_key(self) -> Ed25519PrivateKey:
        if self.path.exists():
            key_data = self.path.read_bytes()
            return serialization.load_pem_private_key(
                key_data,
                password=None,
            )


        self.path.parent.mkdir(parents=True, exist_ok=True)


        private_key = Ed25519PrivateKey.generate()
        key_data = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )


        self.path.write_bytes(key_data)
        self.path.chmod(0o600)


        return private_key


class ProductionSigningProvider(SigningProvider):
    """
    Demonstration adapter for a production provider.

    
    A real implementation should call a KMS, HSM, or a secret manager.
    """


    def __init__(self) -> None:
        encoded_key = os.environ.get("MCP_SIGNING_PRIVATE_KEY_B64")


        if not encoded_key:
            raise RuntimeError(
                "MCP_SIGNING_PRIVATE_KEY_B64 is required in production mode."

            )


        key_data = base64.b64decode(encoded_key)
        self._private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
        )


    @property
    def private_key(self) -> Ed25519PrivateKey:
        return self._private_key


def get_signing_provider(
    mode: str = "ephemeral",
    key_path: str = "keys/dev-signing-key.pem",
) -> SigningProvider:
    selected_mode = mode.lower()


    if selected_mode == "ephemeral":
        return EphemeralSigningProvider()

    if selected_mode == "local":
        return LocalSigningProvider(key_path)

    if selected_mode == "production":
        return ProductionSigningProvider()


    raise RuntimeError(
        f"Unsupported MCP_SIGNING_MODE: {selected_mode}"
    )
