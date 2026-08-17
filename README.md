# cursor-chat-export-to-markdown

A lightweight open-source Python tool for exporting Cursor Chat and Composer conversations from Cursor's local database to standard Markdown files.

The project is designed to improve **developer data portability**: conversations created during AI-assisted development can be archived, searched, migrated, versioned, and reused outside a proprietary IDE.

## Features

- Export Cursor Chat and Composer conversations to Markdown
- List locally stored conversations before exporting
- Batch export conversation history
- Preserve AI-assisted development history in an open, portable text format
- Simple Python implementation with no dependency on Cursor cloud APIs
- Windows helper scripts included
- Database locations documented for Windows, macOS, and Linux
- Maintained across Cursor storage-format changes

## Why this project exists

AI coding conversations increasingly contain useful development context: design decisions, debugging history, implementation ideas, and explanations that may not exist anywhere else in a project.

Cursor stores these conversations locally, but they are not naturally portable. This tool converts that data into Markdown so developers can keep their own long-term archive and reuse it with search tools, knowledge bases, version-control workflows, or other AI systems.

## Usage

### Windows

List all conversations:

```bash
python cursor2md.py --list --db-path "%APPDATA%\Cursor\User\globalStorage\state.vscdb"
```

Export all conversations:

```bash
python cursor2md.py --output ".\markdown_output" --db-path "%APPDATA%\Cursor\User\globalStorage\state.vscdb"
```

You can also run the included Windows helper scripts directly:

- `list_cursor_data.bat`
- `export_cursor_data.bat`

## Database locations

Cursor's local database location differs by platform:

- Windows: `%APPDATA%/Cursor/User/globalStorage/state.vscdb`
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`
- Linux: `~/.config/Cursor/User/workspaceStorage/state.vscdb`

The included helper scripts target Windows. On other platforms, pass the appropriate database path to `cursor2md.py`.

## Cursor version compatibility

The project has been updated as Cursor's local conversation storage format has changed.

- Cursor 0.49: support added for the revised conversation data format.
- Cursor 1.7.54: support added for the newer data structure. Exported filename prefixes now use the conversation end time, for example `202510210800_`, instead of the earlier numeric prefix such as `001_`.

Because Cursor's internal storage format is not a stable public API, future Cursor releases may require additional compatibility updates. If an export stops working after a Cursor update, please open an issue with the Cursor version and relevant error information.

## Acknowledgements

Thanks to M6ZeroG for the Go implementation that inspired this Python version:

https://github.com/M6ZeroG/cursor2md

## License

This project is released under the MIT License. See `LICENSE` for details.
