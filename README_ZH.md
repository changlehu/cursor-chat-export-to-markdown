用python导出cursor的chat和composor为markdown文件。

## 感谢

Go版本脚本作者 M6ZeroG

https://github.com/M6ZeroG/cursor2md

## 功能用法（windows系统示例）

列出所有对话：

python cursor2md.py --list --db-path "%APPDATA%\Cursor\User\globalStorage\state.vscdb"

导出所有对话到markdown_output目录:

python cursor2md.py --output ".\markdown_output" --db-path "%APPDATA%\Cursor\User\globalStorage\state.vscdb"

在windows系统里你也可以直接运行这两个脚本 list_cursor_data.bat 或 export_cursor_data.bat

cursor数据库在不同系统中的位置如下：

* Windows: %APPDATA%/Cursor/User/globalStorage/state.vscdb
* macOS: ~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
* Linux: ~/.config/Cursor/User/workspaceStorage/state.vscdb

## 新版支持

1.7.54 版本的对话数据已支持，目前导出名称前缀为结束时间。
