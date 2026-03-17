# Boost Converter Control Theory - PowerPoint Presentation

## Slide 1: Title Slide
**Title**: Boost Converter Control Theory and Design
**Subtitle**: Complete Guide to Transfer Functions, Stability, and Control Design
**Date**: March 2026

---

## Slide 2: Presentation Overview
### Topics Covered:
- Transfer Functions and Frequency Response
- Bode Plot Analysis
- Feedback System Stability
- PI Controller Design  
- State-Space Modeling
- Boost Converter Analysis

### Learning Objectives:
- Understand fundamental control theory concepts
- Apply stability analysis techniques
- Design PI controllers for power converters
- Derive transfer functions using state-space methods

---

## Slide 3: Transfer Function Fundamentals
### Definition:
**H(s) = Y(s)/X(s) = N(s)/D(s)**

### Key Components:
- **Poles**: Roots of denominator D(s) = 0
- **Zeros**: Roots of numerator N(s) = 0  
- **Dominant Poles**: Closest to imaginary axis

### Example:
```
H(s) = (s + 2)/((s + 1)(s + 5))
```
- Zero at s = -2
- Poles at s = -1, -5
- Dominant pole: s = -1

---

## Slide 4: Poles and Zeros - Physical Meaning
### Poles Determine:
- System stability (must be in left half-plane)
- Transient response characteristics
- Time constants: τ = -1/pole_location

### Zeros Affect:
- Magnitude response
- Phase response
- Initial response direction

### Real vs Complex Poles:
- **Real poles**: Exponential response
- **Complex poles**: Oscillatory response with damping

---

## Slide 5: Transient Response Examples
### First-Order System: H(s) = 1/(s + a)
- Time constant: τ = 1/a
- Step response: y(t) = (1/a)(1 - e^(-at))
- Rise time ∝ 1/a

### Second-Order System: H(s) = ωn²/(s² + 2ζωns + ωn²)
- Natural frequency: ωn
- Damping ratio: ζ
- Overshoot: Mp = e^(-πζ/√(1-ζ²))
- Settling time: ts ≈ 4/(ζωn)

---

## Slide 6: Bode Plot Introduction
### Purpose:
Analyze system frequency response graphically

### Two Plots:
1. **Magnitude**: 20log₁₀|H(jω)| vs log₁₀(ω)
2. **Phase**: ∠H(jω) vs log₁₀(ω)

### Benefits:
- Visual system analysis
- Stability assessment
- Controller design aid
- Multiplicative factors → additive in dB

---

## Slide 7: Bode Plot Building Blocks
### Basic Elements:
| Element | Magnitude Slope | Phase |
|---------|----------------|-------|
| Constant K | 0 dB/decade | 0° |
| Integrator 1/s | -20 dB/decade | -90° |
| Differentiator s | +20 dB/decade | +90° |
| Pole 1/(1+s/ωp) | 0→-20 dB/decade | 0°→-90° |
| Zero (1+s/ωz) | 0→+20 dB/decade | 0°→+90° |

### Corner Frequency:
Point where asymptotes meet (-3dB for poles/zeros)

---

## Slide 8: Bode Plot Construction Example
### Transfer Function:
```
H(s) = 100(s + 10)/[s(s + 2)(s + 100)]
```

### Steps:
1. Factor: H(s) = 10 × (s/10 + 1)/[s × (s/2 + 1) × (s/100 + 1)]
2. Identify corner frequencies: 2, 10, 100 rad/s
3. Plot magnitude asymptotes
4. Plot phase asymptotes
5. Apply actual slopes at corners

---

## Slide 9: Feedback System Stability
### Standard Feedback Loop:
```
R(s) →[+]→ G(s) → Y(s)
       ↑         ↓
       └── H(s) ←┘
```

### Closed-Loop Transfer Function:
**T(s) = G(s)/(1 + G(s)H(s))**

### Loop Transfer Function:
**L(s) = G(s)H(s)**

### Stability Condition:
All closed-loop poles in left half-plane

---

## Slide 10: Stability Margins
### Gain Margin (GM):
- Factor by which gain can increase before instability
- Measured at phase crossover frequency (∠L(jω) = -180°)
- GM = -20log₁₀|L(jωpc)| dB

### Phase Margin (PM):
- Additional phase lag tolerable before instability  
- Measured at gain crossover frequency (|L(jω)| = 1)
- PM = 180° + ∠L(jωgc)

### Design Guidelines:
- GM > 6 dB, PM > 30° (minimum)
- GM > 10 dB, PM > 45° (good design)

---

## Slide 11: Stability Analysis Methods
### Routh-Hurwitz Criterion:
- Algebraic method
- Uses characteristic polynomial coefficients
- No need to solve for roots
- Determines number of unstable poles

### Nyquist Criterion:  
- Graphical method using polar plots
- Based on contour mapping
- Handles systems with RHP poles
- Encirclements of (-1,0) point determine stability

### Bode Plot Method:
- Most practical for design
- Direct reading of margins
- Easy to visualize compensation effects

---

