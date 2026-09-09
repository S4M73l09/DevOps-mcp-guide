from signing import(
    EphemeralSigningProvider,
    LocalSigningProvider,

)


def test_ephemeral_provider_generate_a_key() -> None:
    provider = EphemeralSigningProvider()


    message = b"test-message"
    signature = provider.private_key.sign(message)


    provider.public_key.verify(signature, message)


def test_local_provider_reuses_the_same_key(tmp_path) -> None:
    key_path = tmp_path / "dev-signing-key.pem"


    first_provider = LocalSigningProvider(str(key_path))
    second_provider = LocalSigningProvider(str(key_path))


    message = b"persistent-message"
    signature = first_provider.private_key.sign(message)


    second_provider.public_key.verify(signature, message)



def test_local_key_has_restricted_permissions(tmp_path) -> None:
    key_path = tmp_path / "dev-signing-key.pem"


    LocalSigningProvider(str(key_path))


    permissions = key_path.stat().st_mode & 0o777


    assert permissions == 0o600