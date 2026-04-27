#!/usr/bin/env python3
"""
Co-Vibe: Multi-provider AI Coding Agent
Python標準ライブラリのみを使用したAIコーディングエージェント
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import threading
import queue
import re
import base64
import mimetypes
import fnmatch
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import shutil


# ============================================================================
# 設定・定数
# ============================================================================

VERSION = "1.0.0"
USER_AGENT = f"Co-Vibe/{VERSION}"

# デフォルトモデル設定
DEFAULT_MODELS = {
    "anthropic": {
        "strong": "claude-3-5-sonnet-20241022",
        "balanced": "claude-3-5-haiku-20241022", 
        "fast": "claude-3-5-haiku-20241022"
    },
    "openai": {
        "strong": "gpt-4-turbo-preview",
        "balanced": "gpt-4o-mini",
        "fast": "gpt-3.5-turbo"
    },
    "groq": {
        "strong": "llama-3.1-70b-versatile",
        "balanced": "llama-3.1-8b-instant",
        "fast": "llama-3.1-8b-instant"
    },
    "ollama": {
        "strong": "llama3.1:70b",
        "balanced": "llama3.1:8b",
        "fast": "llama3.1:8b"
    }
}

# API エンドポイント
ENDPOINTS = {
    "anthropic": "https://api.anthropic.com/v1/messages",
    "openai": "https://api.openai.com/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "ollama": "http://localhost:11434/v1/chat/completions"
}


# ============================================================================
# データ構造
# ============================================================================

@dataclass
class Message:
    role: str
    content: str
    timestamp: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ProviderHealth:
    failures: int = 0
    last_failure: Optional[float] = None
    cooldown_until: Optional[float] = None
    
    def is_healthy(self) -> bool:
        now = time.time()
        return self.cooldown_until is None or now > self.cooldown_until
    
    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        # 指数バックオフ: 2^failures 秒のクールダウン
        cooldown_seconds = min(2 ** self.failures, 300)  # 最大5分
        self.cooldown_until = time.time() + cooldown_seconds
    
    def record_success(self):
        self.failures = 0
        self.last_failure = None
        self.cooldown_until = None


# ============================================================================
# ツールシステム
# ============================================================================

class Tool(ABC):
    """ツールの抽象基底クラス"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('tool', '')
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """OpenAI Function Calling スキーマを返す"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """ツールを実行して結果を返す"""
        pass
    
    @property
    def permission_level(self) -> str:
        """権限レベル: safe, confirm, network"""
        return "safe"


class BashTool(Tool):
    """コマンド実行ツール"""
    
    @property
    def permission_level(self) -> str:
        return "confirm"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "bash",
                "description": "Execute bash commands",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute"
                        },
                        "timeout": {
                            "type": "integer", 
                            "description": "Timeout in seconds",
                            "default": 30
                        }
                    },
                    "required": ["command"]
                }
            }
        }
    
    def _sanitize_env(self, env: Dict[str, str]) -> Dict[str, str]:
        """環境変数からシークレットを除外"""
        sensitive_keys = {
            'PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'AUTH', 'CREDENTIAL',
            'API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY'
        }
        
        sanitized = {}
        for key, value in env.items():
            if any(sensitive in key.upper() for sensitive in sensitive_keys):
                continue
            sanitized[key] = value
        
        return sanitized
    
    def execute(self, command: str, timeout: int = 30) -> str:
        try:
            # 危険なコマンドの検出
            dangerous_patterns = [
                r'sudo\s+rm\s+-rf',
                r'rm\s+-rf\s+/',
                r'git\s+push\s+--force',
                r'dd\s+if=',
                r'mkfs\.',
                r'fdisk'
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return f"エラー: 危険なコマンドが検出されました: {command}"
            
            # 環境変数のサニタイズ
            env = self._sanitize_env(os.environ.copy())
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"Return code: {result.returncode}"
            
            return output
            
        except subprocess.TimeoutExpired:
            return f"エラー: コマンドがタイムアウトしました ({timeout}秒)"
        except Exception as e:
            return f"エラー: {str(e)}"


class ReadTool(Tool):
    """ファイル読み取りツール"""
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "read",
                "description": "Read file contents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        },
                        "start_line": {
                            "type": "integer",
                            "description": "Start line number (1-based)"
                        },
                        "end_line": {
                            "type": "integer",
                            "description": "End line number (1-based)"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        }
    
    def _is_binary_file(self, file_path: str) -> bool:
        """ファイルがバイナリかどうか判定"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
                if b'\0' in chunk:
                    return True
            return False
        except:
            return True
    
    def execute(self, file_path: str, start_line: Optional[int] = None, 
                end_line: Optional[int] = None) -> str:
        try:
            if not os.path.exists(file_path):
                return f"エラー: ファイルが見つかりません: {file_path}"
            
            # バイナリファイルの判定
            if self._is_binary_file(file_path):
                # 画像ファイルの場合はbase64エンコード
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type and mime_type.startswith('image/'):
                    with open(file_path, 'rb') as f:
                        encoded = base64.b64encode(f.read()).decode()
                        return f"画像ファイル (base64):\ndata:{mime_type};base64,{encoded}"
                else:
                    return f"バイナリファイル: {file_path} (内容は表示できません)"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 行範囲の指定がある場合
            if start_line is not None or end_line is not None:
                start_idx = (start_line - 1) if start_line else 0
                end_idx = end_line if end_line else len(lines)
                lines = lines[start_idx:end_idx]
            
            # 行番号を付与
            numbered_lines = []
            start_num = start_line if start_line else 1
            for i, line in enumerate(lines):
                numbered_lines.append(f"{start_num + i:4d}│{line.rstrip()}")
            
            return "\n".join(numbered_lines)
            
        except Exception as e:
            return f"エラー: {str(e)}"


