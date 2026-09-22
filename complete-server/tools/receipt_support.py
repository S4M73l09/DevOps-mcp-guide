from typing import Any


from security.receipt import create_receipt
from security.signing import SigningProvider


def attach_signed_receipt(
    response: dict[str, object],
    *,
    include_receipt: bool,
    action: str,
    target: str,
    actor: str,
    environment: str,
    input_data: Any,
    signing_provider: SigningProvider,
) -> dict[str, object]:
    """Attach a signed receipt to a successful tool response."""
    if not include_receipt:
        return response


    receipt = create_receipt(
        action=action,
        target=target,
        actor=actor,
        environment=environment,
        input_data=input_data,
        output_data=response,
        private_key=signing_provider.private_key,
        key_id=signing_provider.key_id,
    )


    return {
        **response,
        "receipt": receipt,
    }