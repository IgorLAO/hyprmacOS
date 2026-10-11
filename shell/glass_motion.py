"""Animation mathematics for HyprMac Tahoe compatibility.

Pure mathematical functions for spring-based animations, extracted from
shell/hyprmac-shell for independent testing and reuse. GTK/Wayland-free.

Mola usada pelo pressionar dos botões, pelo Dock e pelos controles do Spotlight.
A abertura dos painéis (emerge) segue a curva macPop do Hyprland, não esta mola.
A "spring(0.3, 0.7) 150 ms" atribuída ao DesignLibrary.framework vem do registro
tahoe26:apps:DesignLibrary.framework:animations, marcado invalid: não usar.
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
