# Control Theory Fundamentals

## Introduction

Control theory deals with the behavior of dynamical systems with inputs and how their behavior is modified by feedback.

## Basic Concepts

### Transfer Functions

A transfer function represents the relationship between input and output of a linear time-invariant system:

$$G(s) = \frac{Y(s)}{U(s)}$$

Where:
- $G(s)$ is the transfer function
- $Y(s)$ is the Laplace transform of the output
- $U(s)$ is the Laplace transform of the input

### Feedback Control

The closed-loop transfer function is:

$$T(s) = \frac{G(s)}{1 + G(s)H(s)}$$

Where $H(s)$ is the feedback transfer function.

## Stability Criteria

### Routh-Hurwitz Criterion

For a characteristic polynomial:
$$s^n + a_1s^{n-1} + a_2s^{n-2} + \ldots + a_n = 0$$

The system is stable if all coefficients in the first column of the Routh table are positive.

### Nyquist Criterion

A feedback system is stable if the Nyquist plot of $G(s)H(s)$ does not encircle the (-1, 0) point.

## Controller Design

### PID Control

The PID controller has the form:

$$C(s) = K_p + \frac{K_i}{s} + K_d s$$

**Tuning Parameters:**
- $K_p$: Proportional gain - reduces steady-state error
- $K_i$: Integral gain - eliminates steady-state error
- $K_d$: Derivative gain - improves transient response

### Root Locus Method

The root locus shows how closed-loop poles move as the gain varies.

**Rules:**
1. Starts at open-loop poles
2. Ends at open-loop zeros
3. Number of branches = number of poles

## Frequency Domain Analysis

### Bode Plots

Bode plots show:
- Magnitude: $20\log_{10}|G(j\omega)|$ (dB)
- Phase: $\angle G(j\omega)$ (degrees)

**Stability Margins:**
- Gain margin: Additional gain before instability
- Phase margin: Additional phase lag before instability

### Example System

For a second-order system:
$$G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

- $\omega_n$: Natural frequency
- $\zeta$: Damping ratio