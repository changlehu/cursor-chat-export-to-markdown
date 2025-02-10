用python导出cursor的chat和composor为markdown文件。

## 感谢

Go版本脚本作者 M6ZeroG

https://github.com/M6ZeroG/cursor2md

脚本内容是把cursormd.go上传给kimi，让AI依照原代码改成python版本，写作完成的，调试后修了一些错误。

顺便说一下网页版的 kimi/qwen/deepseek 在写这类代码的能力上 >chatGPT/mistral/gemini，也不用迷信deepseek，kimi的网页版编程能力同样非常强大。

https://kimi.moonshot.cn

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