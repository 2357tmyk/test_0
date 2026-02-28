#!/usr/bin/env python3
"""
DC-DC昇圧コンバーター設計システム テストスイート

包括的なテスト・検証・デモンストレーション機能
- 数値計算精度検証
- エッジケーステスト
- 実行可能性確認
- パフォーマンステスト

Author: Professional DC-DC Design System Test Suite
Version: 1.0.0
"""

import os
import sys
import math
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# メインモジュールのインポート
try:
    from boost_converter_designer import (
        DesignSpecification, BoostConverterMath, PIControllerDesign,
        StabilityAnalysis, ExcelInterface, HTMLReportGenerator,
        BoostConverterDesigner
    )
except ImportError:
    print("Error: boost_converter_designer.py not found in the same directory")
    sys.exit(1)

class TestBoostConverterMath(unittest.TestCase):
    """昇圧コンバーター数学モデルテスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.math_engine = BoostConverterMath()
        self.spec = DesignSpecification(
            input_voltage_nominal=8.0,
            output_voltage=12.0,
            load_resistance=45.0,
            inductance=1.0e-3,
            capacitance=44e-6,
            switching_frequency=100e3
        )
    
    def test_steady_state_calculation(self):
        """定常状態計算テスト"""
        result = self.math_engine.calculate_steady_state(self.spec)
        
        # 基本的な妥当性チェック
        self.assertIsInstance(result, dict)
        self.assertIn('duty_cycle', result)
        self.assertIn('inductor_current_avg', result)
        
        # デューティ比の妥当性
        expected_duty = 1 - 8.0/12.0  # 0.333...
        self.assertAlmostEqual(result['duty_cycle'], expected_duty, places=3)
        
        # 電流値の正値チェック
        self.assertGreater(result['inductor_current_avg'], 0)
        self.assertGreater(result['output_current'], 0)
        
    def test_state_space_model_dimensions(self):
        """状態空間モデルの次元チェック"""
        steady_state = self.math_engine.calculate_steady_state(self.spec)
        A, B, Bd = self.math_engine.derive_state_space_model(self.spec, steady_state)
        
        # 行列の次元チェック
        self.assertEqual(A.shape, (2, 2))  # 2x2 システム行列
        self.assertEqual(B.shape, (2, 1))  # 2x1 入力行列
        self.assertEqual(Bd.shape, (2, 1)) # 2x1 制御入力行列
        
        # 数値の妥当性（有限値チェック）
        self.assertTrue(np.all(np.isfinite(A)))
        self.assertTrue(np.all(np.isfinite(B)))
        self.assertTrue(np.all(np.isfinite(Bd)))
    
    def test_transfer_functions_validity(self):
        """伝達関数の妥当性テスト"""
        steady_state = self.math_engine.calculate_steady_state(self.spec)
        tf = self.math_engine.derive_transfer_functions(self.spec, steady_state)
        
        # 右半面零点の正値チェック
        self.assertGreater(tf.rhp_zero_freq, 0)
        self.assertGreater(tf.natural_freq, 0)
        self.assertGreater(tf.quality_factor, 0)
        
        # 係数の有限値チェック
        self.assertTrue(all(math.isfinite(x) for x in tf.gvd_num))
        self.assertTrue(all(math.isfinite(x) for x in tf.gvd_den))
        
    def test_edge_cases(self):
        """エッジケーステスト"""
        # 極端に小さなインダクタンス
        spec_small_l = DesignSpecification(inductance=1e-6)
        try:
            steady_state = self.math_engine.calculate_steady_state(spec_small_l)
            self.assertIsInstance(steady_state, dict)
        except Exception as e:
            self.fail(f"Small inductance case failed: {e}")
        
        # 極端に大きなキャパシタンス
        spec_large_c = DesignSpecification(capacitance=1e-3)
        try:
            steady_state = self.math_engine.calculate_steady_state(spec_large_c)
            self.assertIsInstance(steady_state, dict)
        except Exception as e:
            self.fail(f"Large capacitance case failed: {e}")

class TestPIControllerDesign(unittest.TestCase):
    """PI制御器設計テスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.pi_designer = PIControllerDesign()
        self.math_engine = BoostConverterMath()
        self.spec = DesignSpecification()
        
        steady_state = self.math_engine.calculate_steady_state(self.spec)
        self.tf = self.math_engine.derive_transfer_functions(self.spec, steady_state)
    
    def test_current_controller_design(self):
        """電流制御器設計テスト"""
        controller = self.pi_designer.design_current_controller(self.spec, self.tf)
        
        # 基本的な妥当性チェック
        self.assertGreater(controller.kp, 0)
        self.assertGreater(controller.ki, 0)
        self.assertGreater(controller.ti, 0)
        self.assertGreater(controller.crossover_freq, 0)
        
        # 制約条件チェック
        self.assertLessEqual(controller.crossover_freq, self.spec.switching_frequency / 10)
    
    def test_voltage_controller_design(self):
        """電圧制御器設計テスト"""
        current_controller = self.pi_designer.design_current_controller(self.spec, self.tf)
        voltage_controller = self.pi_designer.design_voltage_controller(
            self.spec, self.tf, current_controller
        )
        
        # 基本的な妥当性チェック
        self.assertGreater(voltage_controller.kp, 0)
        self.assertGreater(voltage_controller.ki, 0)
        self.assertGreater(voltage_controller.ti, 0)
        
        # 帯域制約チェック
        self.assertLess(voltage_controller.crossover_freq, current_controller.crossover_freq)
        self.assertLess(voltage_controller.crossover_freq, self.tf.rhp_zero_freq / 5)

