# Co-Vibe - マルチプロバイダAIコーディングエージェント

Python標準ライブラリのみを使用した、ターミナルベースのAIコーディングエージェントです。

## 主な機能

### 1. マルチプロバイダLLMサポート
- **Anthropic (Claude)**: Messages API対応
- **OpenAI (GPT)**: Chat Completions API対応  
- **Groq**: OpenAI互換API対応
- **Ollama**: ローカルLLM対応

### 2. 豊富なツールシステム
- **Bash**: コマンド実行（安全性チェック付き）
- **Read**: ファイル読み取り（行範囲指定、画像base64変換）
- **Write**: ファイル書き込み（ディレクトリ自動作成）
- **Edit**: 部分編集（文字列置換）
- **Glob**: ファイルパターン検索
- **Grep**: テキスト検索（正規表現対応）

### 3. インテリジェントな戦略選択
- **auto**: バランス型（デフォルト）
- **strong**: 最強モデル優先
- **fast**: 高速モデル優先
- **cheap**: 低コストモデル優先

### 4. セッション管理
- 会話履歴の保存・復元
- JSON形式での永続化

### 5. セキュリティ機能
- 危険なコマンドの検出・確認
- 環境変数からのシークレット除外
- 権限レベル別ツール管理

## インストール・セットアップ

### 1. ファイルの配置
```bash
# co_vibe.py を適切なディレクトリに配置
chmod +x co_vibe.py
```

### 2. 環境変数の設定
```bash
# .env ファイルまたは環境変数で設定
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export GROQ_API_KEY="your-groq-api-key"
# Ollama は localhost:11434 で動作していることを前提
```

## 使用方法

### 基本的な使用
```bash
# インタラクティブモード
python3 co_vibe.py

# ワンショット実行
python3 co_vibe.py -p "Pythonでフィボナッチ数列を計算するコードを書いて"

# 自動承認モード
python3 co_vibe.py -y

# 戦略指定
python3 co_vibe.py --strategy strong
```

### コマンドラインオプション
- `-p, --prompt`: ワンショット実行モード
- `-y, --yes`: 自動承認モード（ツール実行の確認を省略）
- `--strategy`: 実行戦略 (auto/strong/fast/cheap)
- `-m, --model`: 特定モデル指定
- `--resume`: セッション復元
- `--debug`: デバッグモード

### インタラクティブコマンド
- `/help`: ヘルプ表示
- `/model`: モデル情報表示
- `/strategy [新戦略]`: 戦略変更
- `/clear`: 会話履歴クリア
- `/save`: セッション保存
- `/exit`: 終了

## 使用例

### 1. コードの作成・編集
```
> Pythonで素数判定関数を作成して、primes.py ファイルに保存してください

[Co-Vibeがツールを使って実装・保存]
```

### 2. ファイル操作・分析
```
> プロジェクト内の*.py ファイルを検索して、TODO コメントがあるものを教えて

[Glob, Grep ツールを使って検索・分析]
```

### 3. システム操作
```
> 現在のディレクトリの使用容量を確認して、大きなファイルを見つけて

[Bash ツールでdu, find コマンドを実行]
```

## アーキテクチャ

### クラス構造
- **CoVibeAgent**: メインエージェントクラス
- **LLMClient**: マルチプロバイダLLM呼び出し
- **ToolRegistry**: ツール管理・実行
- **Tool (ABC)**: ツールの抽象基底クラス
- **ProviderHealth**: プロバイダー健全性管理

### フェイルオーバー機能
プロバイダーでエラーが発生した場合、指数バックオフを使用して自動的に次のプロバイダーに切り替えます。

### 権限管理
ツールは3つのレベルに分類されます：
- **safe**: 自動実行
- **confirm**: 確認が必要
- **network**: ネットワーク操作（将来実装）

## 制約事項

### 現在の実装（MVP版）
この実装は要求仕様の基本機能を含むMVP版です。以下の高度な機能は将来のバージョンで実装予定：

- サブエージェント・マルチエージェント
- Deep Research パイプライン
- 高度なTUI（DECSTBM、ストリーミング表示）
- MCP クライアント
- GitCheckpoint
- FileWatcher
- DAGWorkflow

### 技術制約
- Python 3.8+ 標準ライブラリのみ
- 単一ファイル構成
- クロスプラットフォーム対応

## トラブルシューティング

### APIキーエラー
```
エラー: APIキーが設定されていません
→ 環境変数を確認してください
```

### プロバイダー接続エラー
```
全てのプロバイダーで呼び出しに失敗しました
→ ネットワーク接続とAPIキーを確認してください
```

### ツール実行エラー
```
ツール実行に失敗しました
→ ファイルパス、権限、コマンド構文を確認してください
```

## 拡張開発

新しいツールを追加する場合：

```python
class MyCustomTool(Tool):
    def get_schema(self) -> Dict[str, Any]:
        # OpenAI Function Calling スキーマを返す
        pass
    
    def execute(self, **kwargs) -> str:
        # ツールの実行ロジック
        pass

# ToolRegistryに登録
registry = ToolRegistry()
registry.register_tool(MyCustomTool())
```

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。

## 貢献

バグ報告や機能提案をお待ちしています。プルリクエストも歓迎です。