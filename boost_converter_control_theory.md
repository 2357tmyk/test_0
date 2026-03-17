# Boost Converter Control Theory - Complete Guide

## Table of Contents
1. [Transfer Functions](#1-transfer-functions)
2. [Bode Plots](#2-bode-plots)
3. [Feedback Stability](#3-feedback-stability)
4. [PI Control](#4-pi-control)
5. [State-Space Models](#5-state-space-models)
6. [Boost Converter Transfer Function Derivation](#6-boost-converter-transfer-function-derivation)

---

## 1. Transfer Functions

### 1.1 Basic Definitions

**Transfer Function**: A mathematical representation of the relationship between the input and output of a linear time-invariant (LTI) system in the frequency domain.

```
H(s) = Y(s)/X(s) = N(s)/D(s)
```

Where:
- H(s) = Transfer function
- Y(s) = Laplace transform of output
- X(s) = Laplace transform of input  
- N(s) = Numerator polynomial
- D(s) = Denominator polynomial

### 1.2 Poles and Zeros

**Poles**: Values of s where the denominator D(s) = 0
- Make the transfer function go to infinity
- Determine system stability and transient response
- Located at roots of denominator polynomial

**Zeros**: Values of s where the numerator N(s) = 0
- Make the transfer function equal to zero
- Affect the magnitude and phase response
- Located at roots of numerator polynomial

**Example**: 
```
H(s) = (s + 2)/((s + 1)(s + 5))
```
- Zero at s = -2
- Poles at s = -1 and s = -5

### 1.3 Dominant Poles

**Definition**: The pole(s) closest to the imaginary axis in the s-plane that primarily determine the system's transient response.

**Why Important**: 
- Systems with multiple poles: the dominant pole has the slowest decay
- Non-dominant poles decay much faster and have less influence
- Allows system simplification for control design

**Example Analysis**:
```
H(s) = 100/((s + 1)(s + 10)(s + 50))
```

Time domain poles:
- τ₁ = 1 second (dominant - slowest)
- τ₂ = 0.1 second  
- τ₃ = 0.02 second (fastest)

The dominant pole at s = -1 controls the overall system response.

### 1.4 Pole/Zero Positions and Transient Response

#### 1.4.1 Real Poles
**Location**: On the real axis in s-plane

**Response Characteristics**:
- **Left Half Plane (s < 0)**: Stable, exponential decay
- **Right Half Plane (s > 0)**: Unstable, exponential growth
- **At Origin (s = 0)**: Marginally stable, constant output

**Time Constant**: τ = -1/pole location

**Example**: Pole at s = -5
- Time constant: τ = 1/5 = 0.2 seconds
- Step response: y(t) = K(1 - e^(-t/0.2))

#### 1.4.2 Complex Conjugate Poles
**Location**: s = -ζωₙ ± jωₙ√(1-ζ²)

Where:
- ζ = damping ratio
- ωₙ = natural frequency

**Response Characteristics**:
- **ζ > 1**: Overdamped (two real poles)
- **ζ = 1**: Critically damped
- **0 < ζ < 1**: Underdamped (oscillatory)
- **ζ = 0**: Undamped oscillation
- **ζ < 0**: Unstable

**Performance Metrics**:
- Rise time: tᵣ ≈ (1.8)/ωₙ
- Settling time: tₛ ≈ 4/(ζωₙ)
- Overshoot: Mp = e^(-πζ/√(1-ζ²)) × 100%

#### 1.4.3 Effect of Zeros
**Left Half Plane Zeros (s < 0)**:
- Improve transient response
- Reduce rise time
- May increase overshoot slightly

**Right Half Plane Zeros (s > 0)**:
- Cause inverse response (undershoot)
- Increase settling time
- Create design challenges

---

## 2. Bode Plots

### 2.1 Introduction to Frequency Response

**Frequency Response**: System's steady-state response to sinusoidal inputs at different frequencies.

**Mathematical Foundation**:
For sinusoidal input: x(t) = A sin(ωt)
Steady-state output: y(t) = A|H(jω)| sin(ωt + ∠H(jω))

Where:
- |H(jω)| = Magnitude response
- ∠H(jω) = Phase response

### 2.2 AC Input Signal Transient Response

**Key Concept**: While Bode plots show steady-state frequency response, the transient behavior depends on how quickly the system reaches steady state.

**Relationship to Poles**:
- Pole location determines settling time: tₛ ≈ 4/|Re(pole)|
- Closer poles to imaginary axis = longer transient period
- System reaches steady-state AC response after transient dies out

**Practical Example**:
```
H(s) = 10/(s + 2)
```
For input x(t) = sin(10t):
1. Transient period: ≈ 4/2 = 2 seconds
2. After 2 seconds: steady-state response = 10sin(10t + φ)/√(104)

### 2.3 Transfer Function Frequency Response

**Bode Plot Construction**:
1. **Magnitude Plot**: 20log₁₀|H(jω)| vs log₁₀(ω)
2. **Phase Plot**: ∠H(jω) vs log₁₀(ω)

**Basic Building Blocks**:

#### 2.3.1 Constant Gain: K
- Magnitude: 20log₁₀(K) dB (horizontal line)
- Phase: 0° (if K > 0), 180° (if K < 0)

#### 2.3.2 Integrator: 1/s
- Magnitude: -20 dB/decade slope
- Phase: -90° (constant)

#### 2.3.3 Differentiator: s
- Magnitude: +20 dB/decade slope  
- Phase: +90° (constant)

### 2.4 Poles in Transfer Function Frequency Response

#### 2.4.1 First-Order Pole: 1/(1 + s/ωₚ)

**Asymptotic Approximation**:
- Low frequency (ω << ωₚ): 0 dB, 0°
- High frequency (ω >> ωₚ): -20 dB/decade, -90°
- Corner frequency: ωₚ

**Exact Values at Corner Frequency**:
- Magnitude: -3 dB
- Phase: -45°

**Example**: H(s) = 1/(1 + s/100)
- Corner frequency: ωₚ = 100 rad/s
- At ω = 100: -3 dB, -45°
- At ω = 1000: -20 dB, -84.3°

#### 2.4.2 Second-Order Poles: ωₙ²/(s² + 2ζωₙs + ωₙ²)

**Characteristics**:
- Corner frequency: ωₙ
- Low frequency: 0 dB, 0°
- High frequency: -40 dB/decade, -180°

**Effect of Damping Ratio ζ**:
- ζ > 0.707: No peaking in magnitude
- ζ < 0.707: Magnitude peaking near ωₙ
- ζ = 0.1: Large resonant peak (~20 dB)

**Peak Magnitude**: Mₚ = 1/(2ζ√(1-ζ²)) at ωᵣ = ωₙ√(1-2ζ²)

### 2.5 Zeros in Transfer Function Frequency Response

#### 2.5.1 First-Order Zero: (1 + s/ωz)

**Asymptotic Approximation**:
- Low frequency (ω << ωz): 0 dB, 0°
- High frequency (ω >> ωz): +20 dB/decade, +90°
- Corner frequency: ωz

**Effect**: Mirror image of pole response
- Magnitude increases at +20 dB/decade beyond corner frequency
- Phase increases from 0° to +90°

#### 2.5.2 Second-Order Zeros: (s² + 2ζωₙs + ωₙ²)/ωₙ²

**Characteristics**:
- Low frequency: 0 dB, 0°  
- High frequency: +40 dB/decade, +180°
- Creates magnitude dip (notch) for low ζ values

**Practical Application**: Used in notch filters to eliminate specific frequencies

### 2.6 Complete Bode Plot Construction Example

**Transfer Function**: 
```
H(s) = 200(s + 10)/[s(s + 2)(s + 100)]
```

**Factored Form**:
```
H(s) = (200 × 10/2 × 100) × (s/10 + 1)/[s × (s/2 + 1) × (s/100 + 1)]
     = 10 × (s/10 + 1)/[s × (s/2 + 1) × (s/100 + 1)]
```

**Corner Frequencies**:
- Integrator: s (starts from -∞ dB)
- Zero: ω = 10 rad/s
- Pole: ω = 2 rad/s  
- Pole: ω = 100 rad/s

**Magnitude Construction**:
1. Start with 20log₁₀(10) = 20 dB at ω = 1 rad/s
2. Integrator: -20 dB/decade slope
3. At ω = 2: add -20 dB/decade (total: -40 dB/decade)
4. At ω = 10: add +20 dB/decade (total: -20 dB/decade)
5. At ω = 100: add -20 dB/decade (total: -40 dB/decade)

---

## 3. Feedback Stability

### 3.1 Closed-Loop System Fundamentals

**Standard Feedback Configuration**:
```
R(s) ──→[+]──→ G(s) ──→ Y(s)
         │                 │
         └──── H(s) ←──────┘
```

**Closed-Loop Transfer Function**:
```
T(s) = Y(s)/R(s) = G(s)/(1 + G(s)H(s))
```

**Loop Transfer Function**: L(s) = G(s)H(s)

**Characteristic Equation**: 1 + L(s) = 0

### 3.2 Stability Criteria Overview

**BIBO Stability**: A system is stable if every bounded input produces a bounded output.

**Mathematical Condition**: All poles of the closed-loop transfer function must be in the left half-plane (LHP) of the s-plane.

### 3.3 Gain Margin and Phase Margin

#### 3.3.1 Gain Margin (GM)

**Definition**: Factor by which the loop gain can be increased before the system becomes unstable.

**Calculation from Bode Plot**:
1. Find phase crossover frequency ωₚc where ∠L(jωₚc) = -180°
2. GM = -20log₁₀|L(jωₚc)| dB

**Alternative Expression**: GM = 1/|L(jωₚc)|

**Stability Indication**:
- GM > 0 dB: Stable
- GM = 0 dB: Marginally stable
- GM < 0 dB: Unstable

#### 3.3.2 Phase Margin (PM)

**Definition**: Additional phase lag that can be tolerated before instability.

**Calculation from Bode Plot**:
1. Find gain crossover frequency ωgc where |L(jωgc)| = 1 (0 dB)
2. PM = 180° + ∠L(jωgc)

**Stability Indication**:
- PM > 0°: Stable
- PM = 0°: Marginally stable  
- PM < 0°: Unstable

#### 3.3.3 Relationship to Transient Response

**Phase Margin to Damping Ratio**:
For second-order systems: ζ ≈ PM/(100°)

**Design Guidelines**:
- PM = 45°-60°: Good transient response
- PM < 30°: Poor transient response (oscillatory)
- PM > 70°: Sluggish response

**Example Analysis**:
```
L(s) = 1000/[s(s + 10)(s + 100)]
```

From Bode plot:
- ωgc ≈ 22 rad/s, PM ≈ 17° (poor stability)
- ωpc ≈ 32 rad/s, GM ≈ 20 dB (good stability)

### 3.4 Bode Plot Stability Assessment

**Stability Rules from Bode Plot**:
1. **Stable System**: GM > 0 dB AND PM > 0°
2. **Critical Points**: 
   - Gain crossover: |L(jω)| = 0 dB
   - Phase crossover: ∠L(jω) = -180°

**Common Bode Plot Patterns**:

#### Type 0 System (No Integrators):
- Phase starts at 0°, decreases to -90n° (n = number of poles)
- Usually stable with adequate margins

#### Type 1 System (One Integrator):
- Phase starts at -90°, decreases further
- Requires careful compensation for stability

#### Type 2 System (Two Integrators):
- Phase starts at -180°
- Usually requires significant compensation

### 3.5 Routh-Hurwitz Stability Criterion

#### 3.5.1 Method Overview

**Purpose**: Determine stability without solving for roots of characteristic polynomial.

**Characteristic Polynomial**: D(s) = aₙsⁿ + aₙ₋₁sⁿ⁻¹ + ... + a₁s + a₀

**Necessary Condition**: All coefficients must be positive (for positive aₙ).

#### 3.5.2 Routh Array Construction

**Step 1**: Arrange coefficients
```
s^n  │ aₙ    aₙ₋₂   aₙ₋₄  ...
s^(n-1)│aₙ₋₁  aₙ₋₃   aₙ₋₅  ...
s^(n-2)│ b₁    b₂     b₃   ...
s^(n-3)│ c₁    c₂     c₃   ...
...    │ ...   ...    ...  ...
s^1    │ *
s^0    │ *
```

**Step 2**: Calculate remaining elements
```
b₁ = (aₙ₋₁ × aₙ₋₂ - aₙ × aₙ₋₃)/aₙ₋₁
b₂ = (aₙ₋₁ × aₙ₋₄ - aₙ × aₙ₋₅)/aₙ₋₁
c₁ = (b₁ × aₙ₋₃ - aₙ₋₁ × b₂)/b₁
```

#### 3.5.3 Stability Rules

**Routh Stability Criterion**: The number of unstable poles equals the number of sign changes in the first column of the Routh array.

**Stable System**: No sign changes in first column.

#### 3.5.4 Example Application

**System**: T(s) = K/[s³ + 6s² + 11s + 6 + K]

**Characteristic Equation**: s³ + 6s² + 11s + (6 + K) = 0

**Routh Array**:
```
s³ │ 1      11
s² │ 6      6+K  
s¹ │ (66-6-K)/6 = (60-K)/6
s⁰ │ 6+K
```

**Stability Conditions**:
1. 6 + K > 0 → K > -6
2. (60 - K)/6 > 0 → K < 60
3. 6 + K > 0 (already satisfied)

**Result**: Stable for -6 < K < 60

### 3.6 Nyquist Stability Criterion

#### 3.6.1 Theoretical Foundation

**Nyquist Plot**: Polar plot of L(jω) as ω varies from 0 to ∞.

**Mapping**: s-plane contour → L(s)-plane contour

**Key Principle**: Use contour mapping to determine closed-loop pole locations.

#### 3.6.2 Nyquist Criterion Statement

**For systems with L(s) having no poles in RHP**:
- **Stable**: Nyquist plot does not encircle the point (-1, 0)
- **Unstable**: Nyquist plot encircles (-1, 0)

**General Case** (P = number of open-loop RHP poles):
Z = N + P

Where:
- Z = number of closed-loop RHP poles
- N = number of clockwise encirclements of (-1, 0)
- P = number of open-loop RHP poles

**Stability**: Z = 0 (stable)

#### 3.6.3 Practical Application

**Stability Margins from Nyquist Plot**:
- **Gain Margin**: Distance from unit circle to (-1, 0) when plot crosses negative real axis
- **Phase Margin**: Angular displacement from (-1, 0) when |L(jω)| = 1

#### 3.6.4 Example Analysis

**Loop Transfer Function**:
```
L(s) = K/[s(s + 2)(s + 10)]
```

**Nyquist Plot Characteristics**:
- Starts at -90° (due to integrator)
- Ends at -270° (three poles)
- Crosses negative real axis at ω = √20

**Critical Gain**: Kcritical = 240 (when plot passes through (-1, 0))

**Stability**: Stable for K < 240

---

## 4. PI Control

### 4.1 PI Control Overview

#### 4.1.1 Basic Structure

**Proportional-Integral Controller**:
```
Gc(s) = Kp + Ki/s = Kp(1 + 1/(Ti·s))
```

Where:
- Kp = Proportional gain
- Ki = Integral gain  
- Ti = Integral time constant (Ti = Kp/Ki)

#### 4.1.2 Controller Benefits

**Proportional Term (Kp)**:
- Provides immediate response to error
- Improves transient response
- Reduces rise time

**Integral Term (Ki/s)**:
- Eliminates steady-state error for step inputs
- Improves accuracy
- Adds phase lag (potential stability issue)

#### 4.1.3 Design Trade-offs

**Advantages of PI Control**:
- Zero steady-state error to step inputs
- Relatively simple implementation
- Good disturbance rejection

**Disadvantages**:
- Integral windup in saturated systems
- Phase lag reduces stability margins
- Slower response compared to PD control

### 4.2 Parameter Design Methods

#### 4.2.1 Bandwidth Design Method

**Objective**: Design PI controller to achieve desired closed-loop bandwidth.

**Design Steps**:
1. Specify desired bandwidth ωBW
2. Choose crossover frequency ωgc ≈ ωBW  
3. Adjust Kp to achieve |L(jωgc)| = 1
4. Place integral zero to maintain adequate phase margin

**Mathematical Approach**:
For plant G(s), design Gc(s) = Kp(1 + 1/(Ti·s))

At crossover: |G(jωgc)Gc(jωgc)| = 1
```
|Kp(1 + 1/(jTi·ωgc))||G(jωgc)| = 1
Kp√(1 + 1/(Ti·ωgc)²)|G(jωgc)| = 1
```

Therefore: Kp = 1/[√(1 + 1/(Ti·ωgc)²)|G(jωgc)|]

#### 4.2.2 Pole-Zero Cancellation Method

**Concept**: Use PI controller zero to cancel a plant pole.

**Applicable When**: Plant has dominant real pole that limits performance.

**Design Procedure**:
1. Identify dominant pole: s = -1/τdom
2. Set Ti = τdom (zero cancels pole)
3. Choose Kp for desired performance

**Example**:
Plant: G(s) = 10/(s(s + 2))
Dominant pole: s = -2

PI Controller: Gc(s) = Kp(1 + 1/(0.5s)) = Kp(s + 2)/s

Resulting: G(s)Gc(s) = 10Kp/s²

**Advantages**: Simplified analysis, reduced system order
**Disadvantages**: Requires exact cancellation, sensitivity to parameter variations

#### 4.2.3 Crossover Frequency Design

**Objective**: Achieve desired gain and phase margins through crossover frequency selection.

**Design Steps**:
1. Choose desired phase margin PMdes (typically 45°-60°)
2. Account for PI phase lag: ∠Gc(jωgc) = arctan(1/(Ti·ωgc))
3. Required plant phase: ∠G(jωgc) = -180° + PMdes - ∠Gc(jωgc)
4. Solve for ωgc from plant phase requirement
5. Calculate Kp from |G(jωgc)Gc(jωgc)| = 1
6. Choose Ti to optimize response

**Detailed Example**:

**Plant**: G(s) = 100/[s(s + 10)]

**Step 1**: Choose PMdes = 50°

**Step 2**: At crossover, plant phase: ∠G(jωgc) = -90° - arctan(ωgc/10)

**Step 3**: Required condition: -90° - arctan(ωgc/10) + arctan(1/(Ti·ωgc)) = -130°
Therefore: arctan(1/(Ti·ωgc)) - arctan(ωgc/10) = -40°

**Step 4**: Choose Ti first (e.g., Ti = 1), then solve:
arctan(1/ωgc) - arctan(ωgc/10) = -40°

**Step 5**: Solve numerically: ωgc ≈ 3.16 rad/s

**Step 6**: Calculate Kp:
|G(j3.16)Gc(j3.16)| = 1
|100/[j3.16(j3.16 + 10)]| × |Kp(1 + j3.16)| = 1
Kp × 100√(1 + 3.16²)/(3.16√(3.16² + 100)) ≈ 1
Kp ≈ 1.1

**Final Controller**: Gc(s) = 1.1(1 + 1/s)

### 4.3 Performance Analysis

#### 4.3.1 Steady-State Performance

**Step Response Error**:
For unit step input with PI control:
```
ess = lim[s→0] s × 1/[1 + G(s)Gc(s)] = 0
```

**Ramp Response Error**:
For unit ramp input:
```
ess = lim[s→0] s × (1/s²)/[1 + G(s)Gc(s)] = 1/Ki
```

**Disturbance Rejection**:
Output due to disturbance d(s):
```
Y(s) = G(s)d(s)/[1 + G(s)Gc(s)]
```

At steady-state: y∞ = 0 for step disturbances

#### 4.3.2 Transient Performance

**Closed-Loop Response**:
```
T(s) = G(s)Gc(s)/[1 + G(s)Gc(s)]
```

**Performance Metrics**:
- Rise time: Depends on crossover frequency
- Overshoot: Related to phase margin
- Settling time: Determined by closed-loop poles

**Typical Values**:
- PM = 45°: Overshoot ≈ 23%
- PM = 60°: Overshoot ≈ 9%
- Bandwidth ≈ ωgc (for adequate PM)

---

## 5. State-Space Models

### 5.1 State-Space Representation Fundamentals

#### 5.1.1 Mathematical Framework

**State-Space Form**:
```
ẋ(t) = Ax(t) + Bu(t)    (State equation)
y(t) = Cx(t) + Du(t)    (Output equation)
```

Where:
- x(t) ∈ ℝⁿ = State vector
- u(t) ∈ ℝᵐ = Input vector  
- y(t) ∈ ℝᵖ = Output vector
- A ∈ ℝⁿˣⁿ = System matrix
- B ∈ ℝⁿˣᵐ = Input matrix
- C ∈ ℝᵖˣⁿ = Output matrix
- D ∈ ℝᵖˣᵐ = Feedthrough matrix

#### 5.1.2 Advantages of State-Space Representation

**Multiple Inputs/Outputs**: Natural handling of MIMO systems
**Internal States**: Access to internal system variables
**Time-Domain Analysis**: Direct time-domain design methods
**Nonlinear Extension**: Framework extends to nonlinear systems
**Computer Implementation**: Efficient numerical computation

#### 5.1.3 State Variable Selection

**Guidelines for State Selection**:
1. Choose energy storage elements (inductors, capacitors)
2. Include integrator outputs
3. Ensure linear independence
4. Physical meaning preferred for intuition

**Example - RLC Circuit**:
For series RLC circuit:
- State 1: x₁ = iL (inductor current)
- State 2: x₂ = vC (capacitor voltage)

### 5.2 Transfer Function Conversion

#### 5.2.1 State-Space to Transfer Function

**Single-Input Single-Output (SISO)**:
```
H(s) = C(sI - A)⁻¹B + D
```

Where I is the identity matrix.

**Characteristic Polynomial**:
```
det(sI - A) = 0
```

System poles are eigenvalues of matrix A.

#### 5.2.2 Transfer Function to State-Space

**Controller Canonical Form**:
For H(s) = (bₙ₋₁sⁿ⁻¹ + ... + b₁s + b₀)/(sⁿ + aₙ₋₁sⁿ⁻¹ + ... + a₁s + a₀)

```
A = [0    1    0   ...  0  ]
    [0    0    1   ...  0  ]
    [⋮    ⋮    ⋮   ⋱   ⋮  ]
    [0    0    0   ...  1  ]
    [-a₀ -a₁  -a₂  ... -aₙ₋₁]

B = [0]     C = [b₀ b₁ b₂ ... bₙ₋₁]     D = [0]
    [0]
    [⋮]
    [0]
    [1]
```

**Example Conversion**:
H(s) = (s + 5)/(s² + 3s + 2)

Controller canonical form:
```
A = [0   1]     B = [0]     C = [5 1]     D = [0]
    [-2 -3]         [1]
```

### 5.3 Solution of State Equations

#### 5.3.1 Homogeneous Solution

**Zero Input Response**: ẋ = Ax, x(0) = x₀
```
x(t) = e^(At)x₀
```

**Matrix Exponential**:
```
e^(At) = I + At + (At)²/2! + (At)³/3! + ...
```

**Eigenvalue Method**: If A has distinct eigenvalues λᵢ with eigenvectors vᵢ:
```
e^(At) = Σᵢ e^(λᵢt)vᵢvᵢᵀ/||vᵢ||²
```

#### 5.3.2 Complete Solution

**With Input**: ẋ = Ax + Bu, x(0) = x₀
```
x(t) = e^(At)x₀ + ∫₀ᵗ e^(A(t-τ))Bu(τ)dτ
```

**Output**:
```
y(t) = Ce^(At)x₀ + C∫₀ᵗ e^(A(t-τ))Bu(τ)dτ + Du(t)
```

#### 5.3.3 Step Response Example

**System**:
```
A = [0   1]     B = [0]     C = [1 0]
    [-2 -3]         [1]
```

**Eigenvalues**: λ₁ = -1, λ₂ = -2

**Step Response**:
For unit step input u(t) = 1:
```
x(t) = [0.5(1-e^(-t)) - 0.5(1-e^(-2t))]
       [0.5e^(-t) - e^(-2t)]

y(t) = x₁(t) = 0.5 - 0.5e^(-t) + 0.5e^(-2t)
```

### 5.4 Controllability and Observability

#### 5.4.1 Controllability

**Definition**: A system is controllable if any initial state can be transferred to any final state in finite time using an appropriate input.

**Controllability Matrix**:
```
Wc = [B AB A²B ... A^(n-1)B]
```

**Controllability Condition**: rank(Wc) = n

**Physical Interpretation**: All states can be influenced by the input.

#### 5.4.2 Observability

**Definition**: A system is observable if the initial state can be determined from input-output data over finite time.

**Observability Matrix**:
```
Wo = [C]
     [CA]
     [CA²]
     [⋮]
     [CA^(n-1)]
```

**Observability Condition**: rank(Wo) = n

**Physical Interpretation**: All states affect the output.

#### 5.4.3 Duality

**Duality Relationship**:
(A,B) controllable ⟺ (Aᵀ,Cᵀ) observable
(A,C) observable ⟺ (Aᵀ,Bᵀ) controllable

This relationship simplifies analysis and controller design.

---

## 6. Boost Converter Transfer Function Derivation

### 6.1 Boost Converter Fundamentals

#### 6.1.1 Circuit Topology

**Basic Boost Converter Circuit**:
```
Vin ──[L]──●──────[D]──●──── Vo
           │              │
           │              C  RL
           │              │
           └──[SW]────────┘
```

**Components**:
- L: Boost inductor
- C: Output capacitor  
- D: Boost diode
- SW: Controlled switch (MOSFET)
- RL: Load resistance

#### 6.1.2 Operating Principles

**Switch ON (0 < t < dT)**:
- Current flows: Vin → L → SW → Ground
- Inductor stores energy: vL = Vin
- Output supplied by capacitor

**Switch OFF (dT < t < T)**:
- Current flows: Vin → L → D → C || RL
- Inductor releases energy: vL = Vin - Vo
- Capacitor charges

**Key Relationships**:
- Duty cycle: d = ton/T
- Ideal steady-state: Vo = Vin/(1-d)
- Continuous conduction mode (CCM) assumed

### 6.2 State-Space Model Development

#### 6.2.1 State Variable Selection

**State Variables** (energy storage elements):
- x₁ = iL: Inductor current
- x₂ = vC = vo: Capacitor voltage (output voltage)

**Input Variables**:
- u₁ = vin: Input voltage
- u₂ = d: Duty cycle (control input)
- u₃ = io: Output current (disturbance)

#### 6.2.2 Circuit Analysis by Switching States

**Switch ON State (d = 1)**:
Inductor equation: L(diL/dt) = vin
Capacitor equation: C(dvc/dt) = -vc/RL = -io

State equations:
```
d/dt[iL] = [0  0 ][iL] + [1/L  0  0][vin]
     [vc]   [0 -1/RC][vc]   [0   0 -1/C][d ]
                                         [io ]
```

**Switch OFF State (d = 0)**:
Inductor equation: L(diL/dt) = vin - vc  
Capacitor equation: C(dvc/dt) = iL - vc/RL

State equations:
```
d/dt[iL] = [0   -1/L][iL] + [1/L  0  0][vin]
     [vc]   [1/C -1/RC][vc]   [0   0 -1/C][d ]
                                          [io ]
```

#### 6.2.3 Average State-Space Model

**Averaging Method**: For switching period T >> time constants, use duty cycle weighting:
```
ẋ = d·(Switch ON dynamics) + (1-d)·(Switch OFF dynamics)
```

**Average System Matrices**:
```
A = d·[0  0 ] + (1-d)·[0   -1/L] = [0      -(1-d)/L]
      [0 -1/RC]        [1/C -1/RC]   [(1-d)/C  -1/RC ]

B = [1/L  0     0  ]
    [0   0   -1/C ]
```

**Complete Average Model**:
```
d/dt[iL] = [0      -(1-d)/L][iL] + [1/L  0     0  ][vin]
     [vo]   [(1-d)/C  -1/RC ][vo]   [0   0   -1/C ][d  ]
                                                   [io ]
```

### 6.3 Small-Signal Linearization

#### 6.3.1 Operating Point Analysis

**Steady-State Operating Point**:
Let: IL, Vo, Vin, D, Io represent steady-state values.

From ẋ = 0:
```
0 = -(1-D)Vo/L + Vin/L        →  Vo = Vin/(1-D)
0 = (1-D)IL/C - Vo/(RC) - Io/C  →  IL = Vo/(1-D)R + Io/(1-D)
```

#### 6.3.2 Small-Signal Perturbation

**Perturbation Variables**:
- iL = IL + ĩL (inductor current = DC + AC)
- vo = Vo + ṽo (output voltage = DC + AC)  
- vin = Vin + ṽin (input voltage = DC + AC)
- d = D + d̃ (duty cycle = DC + AC)
- io = Io + ĩo (output current = DC + AC)

#### 6.3.3 Linearized State-Space Model

**Linearization Process**:
1. Substitute perturbed variables into nonlinear state equations
2. Expand and separate DC and AC terms
3. Cancel DC terms (satisfied by operating point)
4. Collect first-order AC terms (neglect higher-order products)

**Result - Small-Signal State-Space Model**:
```
d/dt[ĩL] = [0      -(1-D)/L][ĩL] + [1/L  Vo/L   0  ][ṽin]
     [ṽo]   [(1-D)/C  -1/RC ][ṽo]   [0  -IL/C -1/C ][d̃  ]
                                                    [ĩo ]
```

**Output Equation**: ỹ = ṽo = [0 1][ĩL ṽo]ᵀ

### 6.4 Transfer Function Extraction

#### 6.4.1 Control-to-Output Transfer Function Gvd(s)

**Definition**: Transfer function from duty cycle perturbation to output voltage.
```
Gvd(s) = ṽo(s)/d̃(s)|ṽin=0,ĩo=0
```

**Calculation**:
```
s[ĩL] = [0      -(1-D)/L][ĩL] + [Vo/L][d̃]
  [ṽo]   [(1-D)/C  -1/RC ][ṽo]   [-IL/C]

ṽo = [0 1][ĩL]
           [ṽo]
```

**Matrix Form**: (sI - A)X = B₂d̃, where X = [ĩL ṽo]ᵀ

**Transfer Function**:
```
Gvd(s) = C(sI - A)⁻¹B₂ = [0 1][s      (1-D)/L ]⁻¹[Vo/L ]
                                [-(1-D)/C s+1/RC]    [-IL/C]
```

**Determinant**: det(sI - A) = s² + s/RC + (1-D)²/(LC)

**After matrix inversion and simplification**:
```
Gvd(s) = (Vo/L)·s - (IL/C)·(1-D)/L
         ────────────────────────────
         s² + s/(RC) + (1-D)²/(LC)

       = Vo[1 - s(IL/Vo)·(1-D)]
         ─────────────────────────
         L[s² + s/(RC) + (1-D)²/(LC)]
```

**Using IL = Vo/((1-D)R) + Io/(1-D)**:
```
Gvd(s) = Vo[1 - s(1/R + Io(1-D)/Vo)·(1-D)L]
         ─────────────────────────────────────
         L[s² + s/(RC) + (1-D)²/(LC)]
```

#### 6.4.2 Control-to-Inductor-Current Transfer Function Gid(s)

**Definition**:
```
Gid(s) = ĩL(s)/d̃(s)|ṽin=0,ĩo=0
```

**Calculation**:
```
Gid(s) = [1 0][s      (1-D)/L ]⁻¹[Vo/L ]
               [-(1-D)/C s+1/RC]    [-IL/C]

       = Vo/L·(s + 1/RC) - (-IL/C)·(1-D)/L
         ─────────────────────────────────
         s² + s/(RC) + (1-D)²/(LC)

       = Vo(s + 1/RC) + IL(1-D)/C
         ──────────────────────────
         L[s² + s/(RC) + (1-D)²/(LC)]
```

### 6.5 Additional Transfer Functions

#### 6.5.1 Input Voltage to Output Voltage: Gvvin(s)

**Definition**: Gvvin(s) = ṽo(s)/ṽin(s)|d̃=0,ĩo=0

**Calculation**:
```
Gvvin(s) = [0 1][s      (1-D)/L ]⁻¹[1/L]
                [-(1-D)/C s+1/RC]    [0  ]

         = (1/L)·(1-D)/L
           ──────────────────────────
           s² + s/(RC) + (1-D)²/(LC)

         = (1-D)/(LC)
           ──────────────────────────
           s² + s/(RC) + (1-D)²/(LC)
```

#### 6.5.2 Input Voltage to Inductor Current: Givin(s)

**Definition**: Givin(s) = ĩL(s)/ṽin(s)|d̃=0,ĩo=0

**Calculation**:
```
Givin(s) = [1 0][s      (1-D)/L ]⁻¹[1/L]
                [-(1-D)/C s+1/RC]    [0  ]

         = (1/L)·(s + 1/RC)
           ──────────────────────────
           s² + s/(RC) + (1-D)²/(LC)

         = (s + 1/RC)/(L)
           ──────────────────────────
           s² + s/(RC) + (1-D)²/(LC)
```

#### 6.5.3 Output Current to Output Voltage: Gvo(s)

**Definition**: Gvo(s) = ṽo(s)/ĩo(s)|ṽin=0,d̃=0

**This represents output impedance**: Zo(s) = -Gvo(s)

**Calculation**:
```
Gvo(s) = [0 1][s      (1-D)/L ]⁻¹[0  ]
               [-(1-D)/C s+1/RC]    [-1/C]

       = (-1/C)·(-(1-D)/L)
         ──────────────────────────
         s² + s/(RC) + (1-D)²/(LC)

       = (1-D)/(LC)
         ──────────────────────────
         s² + s/(RC) + (1-D)²/(LC)
```

#### 6.5.4 Output Current to Inductor Current: Gio(s)

**Definition**: Gio(s) = ĩL(s)/ĩo(s)|ṽin=0,d̃=0

**Calculation**:
```
Gio(s) = [1 0][s      (1-D)/L ]⁻¹[0  ]
               [-(1-D)/C s+1/RC]    [-1/C]

       = (-1/C)·(1-D)/L
         ──────────────────────────
         s² + s/(RC) + (1-D)²/(LC)

       = -(1-D)/(LC)
         ──────────────────────────
         s² + s/(RC) + (1-D)²/(LC)
```

### 6.6 Transfer Function Summary and Analysis

#### 6.6.1 Standard Form Summary

**All transfer functions have the characteristic denominator**:
```
D(s) = s² + s/(RC) + (1-D)²/(LC)
```

**This corresponds to**:
- Natural frequency: ωn = (1-D)/√(LC)
- Damping ratio: ζ = (1/(2RC))√(L/C) × 1/(1-D)
- Quality factor: Q = (1-D)R√(C/L)

#### 6.6.2 Complete Transfer Function Set

```
Gvd(s) = Vo[1 - sL/(R(1-D)) - sLIo(1-D)/Vo]    (Control to Output Voltage)
         ─────────────────────────────────────
         L[s² + s/(RC) + (1-D)²/(LC)]

Gid(s) = Vo(s + 1/(RC)) + IL(1-D)/C             (Control to Inductor Current)  
         ────────────────────────────────
         L[s² + s/(RC) + (1-D)²/(LC)]

Gvvin(s) = (1-D)/(LC)                            (Input Voltage to Output Voltage)
           ──────────────────────────
           s² + s/(RC) + (1-D)²/(LC)

Givin(s) = (s + 1/(RC))/(L)                      (Input Voltage to Inductor Current)
           ──────────────────────────
           s² + s/(RC) + (1-D)²/(LC)

Gvo(s) = (1-D)/(LC)                              (Output Current to Output Voltage)
         ──────────────────────────
         s² + s/(RC) + (1-D)²/(LC)

Gio(s) = -(1-D)/(LC)                             (Output Current to Inductor Current)  
         ──────────────────────────
         s² + s/(RC) + (1-D)²/(LC)
```

#### 6.6.3 Physical Interpretation

**Right Half-Plane Zero in Gvd(s)**:
The zero at s = (1-D)R/L (when Io = 0) creates design challenges:
- Initial inverse response to duty cycle changes
- Phase lag that limits control bandwidth
- Fundamental limitation of boost converter control

**Resonant Behavior**:
All transfer functions exhibit resonant peaking at ωn = (1-D)/√(LC), with peaking magnitude determined by damping ratio ζ.

**Design Implications**:
- Control bandwidth must be well below resonant frequency
- Adequate damping (R loading) required for stability
- Feed-forward compensation may be needed for load variations

---

## Conclusion

This comprehensive guide provides the theoretical foundation and practical design methods for understanding and implementing control systems for boost converters. The material progresses logically from basic transfer function concepts through advanced state-space modeling, providing the mathematical rigor necessary for professional power electronics control design.

The state-space approach to boost converter analysis reveals the complex interactions between circuit elements and provides the transfer functions necessary for systematic control design. Understanding these relationships is essential for achieving stable, high-performance switching power supply systems.