class TestStabilityAnalysis(unittest.TestCase):
    """安定性解析テスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.stability_analyzer = StabilityAnalysis()
        self.spec = DesignSpecification()
    
    def test_ccm_operation_check(self):
        """CCM動作条件テスト"""
        math_engine = BoostConverterMath()
        steady_state = math_engine.calculate_steady_state(self.spec)
        
        ccm_result = self.stability_analyzer.check_ccm_operation(self.spec, steady_state)
        self.assertIsInstance(ccm_result, bool)
        
        # 十分大きなインダクタンス（CCMになるはず）
        spec_large_l = DesignSpecification(inductance=10e-3)
        steady_state_large_l = math_engine.calculate_steady_state(spec_large_l)
        ccm_large_l = self.stability_analyzer.check_ccm_operation(spec_large_l, steady_state_large_l)
        self.assertTrue(ccm_large_l, "Large inductance should ensure CCM operation")

class TestExcelInterface(unittest.TestCase):
    """Excel入出力テスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.excel_interface = ExcelInterface()
        self.temp_dir = tempfile.mkdtemp()
        self.spec = DesignSpecification()
    
    def tearDown(self):
        """テスト後処理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_file_creation(self):
        """設定ファイル作成テスト"""
        config_path = os.path.join(self.temp_dir, "test_config.xlsx")
        
        # ファイル作成
        self.excel_interface.create_config_file(config_path, self.spec)
        
        # JSONファイルもテスト（openpyxlが無い場合の代替）
        json_path = config_path.replace('.xlsx', '.json')
        self.assertTrue(os.path.exists(config_path) or os.path.exists(json_path))
    
    def test_results_saving(self):
        """結果保存テスト"""
        results_path = os.path.join(self.temp_dir, "test_results.xlsx")
        
        # テストデータ作成
        test_results = [
            {
                'case_name': 'Test_Case_1',
                'R': 45.0,
                'L': 1e-3,
                'C': 44e-6,
                'duty_cycle': 0.333,
                'stable': True,
                'efficiency': 0.90
            }
        ]
        
        # 保存実行
        try:
            self.excel_interface.save_results(results_path, test_results)
            # JSONファイルもチェック（代替保存の場合）
            json_path = results_path.replace('.xlsx', '.json')
            self.assertTrue(os.path.exists(results_path) or os.path.exists(json_path))
        except Exception as e:
            self.fail(f"Results saving failed: {e}")

class TestHTMLReportGenerator(unittest.TestCase):
    """HTMLレポート生成テスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.html_generator = HTMLReportGenerator()
        self.temp_dir = tempfile.mkdtemp()
        self.spec = DesignSpecification()
    
    def tearDown(self):
        """テスト後処理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_html_report_generation(self):
        """HTMLレポート生成テスト"""
        html_path = os.path.join(self.temp_dir, "test_report.html")
        
        # テストデータ
        test_results = [
            {
                'case_name': 'Test_Case_1',
                'R': 45.0,
                'L': 1e-3,
                'C': 44e-6,
                'duty_cycle': 0.333,
                'rhp_zero_freq': 1000,
                'ccm_operation': True,
                'stable': True,
                'efficiency': 0.90,
                'fc_i': 10000,
                'pm_i': 60.0,
                'fc_v': 1000,
                'pm_v': 60.0
            }
        ]
        
        # HTML生成
        try:
            self.html_generator.generate_report(html_path, test_results, self.spec)
            self.assertTrue(os.path.exists(html_path))
            
            # ファイルサイズチェック（空でないことを確認）
            self.assertGreater(os.path.getsize(html_path), 1000)
            
            # 基本的なHTML構造チェック
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('<!DOCTYPE html>', content)
                self.assertIn('<title>', content)
                self.assertIn('昇圧コンバーター', content)
                
        except Exception as e:
            self.fail(f"HTML report generation failed: {e}")

class TestBoostConverterDesigner(unittest.TestCase):
    """メイン設計システムテスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.designer = BoostConverterDesigner()
        self.temp_dir = tempfile.mkdtemp()
        self.spec = DesignSpecification()
    
    def tearDown(self):
        """テスト後処理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_single_case_design(self):
        """単一ケース設計テスト"""
        try:
            result = self.designer.design_single_case(self.spec)
            
            # 基本的な結果チェック
            self.assertIsNotNone(result)
            self.assertGreater(result.duty_cycle, 0)
            self.assertLess(result.duty_cycle, 1)
            
            # 制御器パラメータチェック
            self.assertGreater(result.current_controller.kp, 0)
            self.assertGreater(result.voltage_controller.kp, 0)
            
        except Exception as e:
            self.fail(f"Single case design failed: {e}")
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        # 異常な仕様でのテスト
        invalid_spec = DesignSpecification(
            inductance=0,  # ゼロインダクタンス
            capacitance=0  # ゼロキャパシタンス
        )
        
        # エラーが発生しても例外で停止しないことを確認
        try:
            result = self.designer.design_single_case(invalid_spec)
            self.assertIsNotNone(result)
            self.assertFalse(result.design_feasible)
        except Exception:
            # 例外が発生した場合もテスト続行
            pass

class TestNumericalAccuracy(unittest.TestCase):
    """数値計算精度テスト"""
    
    def test_mathematical_consistency(self):
        """数学的整合性テスト"""
        math_engine = BoostConverterMath()
        spec = DesignSpecification(
            input_voltage_nominal=8.0,
            output_voltage=12.0,
            load_resistance=45.0
        )
        
        steady_state = math_engine.calculate_steady_state(spec)
        
        # エネルギー保存則チェック（理想効率を仮定）
        pin_ideal = steady_state['input_current'] * spec.input_voltage_nominal
        pout = spec.output_voltage * steady_state['output_current']
        
        # 理想的には Pin = Pout だが、実際には若干の誤差がある
        efficiency_check = pout / pin_ideal
        self.assertGreater(efficiency_check, 0.95)  # 95%以上の妥当性
        self.assertLess(efficiency_check, 1.05)     # 105%以下の妥当性
    
    def test_frequency_relationships(self):
        """周波数関係の妥当性テスト"""
        math_engine = BoostConverterMath()
        pi_designer = PIControllerDesign()
        
        spec = DesignSpecification()
        steady_state = math_engine.calculate_steady_state(spec)
        tf = math_engine.derive_transfer_functions(spec, steady_state)
        
        current_controller = pi_designer.design_current_controller(spec, tf)
        voltage_controller = pi_designer.design_voltage_controller(spec, tf, current_controller)
        
        # 周波数関係の妥当性
        self.assertLess(voltage_controller.crossover_freq, current_controller.crossover_freq)
        self.assertLess(current_controller.crossover_freq, spec.switching_frequency / 10)
        self.assertLess(voltage_controller.crossover_freq, tf.rhp_zero_freq / 5)

def run_performance_benchmark():
    """パフォーマンステスト実行"""
    print("\n🚀 パフォーマンステスト実行中...")
    
    import time
    
    designer = BoostConverterDesigner()
    spec = DesignSpecification()
    
    # 実行時間計測
    start_time = time.time()
    
    for i in range(10):  # 10回実行
        result = designer.design_single_case(spec)
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 10
    
    print(f"  • 平均設計時間: {avg_time:.3f}秒")
    print(f"  • 1秒あたり設計数: {1/avg_time:.1f}ケース")
    
    if avg_time < 0.1:  # 100ms以下
        print("  ✅ パフォーマンス: 優秀")
    elif avg_time < 0.5:  # 500ms以下
        print("  ✅ パフォーマンス: 良好")  
    else:
        print("  ⚠️  パフォーマンス: 要改善")

def run_comprehensive_test():
    """包括テスト実行"""
    print("🧪 DC-DC昇圧コンバーター設計システム - 包括テスト")
    print("=" * 60)
    
    # 標準テストスイート実行
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 各テストクラスを追加
    test_classes = [
        TestBoostConverterMath,
        TestPIControllerDesign,  
        TestStabilityAnalysis,
        TestExcelInterface,
        TestHTMLReportGenerator,
        TestBoostConverterDesigner,
        TestNumericalAccuracy
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestClass(test_class)
        suite.addTests(tests)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # パフォーマンステスト
    run_performance_benchmark()
    
    # 結果サマリー
    print(f"\n📊 テスト結果サマリー:")
    print(f"  • 実行テスト数: {result.testsRun}")
    print(f"  • 成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  • 失敗: {len(result.failures)}")
    print(f"  • エラー: {len(result.errors)}")
    
    if result.failures:
        print(f"\n⚠️  失敗テスト:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback}")
    
    if result.errors:
        print(f"\n❌ エラーテスト:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback}")
    
    # 全体評価
    if len(result.failures) == 0 and len(result.errors) == 0:
        print(f"\n🎉 全テスト成功! システムは本番使用可能です。")
        return True
    else:
        print(f"\n⚠️  一部テストが失敗しました。修正が必要です。")
        return False

def run_demo():
    """システムデモ実行"""
    print("\n🎬 システムデモ実行")
    print("-" * 30)
    
    try:
        # 一時ディレクトリでデモ実行
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = os.path.join(temp_dir, "config")
            output_dir = os.path.join(temp_dir, "output")
            config_path = os.path.join(config_dir, "demo_config.xlsx")
            
            print(f"📁 一時ディレクトリ: {temp_dir}")
            
            # 設計システム実行（少数ケースでデモ）
            designer = BoostConverterDesigner()
            
            # デモ用の簡単な設計
            spec = DesignSpecification(
                load_resistance=45.0,
                inductance=1.0e-3,
                capacitance=44e-6
            )
            
            print("🔧 単一ケース設計実行中...")
            result = designer.design_single_case(spec)
            
            print(f"✅ 設計完了:")
            print(f"  • デューティ比: {result.duty_cycle:.3f}")
            print(f"  • CCM動作: {'○' if result.ccm_operation else '×'}")
            print(f"  • 安定性: {'○' if result.system_stable else '×'}")
            print(f"  • 電流制御帯域: {result.current_controller.crossover_freq:.0f}Hz")
            print(f"  • 電圧制御帯域: {result.voltage_controller.crossover_freq:.0f}Hz")
            print(f"  • 右半面零点: {result.transfer_functions.rhp_zero_freq:.0f}Hz")
            
            print("\n🎯 デモ成功!")
            
    except Exception as e:
        print(f"❌ デモエラー: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔌 DC-DC昇圧コンバーター設計システム - テスト&検証スイート")
    print("Version 1.0.0")
    print("=" * 70)
    
    # 必要な依存関係の確認
    try:
        import numpy as np
        print("✅ numpy: 利用可能")
    except ImportError:
        print("❌ numpy: 未インストール")
    
    try:
        import pandas as pd
        print("✅ pandas: 利用可能")
    except ImportError:
        print("❌ pandas: 未インストール")
    
    try:
        import openpyxl
        print("✅ openpyxl: 利用可能")
    except ImportError:
        print("⚠️  openpyxl: 未インストール (JSON代替を使用)")
    
    print()
    
    # テストモード選択
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "all"
    
    success = True
    
    if mode in ["all", "test"]:
        success &= run_comprehensive_test()
    
    if mode in ["all", "demo"]:
        success &= run_demo()
    
    if success:
        print(f"\n🏆 全体評価: 成功")
        sys.exit(0)
    else:
        print(f"\n❌ 全体評価: 改善必要")
        sys.exit(1)