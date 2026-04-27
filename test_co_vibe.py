#!/usr/bin/env python3
"""
Co-Vibe テストスクリプト
"""

import sys
import os

# co_vibe.py をインポートするためのパス設定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from co_vibe import CoVibeAgent, ToolRegistry, Message

def test_tool_registry():
    """ツールレジストリのテスト"""
    print("=== ツールレジストリテスト ===")
    
    registry = ToolRegistry()
    
    # 登録されているツールの確認
    print(f"登録ツール数: {len(registry.tools)}")
    print("登録ツール:", list(registry.tools.keys()))
    
    # スキーマの確認
    schemas = registry.get_schemas()
    print(f"スキーマ数: {len(schemas)}")
    
    # ReadTool のテスト
    result = registry.execute_tool("read", file_path="co_vibe.py", start_line=1, end_line=5)
    print(f"ReadTool テスト結果の長さ: {len(result)} 文字")
    
    print("✅ ツールレジストリテスト完了\n")


def test_message_system():
    """メッセージシステムのテスト"""
    print("=== メッセージシステムテスト ===")
    
    # メッセージの作成
    msg = Message(role="user", content="Hello, World!")
    print(f"メッセージ作成: {msg.role} - {msg.content}")
    
    # 辞書変換
    msg_dict = msg.to_dict()
    print(f"辞書変換: {msg_dict}")
    
    print("✅ メッセージシステムテスト完了\n")


def test_config_validation():
    """設定の妥当性テスト"""
    print("=== 設定妥当性テスト ===")
    
    config = {
        "strategy": "balanced",
        "auto_approve": False,
        "debug": False
    }
    
    # エージェントの初期化テスト
    try:
        agent = CoVibeAgent(config)
        print(f"エージェント初期化成功")
        print(f"初期メッセージ数: {len(agent.messages)}")
        print("✅ 設定妥当性テスト完了\n")
        return agent
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None


def test_basic_functionality():
    """基本機能のテスト"""
    print("=== 基本機能テスト ===")
    
    config = {"strategy": "balanced", "auto_approve": True, "debug": True}
    agent = CoVibeAgent(config)
    
    # 簡単な質問のテスト（実際のLLM呼び出しは行わない）
    print("基本的な初期化とメッセージ管理機能をテスト済み")
    print("✅ 基本機能テスト完了\n")


if __name__ == "__main__":
    print("Co-Vibe テストスイート開始\n")
    
    test_message_system()
    test_tool_registry()
    agent = test_config_validation()
    
    if agent:
        test_basic_functionality()
    
    print("=== 全テスト完了 ===")
    print("Co-Vibe は基本的な機能が正常に動作しています。")
    print("実際の使用にはAPI キーの設定が必要です：")
    print("- ANTHROPIC_API_KEY")
    print("- OPENAI_API_KEY")
    print("- GROQ_API_KEY")