"""Crypto contract tests (shared vector with the extension's JS tests)."""

from __future__ import annotations

import pytest
from cryptography.exceptions import InvalidTag

from waidrop_cli.crypto import (
    chat_hash,
    decrypt_media,
    decrypt_text,
    derive_keys,
    derive_media_key,
    encrypt_media,
    is_valid_key,
    media_hash,
)

KEY = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="
ENVELOPE = bytes.fromhex(
    "5741415201000102030405060708090a0b2109e73aa5a338c3a33a3b2e2f3ec1b69f67ed340a8f63ae39807c464f"
)
MEDIA_PATH = "chat=8e59af6366e6c4aa/dt=2026-10-17/media-00112233445566778899aabbccddeeff.enc"
MEDIA_ENVELOPE = bytes.fromhex(
    "57414d5201000102030405060708090a0b6b80213e9b6eb042879d701327849c3fb0940883987c5986dfa8a5"
)


def test_known_answer_vector():
    hash_key, enc_key = derive_keys(KEY)
    assert decrypt_text(enc_key, ENVELOPE) == "hello archive"
    assert chat_hash(hash_key, "49171234567@c.us") == "8e59af6366e6c4aa"


def test_media_known_answer_vector():
    hash_key, _ = derive_keys(KEY)
    assert (
        media_hash(hash_key, "ACE81BE4695181CE094591658F7D7844")
        == "b9b8b4fb8d6daf44d4cd9d39853e9ade"
    )
    media_key = derive_media_key(KEY)
    assert decrypt_media(media_key, MEDIA_PATH, MEDIA_ENVELOPE) == b"hello media"


def test_media_roundtrip_and_path_binding():
    media_key = derive_media_key(KEY)
    encrypted = encrypt_media(media_key, MEDIA_PATH, b"hello media")
    assert decrypt_media(media_key, MEDIA_PATH, encrypted) == b"hello media"
    with pytest.raises(InvalidTag):
        decrypt_media(media_key, MEDIA_PATH + ".x", encrypted)


def test_crypto_roundtrip():
    from waidrop_cli.crypto import encrypt_text

    _, enc_key = derive_keys(KEY)
    encrypted = encrypt_text(enc_key, "some payload")
    assert decrypt_text(enc_key, encrypted) == "some payload"


def test_tampering_fails():
    _, enc_key = derive_keys(KEY)
    tampered = bytearray(ENVELOPE)
    tampered[-1] ^= 0xFF
    with pytest.raises(InvalidTag):
        decrypt_text(enc_key, bytes(tampered))


def test_wrong_key_fails():
    _, other_key = derive_keys("BwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwcHBwc=")
    with pytest.raises(InvalidTag):
        decrypt_text(other_key, ENVELOPE)


def test_key_validation():
    assert is_valid_key(KEY)
    assert not is_valid_key("abc")
    assert not is_valid_key("")
    with pytest.raises(ValueError):
        derive_keys("abc")
