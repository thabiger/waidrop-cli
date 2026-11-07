"""Private env file parsing, permissions and updates."""

from __future__ import annotations

import os
import stat

import pytest

from waidrop_cli.env_file import (
    default_env_path,
    load_env_file,
    parse_env_text,
    read_env_file_unchecked,
    write_env_file,
)
from waidrop_cli.errors import UsageError

KEY = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="


def test_parse_env_text_ignores_comments_and_non_waidrop_keys():
    text = "\n".join(
        [
            "# comment",
            "",
            "WAIDROP_KEY=abc",
            "export WAIDROP_ACCOUNT=work",
            'WAIDROP_QUOTED="value with spaces"',
            "WAIDROP_WITH_EQUALS=a=b",
            "PYTHONPATH=/tmp/evil",
        ]
    )

    values = parse_env_text(text)

    assert values == {
        "WAIDROP_KEY": "abc",
        "WAIDROP_ACCOUNT": "work",
        "WAIDROP_QUOTED": "value with spaces",
        "WAIDROP_WITH_EQUALS": "a=b",
    }


@pytest.mark.skipif(os.name == "nt", reason="POSIX permissions")
def test_write_env_file_creates_private_file_and_directory(tmp_path):
    path = tmp_path / "waidrop" / "env"

    write_env_file(path, key=KEY, account="primary")

    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert path.read_text(encoding="utf-8").splitlines() == [
        "# WAiDrop CLI environment; keep this file private (chmod 600).",
        f"WAIDROP_KEY={KEY}",
        "WAIDROP_ACCOUNT=primary",
    ]
    assert load_env_file(path) == {"WAIDROP_KEY": KEY, "WAIDROP_ACCOUNT": "primary"}


def test_write_env_file_preserves_unrelated_entries(tmp_path):
    path = tmp_path / "env"
    path.write_text(
        "\n".join(
            [
                "# keep this comment",
                "WAIDROP_FOLDER=/archive",
                "WAIDROP_KEY=old-key",
                "export WAIDROP_ACCOUNT=old-account",
                "PYTHONPATH=/tmp/evil",
                "",
            ]
        ),
        encoding="utf-8",
    )

    write_env_file(path, key=KEY, account="work")

    text = path.read_text(encoding="utf-8")
    assert "# keep this comment" in text
    assert "WAIDROP_FOLDER=/archive" in text
    assert "PYTHONPATH=/tmp/evil" in text
    assert text.count("WAIDROP_KEY=") == 1
    assert text.count("WAIDROP_ACCOUNT=") == 1
    assert text.endswith("\n")


@pytest.mark.skipif(os.name == "nt", reason="POSIX permissions")
def test_write_env_file_repairs_insecure_mode(tmp_path):
    path = tmp_path / "env"
    path.write_text("WAIDROP_KEY=old\n", encoding="utf-8")
    path.chmod(0o644)

    write_env_file(path, key=KEY, account="primary")

    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert load_env_file(path)["WAIDROP_KEY"] == KEY


@pytest.mark.skipif(os.name == "nt", reason="POSIX permissions")
def test_read_env_file_unchecked_ignores_insecure_mode(tmp_path):
    path = tmp_path / "env"
    path.write_text("WAIDROP_KEY=abc\n", encoding="utf-8")
    path.chmod(0o644)

    assert read_env_file_unchecked(path) == {"WAIDROP_KEY": "abc"}
    with pytest.raises(UsageError, match="must not be readable or writable"):
        load_env_file(path)


def test_default_env_path_uses_credentials_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("WAIDROP_CREDENTIALS", str(tmp_path / "credentials.json"))

    assert default_env_path() == tmp_path / "env"
