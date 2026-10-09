from __future__ import annotations

from apx.observability.redaction import (
    deep_redact,
    is_sensitive_key,
    redact_headers,
    redact_string,
)


def test_sensitive_keys_are_redacted_recursively():
    payload = {
        "request": {
            "metadata": [
                {"api_key": "secret-api-key-value", "safe": "ordinary"},
                [{"authorization": "Bearer top-secret-token"}],
            ]
        }
    }

    redacted = deep_redact(payload)
    rendered = str(redacted)

    assert "secret-api-key-value" not in rendered
    assert "Bearer top-secret-token" not in rendered
    assert "ordinary" in rendered
    assert "*" in rendered


def test_sensitive_patterns_inside_nested_strings_are_redacted():
    email = "finance@example.com"
    bearer = "Bearer abcdef123456"
    payload = {"events": [[f"contact={email}"], {"message": bearer}]}

    redacted = deep_redact(payload)
    rendered = str(redacted)

    assert email not in rendered
    assert bearer not in rendered
    assert "contact=" in rendered


def test_sensitive_headers_are_redacted():
    headers = {
        "Authorization": "Bearer abcdef123456",
        "X-API-Key": "key-value-that-must-not-leak",
        "Accept": "application/json",
    }

    redacted = redact_headers(headers)

    assert redacted["Authorization"] != headers["Authorization"]
    assert redacted["X-API-Key"] != headers["X-API-Key"]
    assert redacted["Accept"] == "application/json"


def test_sensitive_key_matching_does_not_match_plural_tokens():
    assert is_sensitive_key("access_token")
    assert is_sensitive_key("X-API-Key")
    assert not is_sensitive_key("tokens")


def test_string_redaction_masks_common_identifiers():
    message = "user=finance@example.com ssn=123-45-6789"
    redacted = redact_string(message)

    assert "finance@example.com" not in redacted
    assert "123-45-6789" not in redacted
