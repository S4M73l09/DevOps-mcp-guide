from config import load_config


def test_default_configuration(monkeypatch) -> None:
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)
    monkeypatch.delenv("MCP_SIGNING_MODE", raising=False)


    config = load_config()


    assert config.transport == "stdio"
    assert config.signing_mode == "ephemeral"


def test_local_signing_configuration(monkeypatch) -> None:
    monkeypatch.setenv("MCP_SIGNING_MODE", "local")
    monkeypatch.setenv(
        "MCP_SIGNING_KEY_PATH",
        "keys/dev-signing-key.pem",
    )


    config = load_config()


    assert config.signing_mode == "local"
    assert config.signing_key_path == "keys/dev-signing-key.pem"