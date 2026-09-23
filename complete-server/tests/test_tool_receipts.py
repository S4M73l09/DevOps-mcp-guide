from copy import deepcopy
from pathlib import Path
import shutil


import pytest
from mcp import Client


from security.receipt import verify_receipt
from server import mcp, signing_provider


ROOT = Path(__file__).resolve().parents[1]



def assert_valid_receipt(result) -> dict[str, object]:
    content = result.structured_content


    assert content["ok"] is True
    assert "receipt" in content


    receipt = content["receipt"]


    assert verify_receipt(
        receipt,
        signing_provider.public_key,
    ) is True


    return receipt


@pytest.mark.anyio
async def test_terraform_plan_generates_receipt(tmp_path) -> None:
    source = ROOT / "fixtures/terraform/basic"
    terraform_fixture = tmp_path / "terraform-basic"


    shutil.copytree(source, terraform_fixture)


    async with Client(mcp) as client:
        result = await client.call_tool(
            "terraform_plan",
            {
                "path": str(terraform_fixture),
                "include_receipt": True,
                "actor": "integration-test",
            },
        )

    receipt = assert_valid_receipt(result)


    assert receipt["action"] == "terraform_plan"
    assert receipt["target"] == str(terraform_fixture)


@pytest.mark.anyio
async def test_docker_compose_images_generates_receipt() -> None:
    compose_file = (
        ROOT
        / "fixtures/docker/compose/Db-Observ-compose.yaml"
    )


    async with Client(mcp) as client:
        result = await client.call_tool(
            "docker_compose_images",
            {
                "compose_file": str(compose_file),
                "include_receipt": True,
                "actor": "integration-test",
            },
        )

    receipt = assert_valid_receipt(result)


    assert receipt["action"] == "docker_compose_images"
    assert receipt["target"] == str(compose_file)


@pytest.mark.anyio
async def test_kubernetes_manifest_generates_receipt() -> None:
    overlay = (
        ROOT
        / "fixtures/kubernetes/overlays/development"
    )

    async with Client(mcp) as client:
        result = await client.call_tool(
            "kubernetes_validate_manifest",
            {
                "path": str(overlay),
                "include_receipt": True,
                "actor": "integration-test",
            },
        )

    receipt = assert_valid_receipt(result)


    assert receipt["action"] == "kubernetes_validate_manifest"
    assert receipt["target"] == str(overlay)


@pytest.mark.anyio
async def test_receipt_can_be_disabled() -> None:
    compose_file = (
        ROOT
        / "fixtures/docker/compose/Db-Observ-compose.yaml"
    )


    async with Client(mcp) as client:
        result = await client.call_tool(
            "docker_compose_images",
            {
                "compose_file": str(compose_file),
                "include_receipt": False,
                "actor": "integration-test",
            },
        )


    content = result.structured_content


    assert content["ok"] is True
    assert "receipt" not in content



@pytest.mark.anyio
async def test_modified_tool_receipt_is_rejected() -> None:
    compose_file = (
        ROOT
        / "fixtures/docker/compose/Db-Observ-compose.yaml"
    )


    async with Client(mcp) as client:
        result = await client.call_tool(
            "docker_compose_images",
            {
                "compose_file": str(compose_file),
                "include_receipt": True,
                "actor": "integration-test",
            },
        )


    receipt = assert_valid_receipt(result)
    tampered_receipt = deepcopy(receipt)
    tampered_receipt["target"] = "different-target"


    assert verify_receipt(
        tampered_receipt,
        signing_provider.public_key,
    ) is False