## Slide 12: PI Control Overview
### PI Controller Structure:
```
Gc(s) = Kp + Ki/s = Kp(1 + 1/(Ti·s))
```

### Benefits:
- **Proportional (Kp)**: Fast response, reduces rise time
- **Integral (Ki/s)**: Eliminates steady-state error

### Trade-offs:
- ✓ Zero steady-state error for step inputs
- ✓ Good disturbance rejection
- ✗ Phase lag reduces stability margins
- ✗ Potential integral windup

---

## Slide 13: PI Controller Design Methods
### 1. Bandwidth Design:
- Choose desired crossover frequency ωgc
- Adjust Kp for |L(jωgc)| = 1  
- Place integral zero for adequate PM

### 2. Pole-Zero Cancellation:
- Use PI zero to cancel plant pole
- Simplifies system analysis
- Ti = τpole_to_cancel

### 3. Phase Margin Design:
- Choose desired PM (45°-60°)
- Account for PI phase lag
- Solve for ωgc and parameters iteratively

---

## Slide 14: PI Design Example
### Plant: G(s) = 100/[s(s + 10)]
### Design Requirements: PM ≥ 50°

### Design Steps:
1. Choose Ti = 0.5 (place zero at -2 rad/s)
2. Required plant phase at crossover: -130°
3. From ∠G(jωgc) = -90° - arctan(ωgc/10) = -130°
4. Solve: ωgc ≈ 5.8 rad/s  
5. From |G(jωgc)Gc(jωgc)| = 1: Kp ≈ 0.4

### Result: Gc(s) = 0.4(1 + 2/s)

---

## Slide 15: State-Space Model Introduction
### Mathematical Form:
```
ẋ(t) = Ax(t) + Bu(t)    (State equation)
y(t) = Cx(t) + Du(t)    (Output equation)
```

### Advantages:
- Multiple inputs/outputs naturally handled
- Access to internal states
- Time-domain design methods
- Efficient computer implementation
- Extension to nonlinear systems

### State Selection:
Choose energy storage elements (L, C) as states

---

## Slide 16: State-Space ↔ Transfer Function
### State-Space to Transfer Function:
```
H(s) = C(sI - A)⁻¹B + D
```

### Transfer Function to State-Space:
Multiple forms possible:
- **Controller Canonical Form**
- **Observer Canonical Form**  
- **Modal Form**
- **Physically Motivated Form**

### System Properties:
- **Poles**: Eigenvalues of A matrix
- **Controllability**: rank[B AB A²B ... A^(n-1)B] = n
- **Observability**: rank[C; CA; CA²; ...; CA^(n-1)] = n

---

## Slide 17: Boost Converter Circuit
### Basic Topology:
```
Vin ──[L]──●──────[D]──●──── Vo
           │              │
           │              C  RL  
           │              │
           └──[SW]────────┘
```

### Operation:
- **Switch ON**: Energy stored in inductor
- **Switch OFF**: Energy transferred to output
- **Duty Cycle**: d = ton/T
- **Ideal Gain**: Vo/Vin = 1/(1-d)

---

## Slide 18: Boost Converter State-Space Model
### State Variables:
- x₁ = iL (inductor current)
- x₂ = vo (output voltage)

### Input Variables:
- u₁ = vin (input voltage)
- u₂ = d (duty cycle)  
- u₃ = io (load current)

### Average State-Space Model:
```
[ẋ₁] = [0      -(1-D)/L][x₁] + [1/L  0    0  ][u₁]
[ẋ₂]   [(1-D)/C  -1/RC ][x₂]   [0   0  -1/C ][u₂]
                                              [u₃]
```

---

## Slide 19: Small-Signal Linearization
### Operating Point:
- **DC Values**: IL, Vo, Vin, D, Io
- **Steady-State**: Vo = Vin/(1-D)

### Perturbation Variables:
- iL = IL + ĩL (DC + small AC)
- vo = Vo + ṽo  
- d = D + d̃

### Linearized Model:
```
[d ĩL/dt] = [0      -(1-D)/L][ĩL] + [1/L  Vo/L   0  ][ṽin]
[d ṽo/dt]   [(1-D)/C  -1/RC ][ṽo]   [0  -IL/C -1/C ][d̃  ]
                                                    [ĩo ]
```

---

## Slide 20: Key Transfer Functions
### Control-to-Output: Gvd(s)
```
Gvd(s) = ṽo(s)/d̃(s) = Vo[1 - s·L·IL/(Vo·(1-D))]
                       ──────────────────────────
                       L[s² + s/(RC) + (1-D)²/(LC)]
```

### Control-to-Current: Gid(s)
```
Gid(s) = ĩL(s)/d̃(s) = [Vo(s + 1/RC) + IL(1-D)/C]
                       ────────────────────────────
                       L[s² + s/(RC) + (1-D)²/(LC)]
```

### Common Denominator:
All transfer functions share: **s² + s/(RC) + (1-D)²/(LC)**

---

