"""Estado das molas, magnificação e quique do Dock; sem relógios ou timers próprios."""

import math


class DockMotion:
    """A UI fornece tempo, política de acessibilidade e o integrador compartilhado."""

    def __init__(self, spring):
        self.spring = spring
        self.scales = {}
        self.velocities = {}
        self.positions = {}
        self.position_targets = {}
        self.position_shifts = {}
        self.bounces = {}
        self.last_frame = None
        self.envelope = 0.0           # intensidade da magnificação, 0…1
        self.envelope_velocity = 0.0
        self.pointer_x = None         # último ponteiro dentro do Dock

    def reset_clock(self):
        self.last_frame = None

    def retain_positions(self, items):
        keys = {item["key"] for item in items}
        self.positions = {key: state for key, state in self.positions.items() if key in keys}
        self.position_targets = {key: x for key, x in self.position_targets.items() if key in keys}
        self.position_shifts = {key: x for key, x in self.position_shifts.items() if key in keys}
        for item in items:
            if "x" in item:
                self.positions.setdefault(item["key"], (item["x"], 0.0))
                self.position_targets.setdefault(item["key"], item["x"])

    def scales_for_frame(self, items, icon, gap, origin_x, pointer_x, enabled,
                         hold, reduced, now):
        """A curva segue o ponteiro no mesmo quadro; só a intensidade E usa a mola.
        Curva e tempos são aproximações locais, não medições de animação Tahoe.
        Molas por ícone atrasavam a curva ~0,2 s atrás do ponteiro."""
        dt = 0.0 if self.last_frame is None else now - self.last_frame
        self.last_frame = now
        sigma = (icon + gap) * 1.1
        if not hold and enabled and pointer_x is not None:
            self.pointer_x, target = pointer_x, 1.0
        else:
            target = 0.0      # ao sair, a curva fica onde o ponteiro saiu e só esvazia
        if not hold:
            if reduced:
                self.envelope, self.envelope_velocity = target, 0.0
            else:
                self.envelope, self.envelope_velocity = self.spring(
                    self.envelope, self.envelope_velocity, target, dt)
        if self.envelope <= 0.0005 and target == 0.0:
            self.envelope, self.envelope_velocity = 0.0, 0.0
        animating = (abs(target - self.envelope) > 0.001
                     or abs(self.envelope_velocity) > 0.01) and not hold
        growths = []
        for item in items:
            if item["kind"] == "sep":
                growths.append(0.0)
                continue
            key = item["key"]
            if hold:
                current = self.scales.get(key, 1.0)
            elif self.pointer_x is None or self.envelope == 0.0:
                current = 1.0
            else:
                dx = self.pointer_x - (origin_x + item["x"] + icon / 2)
                intensity = min(1.0, max(0.0, self.envelope))
                current = 1 + 0.6 * intensity * math.exp(-dx * dx / (2 * sigma * sigma))
            self.scales[key], self.velocities[key] = current, 0.0
            growths.append((current - 1.0) * icon)
        return growths, animating, dt

    def position(self, item, dt, reduced, dragged_position=None, shift=0.0):
        target, key = item["x"], item["key"]
        position, velocity = self.positions.get(key, (target, 0.0))
        if target != self.position_targets.get(key, target):
            # Uma troca de ordem muda o crescimento acumulado dos vizinhos.
            # Rebaseia a mola para manter o centro visual no instante da troca.
            position += self.position_shifts.get(key, shift) - shift
        animating = False
        if dragged_position is not None:
            position, velocity = dragged_position, 0.0
        elif reduced:
            position, velocity = target, 0.0
        else:
            position, velocity = self.spring(position, velocity, target, dt)
            if abs(target - position) < 0.05 and abs(velocity) < 0.5:
                position, velocity = target, 0.0
            else:
                animating = True
        self.positions[key] = position, velocity
        self.position_targets[key] = target
        self.position_shifts[key] = shift
        return position, animating

    def bounce(self, key, now, icon, reduced):
        start = self.bounces.get(key)
        if start is None:
            return 0, False
        elapsed = now - start
        if reduced or elapsed > 8:
            self.bounces.pop(key, None)
            return 0, False
        return abs(math.sin(math.pi * elapsed / 0.62)) * icon * 0.55, True
