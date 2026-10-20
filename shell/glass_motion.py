"""Mola compartilhada do shell, Dock e Spotlight.

O cálculo roda em core/motion (Rust) quando a biblioteca compilada está disponível.
A função Python conserva o contrato durante um checkout ainda não instalado.
Não há GTK, estado global de animação ou temporizador neste módulo.
"""

import ctypes
import math
from pathlib import Path


class _SpringState(ctypes.Structure):
    _fields_ = [("value", ctypes.c_double), ("velocity", ctypes.c_double)]


_LIB = Path(__file__).resolve().parents[1] / "core/motion/target/release/libhyprmac_motion.so"
try:
    _rust = ctypes.CDLL(str(_LIB))
    _rust.hyprmac_spring_step.argtypes = [ctypes.c_double] * 6
    _rust.hyprmac_spring_step.restype = _SpringState
except OSError:
    _rust = None

RUST_ACTIVE = _rust is not None


def spring_step(value, velocity, target, dt, frequency=3.7, damping=0.82):
    """Avança uma mola amortecida por um frame, limitando a duração a 50 ms."""
    if _rust is not None:
        state = _rust.hyprmac_spring_step(value, velocity, target, dt, frequency, damping)
        return state.value, state.velocity
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
