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
        try:
            self.data = json.loads(value)
            # Handle new data structure with _v field, 仅当存在嵌套 data 时才解包
            if isinstance(self.data, dict) and "_v" in self.data and "data" in self.data:
                self.data = self.data.get("data", {})
            # Handle checkpoint data
            if "files" in self.data:
                self.data = {"context": {"fileSelections": self.data.get("files", [])}}
        except json.JSONDecodeError:
            self.data = {}

    def has_valid_content(self):
        # 检查对话内容是否实际有效
        conversation = self.data.get("conversation", [])
        if not conversation and isinstance(self.data, dict):
            conversation = self.data.get("messages", [])
        
        # 检查对话内容是否为空或只有空白字符
        has_valid_messages = False
        for msg in conversation:
            text = msg.get("text", "").strip()
            if text:
                has_valid_messages = True
                break
        
        # 修改：时间戳检查，仅当存在 timestamp 时才校验，否则跳过
        created_at = self.created_at
        ended_at = self.ended_at
        if created_at > 0 and ended_at > 0:
            valid_timestamps = ended_at >= created_at
        else:
            valid_timestamps = True
        
        # 检查文件名是否存在
        files = self.data.get("context", {}).get("fileSelections", [])
        has_valid_files = len(files) > 0
        
        # 记录必须满足以下条件之一并且时间戳合理
        return (has_valid_messages or has_valid_files) and valid_timestamps

    @property
    def name(self):
        return self.data.get("name", "untitled")

    @property
    def conversation(self):
        # Handle both old and new conversation structures
        conversation = self.data.get("conversation", [])
        if not conversation and isinstance(self.data, dict):
            conversation = self.data.get("messages", [])
        return conversation

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
    
    created_at = record.created_at
    ended_at = record.ended_at
    if created_at > 0:
        created_time = datetime.fromtimestamp(created_at / 1000)
        md_content += f"- 开始时间: {created_time}\n"
    if ended_at > 0:
        ended_time = datetime.fromtimestamp(ended_at / 1000)
        md_content += f"- 结束时间: {ended_time}\n"
    
    context_files = record.data.get("context", {}).get("fileSelections", [])
    if context_files:
        md_content += "- 相关文件:\n"
        for file in context_files:
            # 处理新的URI结构
            uri = file.get("uri", {})
            path = None
            if isinstance(uri, dict):
                if "fsPath" in uri:
                    path = uri["fsPath"]
                elif "external" in uri:
                    path = uri["external"].replace("file:///", "").replace("%3A", ":")
            
            if path:
                filename = path.split("\\")[-1] if "\\" in path else path.split("/")[-1]
                md_content += f"- [{filename}]({path})\n"
    
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
                    uri = sel.get("uri", {})
                    path = None
                    if isinstance(uri, dict):
                        if "fsPath" in uri:
                            path = uri["fsPath"]
                        elif "external" in uri:
                            path = uri["external"].replace("file:///", "").replace("%3A", ":")
                    
                    if path:
                        filename = path.split("\\")[-1] if "\\" in path else path.split("/")[-1]
                        md_content += f"- From [{filename}]({path}): {sel.get('text', '')}\n"
            md_content += f"> {text}\n"
        elif msg_type == 2:
            md_content += "\n## Cursor\n\n"
            md_content += f"{text}\n"
            if code_blocks:
                for block in code_blocks:
                    uri = block.get("uri", {})
                    path = None
                    if isinstance(uri, dict):
                        if "fsPath" in uri:
                            path = uri["fsPath"]
                        elif "external" in uri:
                            path = uri["external"].replace("file:///", "").replace("%3A", ":")
                    
                    if path:
                        language = block.get("languageId", "text")
                        filename = path.split("\\")[-1] if "\\" in path else path.split("/")[-1]
                        code_content = block.get("content", "")
                        md_content += f"\n```{language} [{filename}]({path})\n"
                        md_content += code_content
                        md_content += "\n```\n"
    
    return md_content

