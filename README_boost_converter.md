# Boost Converter Auto-Design Tool

Professional DCDC design tool with rigorous state-space modeling and dual-loop PI control design.

## Features

- **Rigorous Mathematical Foundation**: State-space modeling with transfer function derivation
- **Dual-Loop PI Control**: Inner current loop + outer voltage loop design
- **Component Optimization**: Discrete component selection with constraint satisfaction
- **Professional Output**: Excel results + HTML documentation with mathematical equations
- **Default Configuration**: Pre-configured for Vin=8V, Vout=12V with discrete component options

## Default Design Specifications

The tool comes pre-configured with the following default values for successful design:

| Parameter | Default Values |
|-----------|----------------|
| Input Voltage | Vin = 8V (fixed) |
| Output Voltage | Vout = 12V (fixed) |
| Load Resistance | R = 15Ω, 30Ω, 45Ω (discrete options) |
| Inductor | L = 0.5mH, 1.0mH, 1.5mH (discrete options) |
| Capacitor | C = 22µF, 44µF, 66µF (discrete options) |
| Switching Frequency | f_sw = 50kHz, 100kHz, 200kHz (discrete options) |

## Quick Start

### 1. Run the Design Tool

```bash
python boost_converter_designer.py
```

### 2. First Run Behavior

On first run, the tool will:
- Create `config/` and `output/` directories
- Generate `config/config_boost_design.xlsx` with default values
- Perform complete design optimization
- Generate results in `output/` directory

### 3. Output Files

**Excel Results**: `output/output_boost_design.xlsx`
- Component values with safety margins
- Control parameters (Kp, Ki for current and voltage loops)
- Design summary with all key parameters

**HTML Documentation**: `output/output_boost_design.html`
- Mathematical derivations with MathJax equations
- Step-by-step design rationale
- Professional review-ready documentation

## Design Methodology

### 1. State-Space Modeling

The tool derives the boost converter state-space model:

```
x = [iL, vC]^T
dx/dt = Ax + Bu + Ed_in
y = Cx
```

Where A, B, C matrices are calculated from circuit parameters.

### 2. Transfer Function Derivation

Key transfer functions are calculated:
- **Gvd(s)**: Control-to-output voltage
- **Gid(s)**: Control-to-inductor current
- **RHP Zero**: Critical for stability analysis

### 3. Control Design

**Inner Current Loop**:
- PI controller design with crossover frequency f_ci
- Constraint: f_ci ≤ f_sw/10

**Outer Voltage Loop**:
- PI controller with RHP zero consideration
- Constraint: f_cv ≤ f_z,RHP/5

### 4. Component Optimization

The tool optimizes component selection by:
- Testing all discrete component combinations
- Checking design feasibility (ripple, stability, duty ratio)
- Minimizing cost function: α×L + β×C + γ/f_sw

## Configuration Customization

To modify design specifications:

1. Edit `config/config_boost_design.xlsx`
2. Update parameters in the appropriate rows
3. Run the tool again

### Configuration Modes

- **FIXED**: Absolute requirement, cannot be changed
- **RANGE**: Continuous range with min/max limits
- **DISCRETE**: Explicit list of selectable values (comma-separated)

## Design Constraints

The tool enforces professional design constraints:

- **Duty Ratio**: 0.1 ≤ D ≤ 0.8
- **Voltage Ripple**: ≤ 2% of output voltage
- **Current Ripple**: ≤ 40% of average inductor current
- **Stability Margins**: PM ≥ 45°, GM ≥ 10dB
- **Bandwidth Separation**: f_ci/f_cv ≥ 5
- **RHP Zero Margin**: f_cv ≤ f_z,RHP/5

## Testing

Run the test suite to validate functionality:

```bash
python test_boost_designer.py
```

## Dependencies

- Python 3.7+
- numpy
- pandas
- openpyxl
- matplotlib

## Professional Use

This tool generates professional-grade documentation suitable for:
- Design reviews
- Technical documentation
- Hardware implementation
- Compliance verification

The mathematical rigor and comprehensive analysis make it suitable for industrial applications requiring high reliability and performance.

---

*Generated with Claude Code Professional Design Tool*