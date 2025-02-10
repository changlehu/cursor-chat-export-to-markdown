import os
import json
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

def get_default_db_path():
    appdata = os.getenv("APPDATA")
    return os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb") if appdata else None

class ChatRecord:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.data = json.loads(value)

    def has_valid_content(self):
        valid = (
            len(self.data.get("conversation", [])) > 0
            and self.data.get("name", "").strip() != ""
        )
        if not valid:
            print(f"无效记录: 键: {self.key}, 值: {self.value[:50]}...")
        return valid

    @property
    def name(self):
        return self.data.get("name", "untitled")

    @property
    def conversation(self):
        return self.data.get("conversation", [])

    @property
    def created_at(self):
        return self.data.get("createdAt", 0)

    @property
    def ended_at(self):
        if self.conversation:
            return self.conversation[-1].get("timingInfo", {}).get("clientEndTime", 0)
        return 0

def list_sessions(db_path):
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM cursorDiskKV")
        rows = cursor.fetchall()

        chat_records = []
        for key, value in rows:
            print(f"调试信息 - Key: {key}, Value: {value[:50]}...")  # 添加调试信息
            if key == "inlineDiffsData" or value == "[]":
                continue
            try:
                record = ChatRecord(key, value)
                if record.has_valid_content():
                    chat_records.append(record)
            except json.JSONDecodeError:
                print(f"JSON 解析失败: 键: {key}, 值: {value[:50]}...")
                continue

        for record in chat_records:
            created_time = datetime.fromtimestamp(record.created_at / 1000)
            ended_time = datetime.fromtimestamp(record.ended_at / 1000)
            print(f"Hash: {record.key}\n"
                  f"Title: {record.name}\n"
                  f"Start Time: {created_time}\n"
                  f"End Time: {ended_time}\n"
                  f"---")

def generate_markdown(record):
    md_content = f"# {record.name}\n\n"
    md_content += "## 会话信息\n\n"
    
    created_time = datetime.fromtimestamp(record.created_at / 1000)
    ended_time = datetime.fromtimestamp(record.ended_at / 1000)
    md_content += f"- 开始时间: {created_time}\n"
    md_content += f"- 结束时间: {ended_time}\n"
    
    context_files = record.data.get("context", {}).get("fileSelections", [])
    if context_files:
        md_content += "- 相关文件:\n"
        for file in context_files:
            filename = urlparse(file["uri"]["path"]).path.split("/")[-1]
            md_content += f"- [{filename}]({file['uri']['path']})\n"
    
    for msg in record.conversation:
        msg_type = msg.get("type", 0)
        text = msg.get("text", "")
        selections = msg.get("context", {}).get("selections", [])
        code_blocks = msg.get("codeBlocks", [])
        
        if msg_type == 1:
            md_content += "\n## User\n\n"
            if selections:
                md_content += "引用的文件:\n"
                for sel in selections:
                    filename = urlparse(sel["uri"]["path"]).path.split("/")[-1]
                    md_content += f"- From [{filename}]({sel['uri']['path']}): {sel['text']}\n"
            md_content += f"> {text}\n"
        elif msg_type == 2:
            md_content += "\n## Cursor\n\n"
            md_content += f"{text}\n"
            if code_blocks:
                for block in code_blocks:
                    language = block.get("languageId", "text")
                    uri = block["uri"].get("path", "")
                    filename = urlparse(uri).path.split("/")[-1]
                    code_content = block.get("content", "")
                    md_content += f"\n```{language} [{filename}]({uri})\n"
                    md_content += code_content
                    md_content += "\n```\n"
    
    return md_content

def export_sessions(db_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM cursorDiskKV")
        rows = cursor.fetchall()
        
        chat_records = {}
        for key, value in rows:
            if key.startswith("composerData:") and value.strip() != "[]":
                try:
                    record = ChatRecord(key, value)
                    if record.has_valid_content():
                        chat_records[key.split(":", 1)[1]] = record
                except json.JSONDecodeError:
                    print(f"JSON解析失败: {key}")
                    continue
        
        for index, (hash_key, record) in enumerate(sorted(chat_records.items(), key=lambda x: x[1].created_at, reverse=True)):
            md_content = generate_markdown(record)
            safe_filename = record.name
            safe_filename = safe_filename.replace("<", "_").replace(">", "_").replace(":", "_").replace("/", "_").replace("\\", "_").replace("|", "_").replace("?", "_").replace("*", "_")
            output_file = Path(output_dir) / f"{safe_filename}.md"
            
            # 检查文件是否已存在，如果存在则添加序号
            while output_file.exists():
                output_file = Path(output_dir) / f"{safe_filename}_{index}.md"
                index += 1
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            print(f"已导出: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Cursor 聊天记录导出工具，python版本")
    parser.add_argument("-ls", "--list", action="store_true", help="列出所有会话")
    parser.add_argument("-db", "--db-path", help="数据库文件路径")
    parser.add_argument("-o", "--output", default="markdown_output", help="markdown 文件输出目录")
    args = parser.parse_args()

    db_path = args.db_path if args.db_path else get_default_db_path()

    if args.list:
        list_sessions(db_path)
    else:
        export_sessions(db_path, args.output)

if __name__ == "__main__":
    main()
