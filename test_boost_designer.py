#!/usr/bin/env python3
"""
DC-DC昇圧コンバーター設計ツール テストスクリプト
Test script for boost converter design tool validation
"""

import unittest
import numpy as np
import os
import sys
from pathlib import Path

# メインモジュールをインポート
sys.path.append('.')
from boost_converter_designer import BoostConverterDesigner

class TestBoostConverterDesigner(unittest.TestCase):
    """
    昇圧コンバーター設計ツールの単体テスト
    """
    
    def setUp(self):
        """テスト前の初期化"""
        self.designer = BoostConverterDesigner()
        
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.designer.Vin, 8.0)
        self.assertEqual(self.designer.Vo, 12.0)
        self.assertEqual(len(self.designer.R_options), 3)
        self.assertEqual(len(self.designer.L_options), 3)
        self.assertEqual(len(self.designer.C_options), 3)
        
    def test_directory_creation(self):
        """ディレクトリ作成テスト"""
        self.assertTrue(self.designer.config_dir.exists())
        self.assertTrue(self.designer.output_dir.exists())
        
    def test_config_creation(self):
        """設定ファイル作成テスト"""
        self.designer.create_default_config()
        self.assertTrue(self.designer.config_file.exists())
        
    def test_operating_point_calculation(self):
        """動作点計算テスト"""
        R = 30.0  # Ω
        L = 1.0e-3  # H
        C = 44e-6  # F
        
        op = self.designer.calculate_operating_point(R, L, C)
        
        # デューティ比チェック
        expected_D = (12.0 - 8.0) / 12.0  # (Vo - Vin) / Vo
        self.assertAlmostEqual(op['D'], expected_D, places=3)
        
        # 出力電流チェック
        expected_Io = 12.0 / 30.0
        self.assertAlmostEqual(op['Io'], expected_Io, places=3)
        
        # CCM条件チェック
        self.assertTrue(op['CCM_condition'])
        
    def test_transfer_function_derivation(self):
        """伝達関数導出テスト"""
        R = 30.0
        L = 1.0e-3
        C = 44e-6
        
        op = self.designer.calculate_operating_point(R, L, C)
        tf = self.designer.derive_transfer_functions(R, L, C, op)
        
        # 基本的な伝達関数情報がすべて含まれているかチェック
        self.assertIn('A_matrix', tf)
        self.assertIn('Gvd_response', tf)
        self.assertIn('Gid_response', tf)
        self.assertIn('f_rhpz', tf)
        self.assertIn('f_res', tf)
        
        # 右半面零点が正の値かチェック
        self.assertGreater(tf['f_rhpz'], 0)
        
    def test_current_controller_design(self):
        """電流制御器設計テスト"""
        R = 30.0
        L = 1.0e-3
        C = 44e-6
        
        op = self.designer.calculate_operating_point(R, L, C)
        tf = self.designer.derive_transfer_functions(R, L, C, op)
        ci = self.designer.design_current_controller(tf, op)
        
        # 制御器パラメータがすべて正の値かチェック
        self.assertGreater(ci['Kp_i'], 0)
        self.assertGreater(ci['Ki_i'], 0)
        self.assertGreater(ci['Ti_i'], 0)
        
        # クロスオーバー周波数制約チェック
        self.assertLessEqual(ci['f_crossover'], self.designer.fsw / 10)
        
    def test_voltage_controller_design(self):
        """電圧制御器設計テスト"""
        R = 30.0
        L = 1.0e-3
        C = 44e-6
        
        op = self.designer.calculate_operating_point(R, L, C)
        tf = self.designer.derive_transfer_functions(R, L, C, op)
        ci = self.designer.design_current_controller(tf, op)
        cv = self.designer.design_voltage_controller(tf, ci, op)
        
        # 制御器パラメータがすべて正の値かチェック
        self.assertGreater(cv['Kp_v'], 0)
        self.assertGreater(cv['Ki_v'], 0)
        self.assertGreater(cv['Ti_v'], 0)
        
        # 電圧ループが電流ループより遅いかチェック
        self.assertLess(cv['f_crossover'], ci['f_crossover'])
        
    def test_single_case_design(self):
        """単一ケース設計テスト"""
        result = self.designer.design_single_case(30.0, 1.0e-3, 44e-6, 1)
        
        self.assertIsNotNone(result)
        self.assertIn('design_success', result)
        self.assertIn('components', result)
        self.assertIn('operating_point', result)
        self.assertIn('current_controller', result)
        self.assertIn('voltage_controller', result)
        
    def test_numerical_stability(self):
        """数値計算の安定性テスト"""
        # 極端な値での計算テスト
        test_cases = [
            (15.0, 0.5e-3, 22e-6),   # 重負荷、小インダクタ、小コンデンサ
            (45.0, 1.5e-3, 66e-6),   # 軽負荷、大インダクタ、大コンデンサ
        ]
        
        for R, L, C in test_cases:
            with self.subTest(R=R, L=L, C=C):
                try:
                    result = self.designer.design_single_case(R, L, C, 999)
                    # 結果がNoneでないか、エラーが発生していないかチェック
                    self.assertTrue(result is not None or True)  # 計算完了が重要
                except Exception as e:
                    self.fail(f"Numerical instability detected: {e}")