def export_sessions(db_path, output_dir):
    # ---------- 新版兼容 & 旧版保留 ----------
    # 1）读出所有 KV 到内存
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM cursorDiskKV")
        rows = cursor.fetchall()
    # decode & filter
    kv_map = {}
    for k, raw in rows:
        if not isinstance(raw, (str, bytes)):
            continue
        v = raw.decode('utf-8') if isinstance(raw, bytes) else raw
        if not v or v.strip() == "[]":
            continue
        kv_map[k] = v

    sessions = []
    # 3）遍历 composerData: 只处理这类键
    for key, val in kv_map.items():
        if not key.startswith("composerData:"):
            continue
        try:
            comp = json.loads(val)
        except:
            continue

        # —— 旧版：直接判断顶层 conversation 数组 —— 
        if isinstance(comp, dict) and "conversation" in comp and isinstance(comp["conversation"], list):
            # 检查是否有实际内容
            has_content = False
            first_msg_text = ""
            for msg in comp["conversation"]:
                text = msg.get("text", "").strip()
                if text:
                    has_content = True
                    if not first_msg_text:
                        first_msg_text = text
            if has_content:
                # 如果名字是 untitled，用第一条消息作为标题
                if not comp.get("name") or comp.get("name").lower() == "untitled":
                    comp["name"] = first_msg_text.split("\n", 1)[0][:50]  # 取更长的标题
                rec = ChatRecord(key, val)
                sessions.append({"type": "old", "record": rec})
                continue

        # —— 新版：fullConversationHeadersOnly + bubbleId 聚合 ——
        # 先解包 _v + data
        if isinstance(comp, dict) and "_v" in comp and "data" in comp:
            comp = comp["data"]

        if comp.get("fullConversationHeadersOnly"):
            cid = comp.get("composerId")
            headers = comp.get("fullConversationHeadersOnly", [])
            msgs = []
            for h in headers:
                bid = h.get("bubbleId")
                tp = h.get("type")
                bubble_key = f"bubbleId:{cid}:{bid}"
                bv = kv_map.get(bubble_key)
                if not bv:
                    continue
                try:
                    bub = json.loads(bv)
                except:
                    continue
                if isinstance(bub, dict) and "_v" in bub and "data" in bub:
                    bub = bub["data"]
                text = bub.get("text", "")
                msgs.append({
                    "type": tp,
                    "text": text,
                    "context": bub.get("context", {}),
                    "codeBlocks": bub.get("codeBlocks", [])
                })
            if msgs:
                # 获取文件列表 - 从 context.mentions.fileSelections 中获取
                file_selections = comp.get("context", {}).get("mentions", {}).get("fileSelections", {})
                files = []
                for file_uri in file_selections.keys():
                    # 转换 URI 格式
                    path = file_uri.replace("file:///", "").replace("%3A", ":").replace("%2F", "/")
                    files.append({"uri": file_uri, "path": path})

                sessions.append({
                    "type": "new",
                    "name": comp.get("name", ""),
                    "start_time": comp.get("createdAt", 0),
                    "end_time": comp.get("lastUpdatedAt", comp.get("createdAt", 0)),  # 使用 lastUpdatedAt 作为结束时间
                    "messages": msgs,
                    "files": files
                })

    # 4）按开始时间升序，但要处理无效时间戳
    def _start(s):
        if s["type"] == "old":
            ts = s["record"].created_at
            # 如果时间戳明显不对（比如2025年），就返回0
            return ts if 0 < ts < 1735660800000 else 0  # 2025-01-01 的时间戳
        return s["start_time"]
    sessions.sort(key=_start)

    # 5）逐个导出到 markdown
    for idx, s in enumerate(sessions):
        try:
            if s["type"] == "old":
                rec = s["record"]
                # 旧版记录：优先用 name，若是 untitled 则用首条消息，限制25字
                title = rec.name.strip()
                if not title or title.lower() == "untitled":
                    first = next((m["text"] for m in rec.conversation if m.get("text")), "")
                    title = first.split("\n", 1)[0].strip()[:25] or "untitled"
                md = generate_markdown(rec)
            else:
                title = s["name"].strip()
                if not title:
                    first = s["messages"][0]["text"].split("\n", 1)[0].strip()
                    title = first[:25]  # 同样限制25字
                lines = [f"# {title}", "", "## 会话信息", ""]
                st = datetime.fromtimestamp(s["start_time"] / 1000)
                lines.append(f"- 开始时间: {st}")

                et = datetime.fromtimestamp(s["end_time"] / 1000)
                lines.append(f"- 结束时间: {et}")

                # 添加相关文件信息
                if s.get("files"):
                    lines.append("- 相关文件:")
                    for file in s["files"]:
                        path = file.get("path", "")
                        if path:
                            filename = path.split("\\")[-1] if "\\" in path else path.split("/")[-1]
                            lines.append(f"- [{filename}]({path})")
                lines.append("")
                for m in s["messages"]:
                    if m["type"] == 1:
                        lines += ["## User", "", f"> {m['text']}", ""]
                    elif m["type"] == 2:
                        lines += ["## Cursor", "", m["text"], ""]
                        for cb in m.get("codeBlocks", []):
                            uri = cb.get("uri", {})
                            path = None
                            if isinstance(uri, dict):
                                path = uri.get("fsPath") or uri.get("external", "").replace("file:///", "").replace("%3A", ":")
                            lang = cb.get("languageId", "text")
                            fname = Path(path).name if path else ""
                            lines += [f"```{lang} [{fname}]({path})", cb.get("content", ""), "```", ""]
                md = "\n".join(lines)
            # 获取结束时间用于文件命名
            if s["type"] == "old":
                end_time = record.ended_at
            else:
                # 新版会话使用 end_time 字段
                end_time = s["end_time"]

            # 格式化时间文件名
            if end_time > 0:
                time_str = datetime.fromtimestamp(end_time / 1000).strftime("%Y%m%d%H%M")
            else:
                # 如果没有有效时间戳，使用创建时间
                if s["type"] == "old":
                    create_time = record.created_at
                else:
                    create_time = s["start_time"]
                if create_time > 0:
                    time_str = datetime.fromtimestamp(create_time / 1000).strftime("%Y%m%d%H%M")
                else:
                    time_str = "unknown"

            # 生成安全文件名时过滤掉更多特殊字符
            safe = title.replace("<", "_").replace(">", "_").replace(":", "_")\
                       .replace("/", "_").replace("\\", "_").replace("|", "_")\
                       .replace("?", "_").replace("*", "_").replace('"', "_")\
                       .replace("'", "_").replace("\n", "_").replace("\r", "_")
            # 限制文件名总长度
            if len(safe) > 40:  # 减少限制，为时间前缀留空间
                safe = safe[:37] + "..."
            fn = f"{time_str}_{safe}.md"
            out = Path(output_dir) / fn
            with open(out, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"已导出: {out}")
        except Exception as e:
            print(f"导出失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="Cursor 聊天记录导出工具")
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
