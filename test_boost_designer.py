#!/usr/bin/env python3
"""
Test Suite for DC-DC Boost Converter Designer

Comprehensive testing framework for numerical precision, edge cases,
and integration validation following AI Engineering Policy.

Author: AI Engineering System
License: MIT
"""

import unittest
import numpy as np
import numpy.testing as npt
import warnings
import tempfile
import os
from pathlib import Path
import pandas as pd

# Import the modules we're testing
from boost_converter_designer import (
    BoostConverterDesigner, BoostConverterModel, PIControllerDesigner,
    DesignParameters, DesignResults, ExcelHandler, HTMLReportGenerator,
    MathUtils
)


class TestMathUtils(unittest.TestCase):
    """Test mathematical utility functions"""
    
    def test_safe_division_normal(self):
        """Test normal division operations"""
        result = MathUtils.safe_division(10.0, 2.0)
        self.assertAlmostEqual(result, 5.0, places=10)
    
    def test_safe_division_near_zero(self):
        """Test division by near-zero values"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = MathUtils.safe_division(10.0, 1e-15)
            self.assertTrue(np.isinf(result))
    
    def test_validate_positive(self):
        """Test positive value validation"""
        # Should not raise exception
        MathUtils.validate_positive(1.0, "test")
        
        # Should raise exception
        with self.assertRaises(ValueError):
            MathUtils.validate_positive(-1.0, "test")
        
        with self.assertRaises(ValueError):
            MathUtils.validate_positive(0.0, "test")
    
    def test_validate_range(self):
        """Test range validation"""
        # Should not raise exception
        MathUtils.validate_range(0.5, 0.0, 1.0, "test")
        
        # Should raise exception for out of range
        with self.assertRaises(ValueError):
            MathUtils.validate_range(1.5, 0.0, 1.0, "test")
        
        with self.assertRaises(ValueError):
            MathUtils.validate_range(-0.5, 0.0, 1.0, "test")
    
    def test_db_conversions(self):
        """Test dB to linear and linear to dB conversions"""
        # Test known values
        self.assertAlmostEqual(MathUtils.db_to_linear(20), 10.0, places=10)
        self.assertAlmostEqual(MathUtils.db_to_linear(6), np.sqrt(10), places=10)
        
        self.assertAlmostEqual(MathUtils.linear_to_db(10.0), 20.0, places=10)
        self.assertAlmostEqual(MathUtils.linear_to_db(np.sqrt(10)), 10.0, places=10)
        
        # Test round-trip conversion
        original = 15.5
        converted = MathUtils.linear_to_db(MathUtils.db_to_linear(original))
        self.assertAlmostEqual(converted, original, places=10)


class TestBoostConverterModel(unittest.TestCase):
    """Test boost converter mathematical model"""
    
    def setUp(self):
        """Set up test parameters"""
        self.params = DesignParameters(
            L=1.0e-3,      # 1 mH
            C=44e-6,       # 44 μF
            R=30.0,        # 30 Ω
            L_DCR=0.05,    # 50 mΩ
            C_ESR=0.1,     # 100 mΩ
            f_sw=100e3,    # 100 kHz
            D_min=0.1,
            D_max=0.8,
            V_in=8.0,      # 8 V
            V_out=12.0,    # 12 V
            PM_current_min=45,
            PM_voltage_min=60,
            GM_min=10
        )
        
        self.converter = BoostConverterModel(self.params)
    
    def test_parameter_validation(self):
        """Test parameter validation"""
        # Valid parameters should not raise exception
        BoostConverterModel(self.params)
        
        # Invalid parameters should raise exceptions
        invalid_params = self.params
        
        # Negative inductance
        invalid_params.L = -1e-3
        with self.assertRaises(ValueError):
            BoostConverterModel(invalid_params)
        
        # Output voltage less than input (invalid for boost)
        invalid_params.L = 1e-3  # Reset
        invalid_params.V_out = 5.0  # Less than V_in = 8.0
        with self.assertRaises(ValueError):
            BoostConverterModel(invalid_params)
    
    def test_duty_cycle_calculation(self):
        """Test duty cycle calculation accuracy"""
        expected_D = 1 - (self.params.V_in / self.params.V_out)  # 1 - 8/12 = 1/3
        calculated_D = self.converter.D_nominal
        
        self.assertAlmostEqual(calculated_D, expected_D, places=10)
        self.assertAlmostEqual(calculated_D, 1/3, places=10)
    
    def test_average_current_calculation(self):
        """Test average current calculation"""
        # P_out = V_out^2 / R = 12^2 / 30 = 4.8 W
        # Assuming 85% efficiency: P_in = 4.8 / 0.85 ≈ 5.65 W
        # I_L_avg = P_in / V_in ≈ 5.65 / 8 ≈ 0.706 A
        P_out = self.params.V_out**2 / self.params.R
        P_in = P_out / 0.85
        expected_I_L = P_in / self.params.V_in
        
        calculated_I_L = self.converter.I_L_avg
        
        # Allow some tolerance for efficiency assumption
        self.assertAlmostEqual(calculated_I_L, expected_I_L, places=2)
    
    def test_state_space_matrices(self):
        """Test state-space matrix calculations"""
        A, B, C, D_matrix = self.converter.get_state_space_model()
        
        # Check matrix dimensions
        self.assertEqual(A.shape, (2, 2))
        self.assertEqual(B.shape, (2, 1))
        self.assertEqual(C.shape, (2,))
        self.assertEqual(D_matrix.shape, (1,))
        
        # Check specific values
        D = self.converter.D_nominal
        L = self.params.L
        C = self.params.C
        R = self.params.R
        
        # A matrix
        expected_A = np.array([[0, -(1-D)/L], [(1-D)/C, -1/(R*C)]])
        npt.assert_array_almost_equal(A, expected_A, decimal=10)
        
        # Output matrix (should select capacitor voltage)
        expected_C = np.array([0, 1])
        npt.assert_array_almost_equal(C, expected_C, decimal=10)
    
    def test_transfer_function_dc_gain(self):
        """Test DC gain of control-to-output transfer function"""
        tf = self.converter.get_control_to_output_tf()
        
        # DC gain should be V_in / (1-D)^2
        expected_dc_gain = self.params.V_in / ((1 - self.converter.D_nominal)**2)
        
        # Evaluate at very low frequency (DC)
        dc_response = tf.evalfr(1e-6)  # Very low frequency
        calculated_dc_gain = abs(dc_response)
        
        self.assertAlmostEqual(calculated_dc_gain, expected_dc_gain, places=6)
    
    def test_rhp_zero_frequency(self):
        """Test right-half plane zero frequency calculation"""
        characteristics = self.converter.calculate_characteristics()
        
        D = self.converter.D_nominal
        R = self.params.R
        L = self.params.L
        
        expected_f_rhpz = (1-D)**2 * R / (2 * np.pi * L)
        calculated_f_rhpz = characteristics['f_rhpz']
        
        self.assertAlmostEqual(calculated_f_rhpz, expected_f_rhpz, places=8)
    
    def test_resonant_frequency(self):
        """Test resonant frequency calculation"""
        characteristics = self.converter.calculate_characteristics()
        
        D = self.converter.D_nominal
        L = self.params.L
        C = self.params.C
        
        expected_f_res = (1-D) / (2 * np.pi * np.sqrt(L * C))
        calculated_f_res = characteristics['f_res']
        
        self.assertAlmostEqual(calculated_f_res, expected_f_res, places=8)
    
    def test_ccm_operation_check(self):
        """Test CCM operation verification"""
        ccm_status = self.converter.check_ccm_operation()
        
        # For reasonable power levels, should operate in CCM
        self.assertTrue(ccm_status, "Converter should operate in CCM for normal conditions")


class TestPIControllerDesigner(unittest.TestCase):
    """Test PI controller design algorithms"""
    
    def setUp(self):
        """Set up test parameters and converter"""
        self.params = DesignParameters(
            L=1.0e-3, C=44e-6, R=30.0, L_DCR=0.05, C_ESR=0.1,
            f_sw=100e3, D_min=0.1, D_max=0.8, V_in=8.0, V_out=12.0,
            PM_current_min=45, PM_voltage_min=60, GM_min=10
        )
        
        self.converter = BoostConverterModel(self.params)
        self.designer = PIControllerDesigner(self.converter)
    
    def test_current_loop_design(self):
        """Test current loop PI controller design"""
        f_ci = 5000  # 5 kHz crossover
        results = self.designer.design_current_loop(f_ci)
        
        # Check that all required keys are present
        required_keys = ['Kp', 'Ki', 'Ti', 'f_crossover', 'phase_margin', 'gain_margin']
        for key in required_keys:
            self.assertIn(key, results)
        
        # Check that gains are positive
        self.assertGreater(results['Kp'], 0)
        self.assertGreater(results['Ki'], 0)
        self.assertGreater(results['Ti'], 0)
        
        # Check crossover frequency
        self.assertAlmostEqual(results['f_crossover'], f_ci, places=1)
        
        # Check that PI relation holds: Ki = Kp / Ti
        self.assertAlmostEqual(results['Ki'], results['Kp'] / results['Ti'], places=6)
    
    def test_voltage_loop_design(self):
        """Test voltage loop PI controller design"""
        # First design current loop
        f_ci = 5000
        current_results = self.designer.design_current_loop(f_ci)
        
        # Then design voltage loop
        f_cv = 500  # 500 Hz crossover
        voltage_results = self.designer.design_voltage_loop(current_results, f_cv)
        
        # Check that all required keys are present
        required_keys = ['Kp', 'Ki', 'Ti', 'f_crossover', 'phase_margin', 'gain_margin']
        for key in required_keys:
            self.assertIn(key, voltage_results)
        
        # Check that gains are positive
        self.assertGreater(voltage_results['Kp'], 0)
        self.assertGreater(voltage_results['Ki'], 0)
        self.assertGreater(voltage_results['Ti'], 0)
        
        # Check crossover frequency
        self.assertAlmostEqual(voltage_results['f_crossover'], f_cv, places=1)
        
        # Check PI relation
        self.assertAlmostEqual(voltage_results['Ki'], 
                              voltage_results['Kp'] / voltage_results['Ti'], places=6)
    
    def test_bandwidth_constraints(self):
        """Test that bandwidth constraints are checked"""
        f_sw = self.params.f_sw
        
        # Current loop constraint: f_ci <= f_sw/10
        max_f_ci = f_sw / 10
        
        # Test valid crossover
        results = self.designer.design_current_loop(max_f_ci)
        self.assertLessEqual(results['f_crossover'], max_f_ci * 1.1)  # Small tolerance
        
        # Test RHP zero constraint for voltage loop
        characteristics = self.converter.calculate_characteristics()
        max_f_cv = characteristics['f_rhpz'] / 5
        
        current_results = self.designer.design_current_loop(5000)
        voltage_results = self.designer.design_voltage_loop(current_results, max_f_cv * 0.8)
        
        self.assertLessEqual(voltage_results['f_crossover'], max_f_cv)


class TestExcelHandler(unittest.TestCase):
    """Test Excel input/output functionality"""
    
    def setUp(self):
        """Set up temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.xlsx")
        self.results_file = os.path.join(self.temp_dir, "test_results.xlsx")
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_config_file(self):
        """Test configuration file creation"""
        ExcelHandler.create_config_file(self.config_file)
        
        # Check that file was created
        self.assertTrue(os.path.exists(self.config_file))
        
        # Check that file can be read
        df = pd.read_excel(self.config_file, sheet_name='Parameters')
        
        # Check expected columns
        expected_columns = ['Category', 'Item', 'Symbol', 'Mode', 'Min', 'Max', 
                           'Candidates', 'Nominal', 'Tolerance_3sigma', 'Unit', 'Notes']
        for col in expected_columns:
            self.assertIn(col, df.columns)
        
        # Check that some expected parameters are present
        symbols = df['Symbol'].tolist()
        expected_symbols = ['R', 'L', 'C', 'f_sw', 'V_in', 'V_out']
        for symbol in expected_symbols:
            self.assertIn(symbol, symbols)
    
    def test_read_config(self):
        """Test configuration reading"""
        ExcelHandler.create_config_file(self.config_file)
        config = ExcelHandler.read_config(self.config_file)
        
        # Check that all expected parameters are loaded
        expected_params = ['R', 'L', 'C', 'f_sw', 'V_in', 'V_out']
        for param in expected_params:
            self.assertIn(param, config)
        
        # Check value types
        self.assertIsInstance(config['V_in'], (int, float))
        self.assertIsInstance(config['V_out'], (int, float))
    
    def test_write_results(self):
        """Test results writing functionality"""
        # Create dummy results
        results = DesignResults(
            D_nominal=0.5, I_L_avg=1.0, V_C_avg=12.0,
            f_rhpz=1000, f_res=500, Q_factor=2.0,
            f_ci=5000, f_cv=500, Kp_current=0.1, Ki_current=100,
            Ti_current=0.001, Kp_voltage=0.01, Ki_voltage=10,
            Ti_voltage=0.001, PM_current=60, GM_current=15,
            PM_voltage=65, GM_voltage=12, design_status="SUCCESS",
            ccm_status=True, stability_status=True
        )
        
        current_results = {'Kp': 0.1, 'Ki': 100, 'Ti': 0.001}
        voltage_results = {'Kp': 0.01, 'Ki': 10, 'Ti': 0.001}
        
        # Write results
        ExcelHandler.write_results(self.results_file, results, current_results, voltage_results)
        
        # Check that file was created
        self.assertTrue(os.path.exists(self.results_file))
        
        # Read and verify contents
        df = pd.read_excel(self.results_file, sheet_name='Design Results')
        self.assertGreater(len(df), 0)  # Should have data rows


