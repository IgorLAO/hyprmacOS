import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shell'))
from glass_motion import spring_step


class GlassTransitionTests(unittest.TestCase):
    def test_moves_toward_target(self):
        """Test that the spring moves toward the target with appropriate velocity."""
        # Starting below target with zero velocity should move upward
        value, velocity = spring_step(0.0, 0.0, 1.0, 0.016)
        self.assertGreater(velocity, 0.0)
        self.assertGreater(value, 0.0)

        # Starting above target with zero velocity should move downward
        value, velocity = spring_step(2.0, 0.0, 1.0, 0.016)
        self.assertLess(velocity, 0.0)
        self.assertLess(value, 2.0)

    def test_zero_time_step(self):
        """Test that zero time step returns unchanged state."""
        value, velocity = spring_step(5.0, -2.0, 10.0, 0.0)
        self.assertEqual((value, velocity), (5.0, -2.0))

    def test_negative_time_step_clamped(self):
        """Test that negative time step is clamped to zero."""
        value, velocity = spring_step(5.0, -2.0, 10.0, -0.1)
        self.assertEqual((value, velocity), (5.0, -2.0))

    def test_large_time_step_clamped(self):
        """Test that large time step is clamped to maximum (0.05)."""
        # We can't easily predict exact values, but we can verify it doesn't crash
        # and returns reasonable floats
        value, velocity = spring_step(0.0, 0.0, 100.0, 1.0)  # dt=1.0 > 0.05
        self.assertIsInstance(value, float)
        self.assertIsInstance(velocity, float)
        # Should have moved significantly toward target
        self.assertGreater(value, 0.0)
        self.assertGreater(velocity, 0.0)

    def test_settling_condition(self):
        """Test that the settling condition correctly identifies when animation is complete."""
        # Start close to target with low velocity - should settle exactly
        value, velocity = spring_step(0.999, 0.005, 1.0, 0.016)
        self.assertEqual((value, velocity), (1.0, 0.0))

        # Start far from target should not settle
        value, velocity = spring_step(0.0, 0.0, 1.0, 0.016)
        self.assertNotEqual((value, velocity), (1.0, 0.0))
        self.assertGreater(abs(value - 1.0), 0.001)

        # High velocity near target should not settle due to velocity condition
        value, velocity = spring_step(0.999, 0.1, 1.0, 0.016)
        self.assertNotEqual((value, velocity), (1.0, 0.0))
        self.assertGreater(abs(velocity), 0.01)

    def test_frequency_effect(self):
        """Test that higher frequency results in faster oscillation."""
        # Use low damping to see oscillation clearly
        damping = 0.1
        freq_low = 1.0
        freq_high = 5.0

        # Start from same conditions
        value_low, vel_low = spring_step(0.0, 0.0, 1.0, 0.1, freq_low, damping)
        value_high, vel_high = spring_step(0.0, 0.0, 1.0, 0.1, freq_high, damping)

        # Higher frequency should result in greater velocity change (more acceleration)
        self.assertGreater(abs(vel_high), abs(vel_low))

    def test_damping_effect(self):
        """Test that higher damping results in slower oscillation (faster settling)."""
        frequency = 2.0
        damp_low = 0.1
        damp_high = 1.0

        # Start with some initial velocity away from equilibrium
        value_low, vel_low = spring_step(0.0, 1.0, 0.0, 0.1, frequency, damp_low)
        value_high, vel_high = spring_step(0.0, 1.0, 0.0, 0.1, frequency, damp_high)

        # Higher damping should result in less velocity (more resistance)
        self.assertLess(abs(vel_high), abs(vel_low))

    def test_deterministic(self):
        """Test that identical inputs produce identical outputs."""
        args = (0.5, -0.3, 1.0, 0.016, 2.5, 0.5)
        result1 = spring_step(*args)
        result2 = spring_step(*args)
        self.assertEqual(result1, result2)

    def test_extreme_values(self):
        """Test function handles extreme values without crashing."""
        # Large values
        value, velocity = spring_step(-1e6, 1e6, 1e6, 0.016)
        self.assertIsInstance(value, float)
        self.assertIsInstance(velocity, float)

        # Small values
        value, velocity = spring_step(-1e-6, 1e-6, 1e-6, 0.016)
        self.assertIsInstance(value, float)
        self.assertIsInstance(velocity, float)

        # Mixed signs
        value, velocity = spring_step(-1000.0, 500.0, 0.0, 0.016)
        self.assertIsInstance(value, float)
        self.assertIsInstance(velocity, float)

    def test_slow_spring_parameters(self):
        """Mola lenta e amortecida ainda anda na direção do alvo."""
        frequency = 0.3
        damping = 0.7

        # Should move toward target
        value, velocity = spring_step(0.0, 0.0, 1.0, 0.016, frequency, damping)
        self.assertGreater(velocity, 0.0)
        self.assertGreater(value, 0.0)

        # With dt=0, should be unchanged
        value, velocity = spring_step(0.5, 0.2, 1.0, 0.0, frequency, damping)
        self.assertEqual((value, velocity), (0.5, 0.2))


if __name__ == '__main__':
    unittest.main()