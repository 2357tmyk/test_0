# DC-DC昇圧コンバーター自動設計システム - 詳細仕様書

## 1. システム概要

### 1.1 目的
プロフェッショナル級のDC-DC昇圧コンバーター自動設計システムを提供し、状態空間モデルによる厳密な伝達関数導出と内外二重PI制御設計を実現する。

### 1.2 品質基準
- スタッフエンジニアレビュー対応級の数学的厳密性
- 実用的な設計制約と安全マージンの確保
- プロダクション品質のコード実装

## 2. 入力仕様 (config_boost_design.xlsx)

### 2.1 Excel設定ファイル構造

**ファイルパス:** `./config/config_boost_design.xlsx`

**列構成:**
| 列 | 列名               | データ型 | 説明                       |
|----|--------------------|----------|----------------------------|
| A  | Category          | string   | 大分類                     |
| B  | Item              | string   | 項目名                     |
| C  | Symbol            | string   | 数学記号                   |
| D  | Mode              | string   | RANGE/DISCRETE/FIXED      |
| E  | Min               | float    | 最小値                     |
| F  | Max               | float    | 最大値                     |
| G  | Candidates        | string   | 離散候補（カンマ区切り）   |
| H  | Nominal           | float    | 公称値                     |
| I  | Tolerance_3sigma  | float    | ±3σ（% or 絶対値）        |
| J  | Unit              | string   | 単位                       |
| K  | Notes             | string   | 制約・設計意図             |

### 2.2 必須パラメータ定義

#### 回路要素
- **抵抗 R**: Mode=DISCRETE, Candidates="10, 15, 20, 30, 45", Unit="Ω"
- **インダクタ L**: Mode=DISCRETE, Candidates="0.5e-3, 1.0e-3, 1.5e-3", Unit="H"
- **インダクタ DCR**: Mode=RANGE, Min=0.01, Max=0.1, Unit="Ω"
- **コンデンサ C**: Mode=DISCRETE, Candidates="22e-6, 44e-6, 66e-6", Unit="F"
- **コンデンサ ESR**: Mode=RANGE, Min=0.01, Max=0.5, Unit="Ω"

#### スイッチング・動作
- **スイッチング周波数**: Mode=DISCRETE, Candidates="50e3, 100e3, 200e3", Unit="Hz"
- **Duty範囲**: Mode=RANGE, Min=0.1, Max=0.8, Unit="-"
- **動作モード**: Mode=FIXED, Nominal="CCM", Unit="-"

#### 制御構成
- **PWM遅れ**: Mode=FIXED, Nominal=0.5e-6, Unit="s"
- **サンプリング遅れ**: Mode=FIXED, Nominal=1e-6, Unit="s"
- **センサLPF遅れ**: Mode=RANGE, Min=1e-6, Max=10e-6, Unit="s"

#### 入力条件
- **入力電圧**: Mode=FIXED, Nominal=8.0, Unit="V"
- **出力電圧**: Mode=FIXED, Nominal=12.0, Unit="V"
- **入力電圧変動速度**: Mode=RANGE, Min=1, Max=100, Unit="V/s"

#### 制御帯域制約
- **電流ループPM**: Mode=RANGE, Min=45, Max=75, Unit="degree"
- **電圧ループPM**: Mode=RANGE, Min=60, Max=75, Unit="degree"
- **ゲイン余裕**: Mode=RANGE, Min=10, Max=20, Unit="dB"

## 3. 出力仕様

### 3.1 Excel結果ファイル (output_boost_design.xlsx)

**ファイルパス:** `./output/output_boost_design.xlsx`

#### 3.1.1 設計結果シート
| 列 | 列名        | データ型 | 説明           |
|----|-------------|----------|----------------|
| A  | Category    | string   | 分類           |
| B  | Parameter   | string   | パラメータ名   |
| C  | Symbol      | string   | 数学記号       |
| D  | Value       | float    | 計算値         |
| E  | Unit        | string   | 単位           |
| F  | Tolerance   | float    | 許容差         |
| G  | Status      | string   | Pass/Fail/Warning |

#### 3.1.2 制御定数シート
**内外二重PI制御パラメータ:**
- 電流ループ: Kp_i, Ki_i, Ti_i, PM_i, GM_i
- 電圧ループ: Kp_v, Ki_v, Ti_v, PM_v, GM_v
- クロスオーバー周波数: f_ci, f_cv
- 安定性指標: 位相余裕, ゲイン余裕

### 3.2 HTML技術文書 (output_boost_design.html)

**ファイルパス:** `./output/output_boost_design.html`

#### 3.2.1 必須セクション
1. **設計概要**: 要求仕様と選定パラメータの要約
2. **状態空間モデル**: 数学的導出過程の詳細説明
3. **伝達関数解析**: 各伝達関数の導出と特性解析
4. **PI制御器設計**: 設計手順と安定性解析
5. **設計検証**: 制約チェックと安全マージン確認
6. **設計結果**: 最終的な設計値と性能予測

