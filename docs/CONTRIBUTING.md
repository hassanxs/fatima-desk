# Contributing to Fatima Desk

Thanks for helping. Bug reports, ideas and pull requests are all welcome.

## Reporting a problem

Open an [issue](https://github.com/hassanxs/fatima-desk/issues) and include:

- your platform and version (Windows 11, macOS 14 on Intel, Linux Mint 22, Android 14, ...),
- what you did, what you expected and what happened,
- the log if you can: on Windows `%APPDATA%\FatimaDesk\log`, on Linux
  `~/.local/share/logs/FatimaDesk`, on macOS `~/Library/Logs/FatimaDesk`.

Please don't post passwords, device IDs you want to keep private, or anything
else sensitive. Security problems go through [SECURITY](SECURITY.md) instead.

## Pull requests

- Work on the `fatima-desk` branch and keep each pull request to one change.
- Keep changes small and close to the existing code; Fatima Desk follows
  RustDesk's structure so upstream fixes can still be merged.
- Add a test when you fix a bug in Rust code, and make sure the build still
  passes (see *Building* in the [README](../README.md)).
- Write commit messages that say what changed and why.

By contributing you agree that your contribution is licensed under the
[GNU AGPL v3.0](../LICENCE), like the rest of the project.

Changes that aren't specific to Fatima Desk may be better sent to
[RustDesk](https://github.com/rustdesk/rustdesk), which Fatima Desk is based on.
