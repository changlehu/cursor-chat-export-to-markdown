# cursor-chat-export-to-markdown

一个轻量的开源 Python 工具，用于从 Cursor 本地数据库中导出 Chat 和 Composer 对话，并保存为标准 Markdown 文件。

本项目的主要目的不仅是“导出聊天记录”，而是改善 **AI 编程数据的可移植性**：让开发者能够将 AI 辅助编程过程中产生的对话长期归档、搜索、迁移、版本化，并在 Cursor 之外继续使用。

## 主要功能

- 导出 Cursor Chat 和 Composer 对话为 Markdown
- 导出前列出本地保存的全部对话
- 批量导出对话历史
- 使用开放、便于长期保存的文本格式保留 AI 辅助开发记录
- Python 实现，不依赖 Cursor 云端 API
- 提供 Windows 辅助脚本
- 提供 Windows、macOS 和 Linux 的数据库位置说明
- 持续适配 Cursor 本地数据格式变化

## 为什么开发这个工具

AI 编程对话中往往保存着大量有价值的开发上下文，例如设计决策、调试过程、实现思路以及代码解释，而这些内容未必会出现在项目的其他文件中。

Cursor 会在本地保存这些对话，但这些数据并不是天然可移植的。本工具将其转换为 Markdown，使开发者能够掌握自己的 AI 编程历史，并进一步用于全文搜索、知识库、版本管理工作流，或者交给其他 AI 工具继续处理。

## 使用方法

### Windows

列出所有对话：

```bash
python cursor2md.py --list --db-path "%APPDATA%\Cursor\User\globalStorage\state.vscdb"
```

导出所有对话到 `markdown_output` 目录：

```bash
python cursor2md.py --output ".\markdown_output" --db-path "%APPDATA%\Cursor\User\globalStorage\state.vscdb"
```

Windows 系统也可以直接运行项目附带的两个辅助脚本：

- `list_cursor_data.bat`
- `export_cursor_data.bat`

## Cursor 数据库位置

不同系统中 Cursor 本地数据库的位置如下：

- Windows: `%APPDATA%/Cursor/User/globalStorage/state.vscdb`
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`
- Linux: `~/.config/Cursor/User/workspaceStorage/state.vscdb`

项目附带的辅助脚本主要面向 Windows。其他平台可以直接给 `cursor2md.py` 指定相应的数据库路径。

## Cursor 版本兼容

本项目会根据 Cursor 本地对话存储格式的变化进行适配。

- Cursor 0.49：已适配新版对话数据格式。
- Cursor 1.7.54：已适配新的数据结构。导出文件名前缀改为使用对话结束时间，例如 `202510210800_`，不再使用早期的 `001_` 数字前缀。

由于 Cursor 的内部存储格式并不是稳定的公开 API，未来 Cursor 升级后仍可能需要继续适配。如果 Cursor 更新后出现无法导出的情况，可以提交 Issue，并注明 Cursor 版本及相关错误信息。

## 感谢

感谢 M6ZeroG 的 Go 版本实现，本项目的 Python 版本受其启发：

https://github.com/M6ZeroG/cursor2md

## 开源许可

本项目采用 MIT License，详见 `LICENSE` 文件。