class WriteTool(Tool):
    """ファイル書き込みツール"""
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "write",
                "description": "Write content to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        },
                        "mode": {
                            "type": "string",
                            "description": "Write mode: overwrite or append",
                            "enum": ["overwrite", "append"],
                            "default": "overwrite"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            }
        }
    
    def execute(self, file_path: str, content: str, mode: str = "overwrite") -> str:
        try:
            # ディレクトリの作成
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            write_mode = 'w' if mode == 'overwrite' else 'a'
            
            with open(file_path, write_mode, encoding='utf-8') as f:
                f.write(content)
            
            action = "書き込み" if mode == 'overwrite' else "追記"
            return f"ファイルに{action}しました: {file_path} ({len(content)} 文字)"
            
        except Exception as e:
            return f"エラー: {str(e)}"


class EditTool(Tool):
    """ファイル部分編集ツール"""
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "edit",
                "description": "Edit file by replacing text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to edit"
                        },
                        "old_string": {
                            "type": "string",
                            "description": "String to replace"
                        },
                        "new_string": {
                            "type": "string",
                            "description": "Replacement string"
                        }
                    },
                    "required": ["file_path", "old_string", "new_string"]
                }
            }
        }
    
    def execute(self, file_path: str, old_string: str, new_string: str) -> str:
        try:
            if not os.path.exists(file_path):
                return f"エラー: ファイルが見つかりません: {file_path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_string not in content:
                return f"エラー: 指定された文字列が見つかりません: {old_string[:50]}..."
            
            # 複数回の出現をチェック
            count = content.count(old_string)
            if count > 1:
                return f"エラー: 文字列が{count}回出現します。より具体的な文字列を指定してください。"
            
            new_content = content.replace(old_string, new_string)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return f"ファイルを編集しました: {file_path}"
            
        except Exception as e:
            return f"エラー: {str(e)}"


class GlobTool(Tool):
    """ファイルパターン検索ツール"""
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "glob",
                "description": "Find files matching a pattern",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "File pattern to match (supports * and ?)"
                        },
                        "directory": {
                            "type": "string",
                            "description": "Directory to search in",
                            "default": "."
                        }
                    },
                    "required": ["pattern"]
                }
            }
        }
    
    def execute(self, pattern: str, directory: str = ".") -> str:
        try:
            matches = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, directory)
                    if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(file, pattern):
                        matches.append(relative_path)
            
            if matches:
                matches.sort()
                return "\n".join(matches)
            else:
                return f"パターンにマッチするファイルが見つかりません: {pattern}"
                
        except Exception as e:
            return f"エラー: {str(e)}"


