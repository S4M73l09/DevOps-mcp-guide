import base64
from copy import deepcopy
from typing import Any

import pytest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


from security.receipt import create_receipt, verify_receipt
from security.signing import (
    EphemeralSigningProvider,
    LocalSigningProvider,
    ProductionSigningProvider,
    get_signing_provider,
)


def _create_test_receipt(
    provider,
    *,
    action: str,
    target: str,
    input_data: Any,
    output_data: Any,
) -> dict[str, object]:
    return create_receipt(
        action=action,
        target=target,
        actor="test-user",
        environment="development",
        input_data=input_data,
        output_data=output_data,
        private_key=provider.private_key,
        key_id=provider.key_id,
    )


RECEIPT_CASES = [
    {
        "action": "terraform_plan",
        "target": "fixtures/terraform/basic",
        "input_data": {
            "path": "fixtures/terraform/basic",
        },
        "output_data": {
            "ok": True,
            "status": "plan_completed",
        },
    },
    {
        "action": "docker_compose_images",
        "target": "fixtures/docker/compose/Db-Observ-compose.yaml",
        "input_data": {
            "compose_file": (
                "fixtures/docker/compose/Db-Observ-compose.yaml"
            ),
        },
        "output_data": {
            "ok": True,
            "status": "images_found",
            "count": 4,
        },
    },
    {
        "action": "kubernetes_validate_manifest",
        "target": "fixtures/kubernetes/overlays/development",
        "input_data": {
            "path": "fixtures/kubernetes/overlays/development",
        },
        "output_data": {
            "ok": True,
            "status": "manifest_valid",
        },
    },
]


@pytest.mark.parametrize("case", RECEIPT_CASES)
def test_valid_receipts_are_accepted(case) -> None:
    provider = EphemeralSigningProvider()

    receipt = _create_test_receipt(provider, **case)

    assert verify_receipt(
        receipt,
        provider.public_key,
    ) is True


@pytest.mark.parametrize("case", RECEIPT_CASES)
def test_tampered_receipts_are_rejected(case) -> None:
    provider = EphemeralSigningProvider()

    receipt = _create_test_receipt(provider, **case)
    tampered_receipt = deepcopy(receipt)
    tampered_receipt["target"] = "different-target"


    assert verify_receipt(
        tampered_receipt,
        provider.public_key,
    ) is False


def test_local_provider_persists_the_same_key(tmp_path) -> None:
    key_path = tmp_path / "dev-signing-key.pem"


    first_provider = LocalSigningProvider(str(key_path))
    second_provider = LocalSigningProvider(str(key_path))


    assert key_path.exists()
    assert first_provider.key_id == second_provider.key_id


    receipt = _create_test_receipt(
        first_provider,
        **RECEIPT_CASES[0],
    )


    assert verify_receipt(
        receipt,
        second_provider.public_key,
    ) is True


def test_ephemeral_providers_use_different_keys() -> None:
    first_provider = get_signing_provider("ephemeral")
    second_provider = get_signing_provider("ephemeral")


    assert isinstance(first_provider, EphemeralSigningProvider)
    assert isinstance(second_provider, EphemeralSigningProvider)
    assert first_provider.key_id != second_provider.key_id


def test_local_provider_is_selected(tmp_path) -> None:
    key_path = tmp_path / "local-signing-key.pem"


    provider = get_signing_provider(
        mode="local",
        key_path=str(key_path),
    )


    assert isinstance(provider, LocalSigningProvider)
    assert key_path.exists()


def test_production_provider_is_selected(monkeypatch) -> None:
    private_key = Ed25519PrivateKey.generate()


    key_data = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


    encoded_key = base64.b64encode(key_data).decode("ascii")


    monkeypatch.setenv(
        "MCP_SIGNING_PRIVATE_KEY_B64",
        encoded_key,
    )


    provider = get_signing_provider("production")


    assert isinstance(provider, ProductionSigningProvider)
    assert provider.key_id
