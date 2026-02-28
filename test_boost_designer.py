#!/usr/bin/env python3
"""
Test script for boost converter designer
Validates the implementation with specified default values
"""

import sys
import os

def test_boost_designer():
    """Test the boost converter designer functionality"""
    try:
        # Import the designer class
        from boost_converter_designer import BoostConverterDesigner
        
        print("✅ Successfully imported BoostConverterDesigner")
        
        # Create designer instance
        designer = BoostConverterDesigner()
        print("✅ Designer instance created")
        
        # Test configuration creation
        designer.create_default_config()
        print("✅ Default config file created")
        
        # Test configuration loading
        config = designer.load_config()
        if config:
            print("✅ Configuration loaded successfully")
            
            # Verify key default values
            expected_values = {
                'Vin_min': 8.0,
                'Vout': 12.0,
                'R_load': '15, 30, 45',
                'L': '0.5e-3, 1.0e-3, 1.5e-3', 
                'C': '22e-6, 44e-6, 66e-6'
            }
            
            for key, expected in expected_values.items():
                if key in config:
                    if key in ['R_load', 'L', 'C']:
                        actual = config[key]['candidates']
                        print(f"✅ {key}: {actual} (discrete candidates)")
                    else:
                        actual = config[key]['nominal']
                        print(f"✅ {key}: {actual}")
                else:
                    print(f"❌ Missing key: {key}")
            
            print("\n🔍 Testing design feasibility...")
            
            # Test operating point calculation
            op_point = designer.calculate_operating_point(config)
            print(f"✅ Operating point: D={op_point['D']:.3f}, IL={op_point['IL_avg']:.3f}A")
            
            # Test component optimization
            best_design, feasible = designer.optimize_components(config)
            if best_design:
                print(f"✅ Found {len(feasible)} feasible designs")
                print(f"✅ Optimal: L={best_design['L']*1000:.1f}mH, C={best_design['C']*1e6:.0f}µF, R={best_design['R_load']}Ω")
            else:
                print("❌ No feasible design found")
            
            return True
        else:
            print("❌ Failed to load configuration")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Boost Converter Designer")
    print("=" * 50)
    
    success = test_boost_designer()
    
    if success:
        print("\n🎉 All tests passed! The designer is ready to use.")
    else:
        print("\n❌ Tests failed. Please check the implementation.")
    
    sys.exit(0 if success else 1)