class GrepTool(Tool):
    """テキスト検索ツール"""
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "grep",
                "description": "Search for text in files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Text pattern to search for (supports regex)"
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "File pattern to search in",
                            "default": "*"
                        },
                        "directory": {
                            "type": "string",
                            "description": "Directory to search in",
                            "default": "."
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Case sensitive search",
                            "default": false
                        }
                    },
                    "required": ["pattern"]
                }
            }
        }
    
    def execute(self, pattern: str, file_pattern: str = "*", 
                directory: str = ".", case_sensitive: bool = False) -> str:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            matches = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if not fnmatch.fnmatch(file, file_pattern):
                        continue
                        
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, 1):
                                if regex.search(line):
                                    relative_path = os.path.relpath(full_path, directory)
                                    matches.append(f"{relative_path}:{line_num}:{line.strip()}")
                    except (UnicodeDecodeError, PermissionError):
                        continue
            
            if matches:
                return "\n".join(matches[:100])  # 最初の100件まで
            else:
                return f"パターンにマッチするテキストが見つかりません: {pattern}"
                
        except Exception as e:
            return f"エラー: {str(e)}"


class ToolRegistry:
    """ツール登録・管理クラス"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """ビルトインツールの登録"""
        builtin_tools = [
            BashTool(),
            ReadTool(),
            WriteTool(), 
            EditTool(),
            GlobTool(),
            GrepTool()
        ]
        
        for tool in builtin_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: Tool):
        """ツールの登録"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """ツールの取得"""
        return self.tools.get(name)
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """全ツールのスキーマを取得"""
        return [tool.get_schema() for tool in self.tools.values()]
    
    def execute_tool(self, name: str, **kwargs) -> str:
        """ツールの実行"""
        tool = self.get_tool(name)
        if not tool:
            return f"エラー: ツールが見つかりません: {name}"
        
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return f"エラー: ツール実行に失敗しました: {str(e)}"


# ============================================================================
# LLMクライアント
# ============================================================================

class LLMClient:
    """マルチプロバイダLLMクライアント"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.health = {
            provider: ProviderHealth()
            for provider in ["anthropic", "openai", "groq", "ollama"]
        }
        self.tool_registry = ToolRegistry()
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """APIキーの取得"""
        key_names = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY", 
            "groq": "GROQ_API_KEY",
            "ollama": None  # ローカルなのでAPIキー不要
        }
        
        key_name = key_names.get(provider)
        if key_name:
            return os.getenv(key_name)
        return None
    
    def _build_anthropic_request(self, messages: List[Message], model: str) -> Dict[str, Any]:
        """Anthropic API リクエストの構築"""
        # システムメッセージの分離
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message += msg.content + "\n"
            else:
                user_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        request = {
            "model": model,
            "messages": user_messages,
            "max_tokens": 4000,
            "tools": self.tool_registry.get_schemas()
        }
        
        if system_message:
            request["system"] = system_message.strip()
        
        return request
    
    def _build_openai_request(self, messages: List[Message], model: str) -> Dict[str, Any]:
        """OpenAI互換 API リクエストの構築"""
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": 4000,
            "tools": self.tool_registry.get_schemas(),
            "tool_choice": "auto"
        }
    
    def _make_request(self, provider: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP リクエストの実行"""
        url = ENDPOINTS[provider]
        
        # ヘッダーの構築
        headers = {
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT
        }
        
        if provider == "anthropic":
            api_key = self._get_api_key("anthropic")
            if api_key:
                headers["x-api-key"] = api_key
                headers["anthropic-version"] = "2023-06-01"
        elif provider in ["openai", "groq"]:
            api_key = self._get_api_key(provider)
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        
        # リクエストの作成と送信
        request_data = json.dumps(data).encode('utf-8')
        request = urllib.request.Request(url, data=request_data, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"HTTP {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {str(e)}")
    
    def _process_anthropic_response(self, response: Dict[str, Any]) -> Tuple[str, List[Dict]]:
        """Anthropic レスポンスの処理"""
        content = response.get("content", [])
        
        text_content = ""
        tool_calls = []
        
        for item in content:
            if item.get("type") == "text":
                text_content += item.get("text", "")
            elif item.get("type") == "tool_use":
                tool_calls.append({
                    "name": item.get("name"),
                    "parameters": item.get("input", {})
                })
        
        return text_content, tool_calls
    
    def _process_openai_response(self, response: Dict[str, Any]) -> Tuple[str, List[Dict]]:
        """OpenAI互換レスポンスの処理"""
        choices = response.get("choices", [])
        if not choices:
            return "", []
        
        message = choices[0].get("message", {})
        text_content = message.get("content", "") or ""
        
        tool_calls = []
        if message.get("tool_calls"):
            for call in message["tool_calls"]:
                function = call.get("function", {})
                try:
                    parameters = json.loads(function.get("arguments", "{}"))
                except json.JSONDecodeError:
                    parameters = {}
                
                tool_calls.append({
                    "name": function.get("name"),
                    "parameters": parameters
                })
        
        return text_content, tool_calls
    
    def generate(self, messages: List[Message], strategy: str = "balanced") -> Tuple[str, List[Dict]]:
        """テキスト生成とツール呼び出し"""
        
        # 戦略に基づくプロバイダーとモデルの選択
        providers = self._get_providers_by_strategy(strategy)
        
        for provider in providers:
            if not self.health[provider].is_healthy():
                continue
            
            try:
                model = self._get_model_for_provider(provider, strategy)
                
                # リクエストの構築
                if provider == "anthropic":
                    request_data = self._build_anthropic_request(messages, model)
                else:
                    request_data = self._build_openai_request(messages, model)
                
                # API呼び出し
                response = self._make_request(provider, request_data)
                
                # レスポンスの処理
                if provider == "anthropic":
                    text, tool_calls = self._process_anthropic_response(response)
                else:
                    text, tool_calls = self._process_openai_response(response)
                
                # 成功時はヘルスを回復
                self.health[provider].record_success()
                
                return text, tool_calls
                
            except Exception as e:
                print(f"プロバイダー {provider} でエラー: {str(e)}")
                self.health[provider].record_failure()
                continue
        
        raise Exception("全てのプロバイダーで呼び出しに失敗しました")
    
    def _get_providers_by_strategy(self, strategy: str) -> List[str]:
        """戦略に基づくプロバイダーの優先順位"""
        strategies = {
            "auto": ["anthropic", "openai", "groq", "ollama"],
            "strong": ["anthropic", "openai", "groq", "ollama"],
            "fast": ["groq", "ollama", "openai", "anthropic"],
            "cheap": ["ollama", "groq", "openai", "anthropic"]
        }
        return strategies.get(strategy, strategies["auto"])
    
    def _get_model_for_provider(self, provider: str, strategy: str) -> str:
        """プロバイダーと戦略に基づくモデル選択"""
        tier = "balanced"
        if strategy in ["strong"]:
            tier = "strong"
        elif strategy in ["fast", "cheap"]:
            tier = "fast"
        
        return DEFAULT_MODELS[provider][tier]


# ============================================================================
# エージェント本体
# ============================================================================

class CoVibeAgent:
    """Co-Vibe AIエージェント"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_client = LLMClient(config)
        self.messages: List[Message] = []
        self.session_file = None
        self._initialize_system_prompt()
    
    def _initialize_system_prompt(self):
        """システムプロンプトの初期化"""
        import platform
        
        system_prompt = f"""あなたは Co-Vibe、高度なAIコーディングエージェントです。

# 基本情報
- OS: {platform.system()} {platform.release()}
- Python: {sys.version}
- 日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 役割
ユーザーからの指示に基づいて、以下のタスクを実行します：
1. コーディング・プログラム作成
2. ファイル操作・編集
3. コマンド実行
4. テキスト検索・解析
5. 技術的質問への回答

# ツール使用指針
- ファイル操作前は必ず内容を確認する
- コマンド実行は安全性を考慮する
- エラーが発生した場合は詳細を分析する
- ユーザーの質問に対して具体的で実用的な回答を提供する

# 言語設定
ユーザーが日本語で質問した場合は日本語で回答し、英語の場合は英語で回答します。
"""
        
        self.messages.append(Message(role="system", content=system_prompt))
    
    def process_message(self, user_input: str) -> str:
        """ユーザーメッセージの処理"""
        # ユーザーメッセージを追加
        self.messages.append(Message(role="user", content=user_input))
        
        try:
            # LLM呼び出し
            strategy = self.config.get("strategy", "balanced")
            response_text, tool_calls = self.llm_client.generate(self.messages, strategy)
            
            # ツール呼び出しの実行
            if tool_calls:
                tool_results = []
                for call in tool_calls:
                    name = call["name"]
                    params = call["parameters"]
                    
                    # 権限確認
                    tool = self.llm_client.tool_registry.get_tool(name)
                    if tool and tool.permission_level == "confirm" and not self.config.get("auto_approve", False):
                        response = input(f"ツール '{name}' を実行しますか？ (y/n): ")
                        if response.lower() != 'y':
                            tool_results.append(f"ツール '{name}' の実行がキャンセルされました")
                            continue
                    
                    result = self.llm_client.tool_registry.execute_tool(name, **params)
                    tool_results.append(f"ツール '{name}' の実行結果:\n{result}")
                
                # ツール結果を含めて再度LLM呼び出し
                if tool_results:
                    tool_summary = "\n\n".join(tool_results)
                    self.messages.append(Message(role="assistant", content=f"ツールを実行します...\n\n{tool_summary}"))
                    self.messages.append(Message(role="user", content="ツールの実行結果を踏まえて、回答を完成させてください。"))
                    response_text, _ = self.llm_client.generate(self.messages, strategy)
            
            # アシスタント回答を追加
            self.messages.append(Message(role="assistant", content=response_text))
            
            return response_text
            
        except Exception as e:
            error_msg = f"エラーが発生しました: {str(e)}"
            self.messages.append(Message(role="assistant", content=error_msg))
            return error_msg
    
    def save_session(self, filename: str):
        """セッションの保存"""
        try:
            session_data = {
                "version": VERSION,
                "timestamp": datetime.now().isoformat(),
                "config": self.config,
                "messages": [msg.to_dict() for msg in self.messages]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"セッション保存エラー: {str(e)}")
    
    def load_session(self, filename: str):
        """セッションの復元"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.messages = []
            for msg_data in session_data.get("messages", []):
                self.messages.append(Message(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    timestamp=msg_data.get("timestamp")
                ))
                
        except Exception as e:
            print(f"セッション復元エラー: {str(e)}")


# ============================================================================
# CLI インターフェース
# ============================================================================

def print_banner():
    """バナー表示"""
    banner = f"""
╔══════════════════════════════════════╗
║        Co-Vibe v{VERSION}               ║
║   Multi-provider AI Coding Agent     ║
╚══════════════════════════════════════╝

使用可能なコマンド:
  /help    - ヘルプを表示
  /model   - モデル情報を表示  
  /strategy - 戦略を変更
  /clear   - 会話履歴をクリア
  /save    - セッションを保存
  /load    - セッションを読み込み
  /exit    - 終了

チャットを開始してください...
"""
    print(banner)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Co-Vibe AI Coding Agent")
    parser.add_argument("-p", "--prompt", help="ワンショット実行モード")
    parser.add_argument("-y", "--yes", action="store_true", help="自動承認モード")
    parser.add_argument("--strategy", choices=["auto", "strong", "fast", "cheap"], 
                       default="balanced", help="実行戦略")
    parser.add_argument("-m", "--model", help="使用するモデル")
    parser.add_argument("--resume", help="セッションファイルから復元")
    parser.add_argument("--debug", action="store_true", help="デバッグモード")
    
    args = parser.parse_args()
    
    # 設定の構築
    config = {
        "strategy": args.strategy,
        "auto_approve": args.yes,
        "debug": args.debug
    }
    
    # エージェントの初期化
    agent = CoVibeAgent(config)
    
    # セッション復元
    if args.resume:
        agent.load_session(args.resume)
        print(f"セッションを復元しました: {args.resume}")
    
    # ワンショットモード
    if args.prompt:
        response = agent.process_message(args.prompt)
        print(response)
        return
    
    # インタラクティブモード
    print_banner()
    
    try:
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # スラッシュコマンドの処理
                if user_input.startswith("/"):
                    command = user_input[1:].split()[0]
                    
                    if command == "help":
                        print_banner()
                    elif command == "exit":
                        break
                    elif command == "clear":
                        agent.messages = [agent.messages[0]]  # システムプロンプトのみ残す
                        print("会話履歴をクリアしました")
                    elif command == "save":
                        filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        agent.save_session(filename)
                        print(f"セッションを保存しました: {filename}")
                    elif command == "model":
                        print(f"現在の戦略: {config['strategy']}")
                        print("利用可能なプロバイダー: anthropic, openai, groq, ollama")
                    elif command == "strategy":
                        parts = user_input.split()
                        if len(parts) > 1:
                            new_strategy = parts[1]
                            if new_strategy in ["auto", "strong", "fast", "cheap"]:
                                config["strategy"] = new_strategy
                                print(f"戦略を {new_strategy} に変更しました")
                            else:
                                print("無効な戦略です。auto, strong, fast, cheap から選択してください")
                        else:
                            print(f"現在の戦略: {config['strategy']}")
                    else:
                        print(f"不明なコマンド: {command}")
                    continue
                
                # 通常のメッセージ処理
                print("\n処理中...")
                response = agent.process_message(user_input)
                print(f"\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n処理を中断しました")
                continue
                
    except (EOFError, KeyboardInterrupt):
        print("\n\nCo-Vibe を終了します。")


if __name__ == "__main__":
    main()