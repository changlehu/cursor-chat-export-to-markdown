# cursor-chat-export-to-markdown
Export cursor chat and composer data to markdown. Python version.

## Thanks

Go version:

https://github.com/M6ZeroG/cursor2md

## Usage (in windows)

List all conversations：

python cursor2md.py --list --db-path "%APPDATA%\Cursor\User\globalStorage\state.vscdb"

Export all conversations:

python cursor2md.py --output ".\markdown_output" --db-path "%APPDATA%\Cursor\User\globalStorage\state.vscdb"

You can run bat file directly: list_cursor_data.bat or export_cursor_data.bat

## Other platforms:

Please write your own script by different db path.

* Windows: %APPDATA%/Cursor/User/globalStorage/state.vscdb
* macOS: ~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
* Linux: ~/.config/Cursor/User/workspaceStorage/state.vscdb

## New version support:

Support new version 0.49. It can export old and new chat data at the same time.
