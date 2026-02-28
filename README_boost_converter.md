# Boost Converter Auto-Design Tool

## Overview

This is a comprehensive boost converter auto-design tool that follows rigorous AI engineering policies and state-space modeling principles. The tool automatically designs boost converters with dual-loop PI control, component optimization, and comprehensive stability analysis.

## Features

### 🔬 **Rigorous Mathematical Modeling**
- State-space modeling with small-signal linearization
- Transfer function derivation from first principles  
- Right-half-plane zero analysis and constraints
- Frequency domain stability analysis

### ⚡ **Dual-Loop PI Control Design**
- Inner current loop for fast transient response
- Outer voltage loop with reference tracking
- Automatic PI parameter calculation
- Phase and gain margin optimization

### 🎯 **Component Optimization**
- Discrete selection from E-series standard values
- Minimizes size, weight, and cost
- Ripple analysis and constraint verification
- Safety margin calculations with ±3σ tolerances

### 📊 **Professional Documentation**
- Excel configuration input/output
- HTML reports with mathematical equations
- Step-by-step design rationale
- Third-party review ready documentation

## Quick Start

1. **Run the tool:**
   ```bash
   python boost_converter_designer.py
   ```

2. **First run creates configuration template:**
   - `config/config_boost_design.xlsx` - Edit your specifications
   
3. **Edit configuration file with your requirements:**
   - Input/output voltages
   - Current ratings
   - Control bandwidth specifications
   - Component constraints

4. **Run again to generate design:**
   - `output/output_boost_design.xlsx` - Design results
   - `output/output_boost_design.html` - Detailed documentation

## Configuration File Format

The Excel configuration uses a structured format with these modes:

- **FIXED**: Absolute requirements (cannot be changed)
- **RANGE**: Continuous allowable range (min/max values)  
- **DISCRETE**: Specific candidate values (E-series components)

### Key Parameters

| Category | Parameter | Description |
|----------|-----------|-------------|
| Circuit Elements | L, C, R_L, R_C | Inductor, capacitor, resistances |
| Switching | f_sw, D_min, D_max | Frequency and duty ratio limits |
| Control | f_ci, f_cv, PM_min, GM_min | Bandwidth and stability margins |
| Input | Vin_min, Vin_max, Iin_max | Input specifications |
| Output | Vout, Iout_max, ripple limits | Output requirements |

## Design Methodology

### 1. **State-Space Model Derivation**
```
State variables: x = [iL, vC]ᵀ
State equation: dx/dt = Ax + Bu + Ed_in
Output equation: y = Cx
```

### 2. **Transfer Functions**
- **Gvd(s)**: Control-to-output voltage (voltage loop)
- **Gid(s)**: Control-to-inductor current (current loop)
- **RHP Zero**: f_z,RHP = R_load(1-D)²/(2πL)

### 3. **Control Design Constraints**
- Current loop: f_ci ≤ f_sw/10
- Voltage loop: f_cv ≤ f_ci/10  
- RHP constraint: f_cv ≤ f_z,RHP/5
- Stability: PM ≥ 45°, GM ≥ 10dB

### 4. **Component Selection**
Optimization objective:
```
minimize: α×L + β×C + γ/f_sw
subject to: ripple_constraints & stability_constraints
```

## Output Files

### Excel Output (`output_boost_design.xlsx`)
- **Design_Summary**: Requirements and results overview
- **Circuit_Components**: Selected component values with tolerances
- **Control_Parameters**: PI controller gains and performance
- **Analysis_Results**: Stability margins and verification

### HTML Documentation (`output_boost_design.html`)
- Mathematical derivations with MathJax equations
- Design flow explanation and rationale  
- Professional review-ready documentation
- Component selection justification

## Example Use Cases

1. **12V to 24V, 5A Converter**
   - Input: 12-16V, Output: 24V/5A
   - Target efficiency: >90%
   - Compact design with standard components

2. **Automotive Applications** 
   - Wide input range handling
   - EMI consideration
   - Temperature derating

3. **Research and Education**
   - Understanding control theory principles
   - Component sensitivity analysis
   - Design trade-off exploration

## Technical Specifications

### Requirements
- Python 3.7+
- NumPy, SciPy, Pandas
- OpenPyXL for Excel handling
- Matplotlib for plotting

### Validation
- All designs verified for stability
- Component stress analysis included
- Worst-case scenario validation
- Temperature coefficient considerations

### Limitations
- Continuous conduction mode (CCM) only
- Ideal switch and diode assumptions
- Linear control design (small-signal)
- Standard ambient conditions

## AI Engineering Policy Compliance

This tool strictly follows AI engineering policies:

✅ **Plan-First Approach**: Detailed implementation planning before coding
✅ **Step-by-Step Validation**: Each design step verified before proceeding  
✅ **Rigorous Documentation**: Mathematical derivations and design rationale
✅ **Error Recovery**: Comprehensive validation and lessons learned
✅ **Self-Improvement**: Continuous learning from design iterations

## Advanced Features

### State-Space Analysis
- Eigenvalue analysis for natural frequencies
- Controllability and observability matrices
- Time-domain response prediction

### Robustness Assessment  
- Component tolerance sensitivity
- Operating point variations
- Temperature stability analysis

### Optimization Extensions
- Multi-objective optimization (efficiency vs size)
- Pareto frontier exploration
- Monte Carlo tolerance analysis

## Support and Validation

⚠️ **Important**: This tool provides theoretical design calculations. All designs must be validated through:
1. SPICE circuit simulation
2. Hardware prototype testing  
3. EMI/EMC compliance verification
4. Thermal analysis and testing

## License and Disclaimer

This tool is provided for educational and research purposes. Users are responsible for validating all designs before production use. The tool follows established power electronics principles but cannot account for all real-world effects and constraints.

---
**Generated with AI Engineering Policy compliance - Rigorous verification at each step.**