#### 3.2.2 数式表記要求
- MathJax使用による美しい数式表示
- 一般式と数値代入式の両方を記載
- 計算過程の詳細な説明

## 4. 数学的仕様

### 4.1 状態空間モデル

**状態変数:**
```
x = [i_L, v_C]^T
```

**状態方程式:**
```
dx/dt = A*x + B*u + E*d
y = C*x
```

**係数行列:**
```
A = [0,        -(1-D)/L]
    [(1-D)/C,  -1/(RC) ]

B = [1/L]
    [0  ]

C = [0, 1]
```

### 4.2 伝達関数

#### 4.2.1 制御-出力伝達関数
```
G_vd(s) = V_in/(1-D)^2 * (1 - s/ω_z) / (1 + s/(ω_0*Q) + s^2/ω_0^2)
```

**特性周波数:**
- RHP零点: `ω_z = (1-D)^2*R/L`
- 共振周波数: `ω_0 = (1-D)/sqrt(L*C)`
- 品質係数: `Q = (1-D)*R*sqrt(C/L)`

#### 4.2.2 線形-出力伝達関数
```
G_vg(s) = 1/(1-D) * 1 / (1 + s/(ω_0*Q) + s^2/ω_0^2)
```

### 4.3 PI制御器設計

#### 4.3.1 電流ループ設計
**設計制約:**
- f_ci ≤ f_sw/10
- PM_i ≥ 45° (推奨 ≥ 60°)
- GM_i ≥ 10dB

**PI制御器:**
```
C_i(s) = K_pi * (1 + 1/(Ti_i*s))
```

#### 4.3.2 電圧ループ設計
**設計制約:**
- f_cv = f_ci/5 ~ f_ci/10
- f_cv ≤ f_rhpz/5 (最悪条件)
- PM_v ≥ 60°
- GM_v ≥ 10dB

**PI制御器:**
```
C_v(s) = K_pv * (1 + 1/(Ti_v*s))
```

## 5. 実装仕様

### 5.1 プログラム構造

**メインモジュール:** `boost_converter_designer.py`

#### 5.1.1 クラス設計
```python
class BoostConverterDesigner:
    """メイン設計クラス"""
    def __init__(self)
    def load_config(self, filepath)
    def design_converter(self)
    def generate_reports(self)

class ConverterModel:
    """コンバーターモデルクラス"""
    def __init__(self, L, C, R, D)
    def get_state_space_model(self)
    def get_transfer_functions(self)
    def calculate_characteristics(self)

class PIController:
    """PI制御器設計クラス"""
    def __init__(self, plant_tf)
    def design_current_loop(self, f_ci, pm_target)
    def design_voltage_loop(self, f_cv, pm_target)
    def analyze_stability(self)
```

### 5.2 数値計算精度要求

**精度基準:**
- 周波数計算: ±0.1%
- 位相余裕: ±1°
- ゲイン計算: ±0.1dB
- 伝達関数係数: 有効桁数10桁以上

**数値安定性対策:**
- ゼロ除算チェック
- 条件数評価
- NaN/Inf検出
- 警告システム

## 6. 検証仕様

### 6.1 単体テスト要求

**テスト対象:**
- 状態空間行列計算
- 伝達関数導出
- PI制御器設計
- 安定性解析
- Excel I/O

**テストカバレッジ:** ≥95%

### 6.2 統合テスト要求

**テストシナリオ:**
1. 正常設計フロー
2. 制約違反ケース
3. エッジケース (極端なパラメータ)
4. 数値精度検証

### 6.3 性能要求

**実行時間:** <10秒 (標準PC環境)
**メモリ使用量:** <100MB
**ファイルサイズ:** Excel <1MB, HTML <5MB

## 7. エラーハンドリング仕様

### 7.1 パラメータ検証

**必須チェック項目:**
- Duty比範囲: 0 < D < 1
- 昇圧条件: V_out > V_in
- 正値チェック: L, C, R > 0
- CCM条件: 連続導通モード確認

### 7.2 設計失敗時の対応

**失敗条件:**
- 安定性基準未達
- 制約違反
- 数値計算エラー

**対応動作:**
- 詳細エラーメッセージ出力
- 代替パラメータ提案
- 部分結果保存

## 8. 文書化要求

### 8.1 コード文書化

**Docstring要求:**
- 関数目的
- 引数・戻り値型
- 数式参照
- 使用例

### 8.2 技術文書要求

**HTML文書内容:**
- 設計理論解説
- 数式導出過程
- 計算結果検証
- 設計トレードオフ分析

## 9. 品質保証

### 9.1 コード品質

**品質基準:**
- PEP8準拠
- 型ヒント完備
- 例外処理適切
- ログ出力充実

### 9.2 数学的正確性

**検証方法:**
- 理論値との比較
- 商用ツールとの比較
- 文献値との照合
- ベンチマークテスト

この詳細仕様書により、実装時の曖昧さを排除し、プロフェッショナル級の品質を保証する。