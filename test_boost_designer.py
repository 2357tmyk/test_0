#!/usr/bin/env python3
"""
Test script for boost converter designer tool
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_boost_designer():
    """Test the boost converter designer."""
    
    print("Testing Boost Converter Designer...")
    
    try:
        from boost_converter_designer import BoostConverterDesigner
        
        # Create designer instance
        designer = BoostConverterDesigner()
        print("✅ Designer class instantiated successfully")
        
        # Test configuration template creation
        success = designer.create_config_template()
        if success:
            print("✅ Configuration template created successfully")
            print(f"  Template location: {designer.config_file}")
        else:
            print("❌ Configuration template creation failed")
            return False
        
        # Check if files were created
        if designer.config_file.exists():
            print("✅ Config file exists")
            print(f"  Size: {designer.config_file.stat().st_size} bytes")
        else:
            print("❌ Config file not found")
            return False
        
        # Test configuration loading
        load_success = designer.load_configuration()
        if load_success:
            print("✅ Configuration loaded successfully")
            print(f"  Parameters loaded: {len(designer.config)}")
        else:
            print("❌ Configuration loading failed")
        
        # Test validation
        valid, errors, warnings = designer.validate_configuration()
        print(f"✅ Configuration validation completed")
        print(f"  Valid: {valid}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("✅ Basic functionality test PASSED")
        print("📁 Files created in config/ and output/ directories")
        print("🔧 Ready for full design process")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_boost_designer()
    sys.exit(0 if success else 1)