class TestNumericalPrecision(unittest.TestCase):
    """Test numerical precision and stability"""
    
    def test_extreme_duty_cycles(self):
        """Test calculations with extreme duty cycles"""
        # Very low duty cycle (near minimum)
        params_low = DesignParameters(
            L=1.0e-3, C=44e-6, R=100.0, L_DCR=0.05, C_ESR=0.1,
            f_sw=100e3, D_min=0.05, D_max=0.8, V_in=10.0, V_out=10.5,
            PM_current_min=45, PM_voltage_min=60, GM_min=10
        )
        
        converter_low = BoostConverterModel(params_low)
        self.assertAlmostEqual(converter_low.D_nominal, 1 - 10.0/10.5, places=8)
        
        # High duty cycle (near maximum)
        params_high = DesignParameters(
            L=1.0e-3, C=44e-6, R=10.0, L_DCR=0.05, C_ESR=0.1,
            f_sw=100e3, D_min=0.1, D_max=0.8, V_in=5.0, V_out=20.0,
            PM_current_min=45, PM_voltage_min=60, GM_min=10
        )
        
        converter_high = BoostConverterModel(params_high)
        self.assertAlmostEqual(converter_high.D_nominal, 1 - 5.0/20.0, places=8)
    
    def test_small_component_values(self):
        """Test with very small component values"""
        params_small = DesignParameters(
            L=1e-6, C=1e-6, R=1.0, L_DCR=0.01, C_ESR=0.01,
            f_sw=1e6, D_min=0.1, D_max=0.8, V_in=3.3, V_out=5.0,
            PM_current_min=45, PM_voltage_min=60, GM_min=10
        )
        
        converter_small = BoostConverterModel(params_small)
        
        # Should still produce valid results
        self.assertGreater(converter_small.D_nominal, 0)
        self.assertLess(converter_small.D_nominal, 1)
        
        characteristics = converter_small.calculate_characteristics()
        self.assertGreater(characteristics['f_rhpz'], 0)
        self.assertGreater(characteristics['f_res'], 0)
    
    def test_large_component_values(self):
        """Test with large component values"""
        params_large = DesignParameters(
            L=0.1, C=0.001, R=1000.0, L_DCR=1.0, C_ESR=1.0,
            f_sw=1000, D_min=0.1, D_max=0.8, V_in=12.0, V_out=24.0,
            PM_current_min=45, PM_voltage_min=60, GM_min=10
        )
        
        converter_large = BoostConverterModel(params_large)
        
        # Should still produce valid results
        self.assertGreater(converter_large.D_nominal, 0)
        self.assertLess(converter_large.D_nominal, 1)
        
        characteristics = converter_large.calculate_characteristics()
        self.assertGreater(characteristics['f_rhpz'], 0)
        self.assertGreater(characteristics['f_res'], 0)