## Slide 21: Complete Transfer Function Set
### Input-to-Output Relations:
```
Gvvin(s) = ṽo/ṽin = (1-D)/(LC) / [s² + s/(RC) + (1-D)²/(LC)]

Givin(s) = ĩL/ṽin = (s + 1/RC)/L / [s² + s/(RC) + (1-D)²/(LC)]
```

### Load-to-Output Relations:
```
Gvo(s) = ṽo/ĩo = (1-D)/(LC) / [s² + s/(RC) + (1-D)²/(LC)]

Gio(s) = ĩL/ĩo = -(1-D)/(LC) / [s² + s/(RC) + (1-D)²/(LC)]
```

### Output Impedance:
**Zo(s) = -Gvo(s)**

---

## Slide 22: Characteristic Polynomial Analysis
### Standard Form:
```
D(s) = s² + s/(RC) + (1-D)²/(LC)
```

### System Parameters:
- **Natural Frequency**: ωn = (1-D)/√(LC)
- **Damping Ratio**: ζ = (1/2RC)√(L/C) × 1/(1-D)  
- **Quality Factor**: Q = (1-D)R√(C/L) = 1/(2ζ)

### Design Implications:
- **Resonant Peaking**: Q > 0.5 creates magnitude peaking
- **Control Bandwidth**: Must be << ωn for stability
- **Load Effect**: Heavier loads (smaller R) increase damping

---

## Slide 23: Right Half-Plane Zero Challenge
### Gvd(s) Zero Location:
For resistive load (Io ≈ 0): **s ≈ (1-D)R/L**

### Physical Explanation:
1. Duty cycle increase → inductor current initially decreases
2. Energy temporarily diverted from output  
3. Output voltage initially drops (inverse response)
4. Eventually rises to higher steady-state value

### Control Design Impact:
- **Fundamental Limitation**: Cannot control faster than RHP zero
- **Bandwidth Limit**: ωBW < (1-D)R/(2L) typically
- **Phase Lag**: Reduces stability margins

---

## Slide 24: Practical Design Guidelines
### Component Selection:
- **Inductor**: L determines current ripple and control bandwidth
- **Capacitor**: C affects voltage ripple and system dynamics
- **Load**: R influences damping and stability

### Control Design Rules:
1. **Crossover Frequency**: ωgc < ωn/5 (avoid resonance)
2. **Phase Margin**: PM > 45° minimum, 60° preferred
3. **Gain Margin**: GM > 10 dB for robust design

### Practical Considerations:
- **ESR Effects**: Capacitor ESR adds damping and zeros
- **Current Mode Control**: Alternative to voltage mode
- **Compensation Networks**: May need lead-lag compensation

---

## Slide 25: Design Example Summary
### Boost Converter Specifications:
- Input: 12V, Output: 24V (D = 0.5)
- L = 100μH, C = 100μF, R = 10Ω
- Switching frequency: 100kHz

### Calculated Parameters:
- ωn = 0.5/√(100μH × 100μF) = 50,000 rad/s
- ζ = (1/20Ω)√(100μH/100μF) × 1/0.5 = 0.1
- Q = 5 (significant resonant peaking)

### Transfer Functions:
```
Gvd(s) = 24[1 - s(100μH)/(5Ω)] / [100μH(s² + 1000s + 2.5×10⁹)]
```

---

## Slide 26: Conclusion and Key Takeaways
### Fundamental Concepts Mastered:
- ✓ Transfer function analysis with poles and zeros
- ✓ Bode plot construction and interpretation  
- ✓ Stability analysis using margins and criteria
- ✓ PI controller design methodologies
- ✓ State-space modeling for power converters

### Critical Design Insights:
- **RHP Zero Limitation**: Fundamental bandwidth constraint
- **Resonance Management**: Proper damping essential
- **Stability Margins**: Conservative design for robustness

### Advanced Topics for Further Study:
- Current mode control techniques
- Advanced compensation methods
- Digital control implementation
- Nonlinear control approaches

---

## Slide 27: References and Further Reading
### Recommended Textbooks:
- "Power Electronics: Converters, Applications, and Design" - Mohan, Undeland, Robbins
- "Modern Control Engineering" - Ogata  
- "Control Systems Engineering" - Nise
- "Fundamentals of Power Electronics" - Erickson, Maksimović

### Key IEEE Papers:
- Small-signal modeling techniques for switching converters
- Right half-plane zero effects in boost converters
- Advanced control methods for power electronics

### Design Tools:
- MATLAB/Simulink for analysis and simulation
- LTspice for circuit simulation
- Python control library for modern analysis

---

## Slide 28: Questions and Discussion
### Review Questions:
1. What determines the dominant poles in a transfer function?
2. How do stability margins relate to transient response?
3. Why does the boost converter have a RHP zero?
4. When would you use pole-zero cancellation in PI design?

### Design Exercises:
- Design PI controller for given boost converter specs
- Analyze stability of modified circuit topologies  
- Compare different compensation strategies
- Optimize performance vs stability trade-offs

### Next Steps:
- Implement designs in simulation
- Build and test hardware prototypes
- Explore advanced control techniques
- Study practical implementation challenges