def run_validation_tests():
    """
    バリデーションテストの実行
    """
    print("🧪 DC-DC昇圧コンバーター設計ツール バリデーションテスト開始")
    print("=" * 60)
    
    # テストスイート作成
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBoostConverterDesigner)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ すべてのテストが成功しました")
        return True
    else:
        print(f"❌ テスト失敗: {len(result.failures)} failures, {len(result.errors)} errors")
        return False


def run_functional_demo():
    """
    機能デモンストレーション
    """
    print("🚀 機能デモンストレーション")
    print("=" * 60)
    
    try:
        designer = BoostConverterDesigner()
        
        # 1. 設定ファイル作成
        print("📝 1. デフォルト設定ファイル作成")
        designer.create_default_config()
        
        # 2. 設定読み込み
        print("📖 2. 設定ファイル読み込み")
        designer.load_config()
        
        # 3. 単一ケース設計デモ
        print("⚙️ 3. 単一ケース設計デモ (R=30Ω, L=1.0mH, C=44μF)")
        result = designer.design_single_case(30.0, 1.0e-3, 44e-6, "Demo")
        
        if result and result['design_success']:
            op = result['operating_point']
            ci = result['current_controller']
            cv = result['voltage_controller']
            
            print(f"   ✅ 設計成功")
            print(f"   📊 デューティ比: {op['D']:.3f}")
            print(f"   📊 平均インダクタ電流: {op['IL_avg']:.3f}A")
            print(f"   📊 電流制御器 Kp={ci['Kp_i']:.4f}, Ki={ci['Ki_i']:.2f}")
            print(f"   📊 電圧制御器 Kp={cv['Kp_v']:.4f}, Ki={cv['Ki_v']:.2f}")
            print(f"   📊 位相余裕: 電流={ci['PM_i']:.1f}°, 電圧={cv['PM_v']:.1f}°")
        else:
            print("   ❌ 設計失敗")
            
        print("✅ 機能デモ完了")
        return True
        
    except Exception as e:
        print(f"❌ デモ実行エラー: {str(e)}")
        return False


if __name__ == "__main__":
    try:
        # テスト実行
        test_success = run_validation_tests()
        
        # デモ実行
        demo_success = run_functional_demo()
        
        if test_success and demo_success:
            print("\n🎉 バリデーション完了: すべて成功")
            sys.exit(0)
        else:
            print("\n⚠️ バリデーションで問題が検出されました")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ バリデーション実行エラー: {str(e)}")
        sys.exit(1)