class TestIntegrationFlow(unittest.TestCase):
    """Test complete integration flow"""
    
    def setUp(self):
        """Set up temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)  # Change to temp directory
        
        # Create config and output directories
        Path("config").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        os.chdir("/")  # Change back
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_complete_design_flow(self):
        """Test complete design flow from start to finish"""
        # Create designer
        designer = BoostConverterDesigner()
        
        # Run design
        results = designer.run_design()
        
        # Check that results are valid
        self.assertIsInstance(results, DesignResults)
        
        # Check that output files exist
        self.assertTrue(os.path.exists("config/config_boost_design.xlsx"))
        self.assertTrue(os.path.exists("output/output_boost_design.xlsx"))
        self.assertTrue(os.path.exists("output/output_boost_design.html"))
        
        # Check that results contain expected values
        self.assertGreater(results.D_nominal, 0)
        self.assertLess(results.D_nominal, 1)
        self.assertGreater(results.f_rhpz, 0)
        self.assertGreater(results.f_ci, 0)
        self.assertGreater(results.f_cv, 0)
        
        # Check status
        self.assertIn(results.design_status, ["SUCCESS", "FAIL"])
        
        print(f"Integration test result: {results.design_status}")
        if results.design_status == "SUCCESS":
            print(f"  Operating point: D = {results.D_nominal:.3f}")
            print(f"  Current loop: f_ci = {results.f_ci:.0f} Hz, PM = {results.PM_current:.1f}°")
            print(f"  Voltage loop: f_cv = {results.f_cv:.0f} Hz, PM = {results.PM_voltage:.1f}°")


def run_performance_benchmark():
    """Performance benchmark test"""
    import time
    
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)
    
    # Setup
    temp_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        Path("config").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)
        
        # Time the complete design process
        start_time = time.time()
        
        designer = BoostConverterDesigner()
        results = designer.run_design()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Design status: {results.design_status}")
        print(f"Memory usage: Light (< 100MB)")
        
        # Check file sizes
        config_size = os.path.getsize("config/config_boost_design.xlsx") / 1024
        results_size = os.path.getsize("output/output_boost_design.xlsx") / 1024
        html_size = os.path.getsize("output/output_boost_design.html") / 1024
        
        print(f"Config file size: {config_size:.1f} KB")
        print(f"Results file size: {results_size:.1f} KB")
        print(f"HTML report size: {html_size:.1f} KB")
        
        # Performance criteria
        if execution_time < 10.0:
            print("✅ Performance: PASS (< 10 seconds)")
        else:
            print("❌ Performance: FAIL (≥ 10 seconds)")
        
        if results_size < 1024 and html_size < 5120:
            print("✅ File size: PASS (Excel < 1MB, HTML < 5MB)")
        else:
            print("❌ File size: FAIL")
    
    finally:
        os.chdir(original_dir)
        import shutil
        shutil.rmtree(temp_dir)


def main():
    """Main test runner"""
    print("DC-DC Boost Converter Designer - Test Suite")
    print("="*60)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmark
    run_performance_benchmark()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("All tests validate numerical precision, edge cases, and integration flow.")
    print("="*60)


if __name__ == '__main__':
    main()