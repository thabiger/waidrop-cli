# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-11-07

### Added

- Initial release of `waidrop-cli`, the companion CLI for WAiDrop archives.
- Dropbox OAuth 2.0 authorization using PKCE with offline refresh tokens.
- `auth`, `auth --status`, `auth --status --json` and `auth --revoke` commands.
- `config` command that stores the archive key and account alias in a private
  env file (`0600`; parent `0700`) and keeps unrelated entries.
- `chats`, `query` and `context` commands with name, number, chat-hash and JID
  selectors.
- Date-, hour-, minute- and second-precision windows, plus rolling `--last`
  windows.
- NDJSON, text and CSV output.
- Full-resolution image, sticker and GIF export with an NDJSON manifest.
- Per-chat context chunks with optional context-before and character splitting.
- Optional `mcp` extra and `waidrop-mcp` stdio server with read-only
  `list_chats` and `get_context` tools.
- Automatic loading of the private CLI environment file for `chats`, `query`
  and `context`.
- Private permissions for credentials, output files and exported media.
- Terminal control-character escaping and CSV formula-injection protection.
- Apache-2.0 license and `NOTICE`.

### Changed

- Package, module, command, environment variables and configuration paths use
  the `waidrop` name: `waidrop-cli`, `waidrop_cli`, `waidrop`, `WAIDROP_*`,
  `~/.config/waidrop` and `%APPDATA%\waidrop`.
- Archive format 4 uses layout `waidrop`, media layout `waidrop-media-v1` and
  HKDF salt `waidrop-v1`.
- Credentials default to `~/.config/waidrop/credentials.json`.

### Removed

- Plaintext archive support. Archives must use the encrypted format.
- Backwards compatibility with earlier packages, archives,
  credentials and environment variables.
