"""Animation mathematics for HyprMac Tahoe compatibility.

Pure mathematical functions for spring-based animations, extracted from
shell/hyprmac-shell for independent testing and reuse. GTK/Wayland-free.

Uses spring physics for panel emerge/stop animations with configurable
frequency and damping parameters.

Verified parameters from macOS Tahoe 26.6.1 DesignLibrary.framework mining:
- popover_appear: spring(0.3, 0.7), 150ms, transform+opacity
- Source: tahoe26_mining_inserts.sql, mining_a22f4e35e301cfd70.json
"""

import math


def spring_step(value, velocity, target, dt, frequency=3.7, damping=0.82):
    """
    Uma mola amortecida com passo em segundos, estável mesmo após quadro perdido.

    Args:
        value: Current position/value
        velocity: Current velocity
        target: Target position/value to spring toward
        dt: Time delta in seconds
        frequency: Spring frequency (Hz). Default 3.7 for HyprMac
        damping: Damping coefficient. Default 0.82 for HyprMac

    Returns:
        tuple: (new_value, new_velocity)
    """
    dt = min(max(dt, 0.0), 0.05)
    omega = 2 * math.pi * frequency
    steps = max(1, math.ceil(dt / 0.008))
    h = dt / steps
    for _ in range(steps):
        velocity += (omega * omega * (target - value)
                     - 2 * damping * omega * velocity) * h
        value += velocity * h
    if abs(target - value) < 0.001 and abs(velocity) < 0.01:
        return target, 0.0
    return value, velocity


# Tahoe 26 animation parameters - VERIFIED from DesignLibrary.framework mining
# popover_appear: spring(0.3, 0.7), 150ms, transform+opacity
# Source: tahoe26_mining_inserts.sql line 94-95, mining_a22f4e35e301cfd70.json
TAHOE_POPOVER_DURATION = 0.150   # 150ms - VERIFIED from Tahoe 26.6.1
TAHOE_POPOVER_FREQUENCY = 0.3    # frequency=0.3 - VERIFIED from Tahoe 26.6.1
TAHOE_POPOVER_DAMPING = 0.7      # damping=0.7 - VERIFIED from Tahoe 26.6.1
POP_FROM = 0.90  # Starting scale for popin animation