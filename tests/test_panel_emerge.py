"""Tests for panel emerge/stop_emerge animations with Tahoe 26.6.1 parameters."""

import unittest
from pathlib import Path


class TestEmergeAnimationImplementation(unittest.TestCase):
    """Test that emerge/stop_emerge implementation matches Tahoe 26.6.1 requirements."""

    def setUp(self):
        """Set up test fixtures."""
        self.hyprmac_path = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell"
        with open(self.hyprmac_path, 'r') as f:
            self.content = f.read()

    def test_emerge_function_exists(self):
        """Test that emerge function exists in the code."""
        self.assertIn('def emerge(win, base, origin=None):', self.content)

    def test_stop_emerge_function_exists(self):
        """Test that stop_emerge function exists in the code."""
        self.assertIn('def stop_emerge(win, base):', self.content)

    def test_emerge_uses_reduce_motion_check(self):
        """Test that emerge checks reduce_motion."""
        # Find the emerge function and check it calls reduce_motion
        emerge_start = self.content.find('def emerge(win, base, origin=None):')
        emerge_end = self.content.find('def stop_emerge(win, base):')
        emerge_content = self.content[emerge_start:emerge_end]
        self.assertIn('if reduce_motion():', emerge_content)

    def test_stop_emerge_uses_reduce_motion_check(self):
        """Test that stop_emerge checks reduce_motion."""
        # Find the stop_emerge function and check it calls reduce_motion
        stop_emerge_start = self.content.find('def stop_emerge(win, base):')
        # Find next function after stop_emerge to bound the search
        next_func_start = self.content.find('def ', stop_emerge_start + 1)
        if next_func_start == -1:
            next_func_start = len(self.content)
        stop_emerge_content = self.content[stop_emerge_start:next_func_start]
        self.assertIn('if reduce_motion():', stop_emerge_content)

    def test_emerge_uses_150ms_timing(self):
        """Test that emerge uses 150ms timing."""
        emerge_start = self.content.find('def emerge(win, base, origin=None):')
        emerge_end = self.content.find('def stop_emerge(win, base):')
        emerge_content = self.content[emerge_start:emerge_end]
        self.assertIn('if elapsed >= 0.150:  # 150ms', emerge_content)

    def test_stop_emerge_uses_150ms_timing(self):
        """Test that stop_emerge uses 150ms timing."""
        self.assertIn('if elapsed >= 0.150:  # 150ms', self.content)

    def test_emerge_uses_tahoe_spring_parameters(self):
        """Test that emerge uses Tahoe spring parameters (frequency=0.3, damping=0.7)."""
        emerge_start = self.content.find('def emerge(win, base, origin=None):')
        emerge_end = self.content.find('def stop_emerge(win, base):')
        emerge_content = self.content[emerge_start:emerge_end]
        self.assertIn('frequency=0.3, damping=0.7', emerge_content)

    def test_stop_emerge_uses_tahoe_spring_parameters(self):
        """Test that stop_emerge uses Tahoe spring parameters (frequency=0.3, damping=0.7)."""
        self.assertIn('elapsed, frequency=0.3, damping=0.7', self.content)

    def test_emerge_initializes_with_pop_from(self):
        """Test that emerge initializes with POP_FROM (0.9)."""
        emerge_start = self.content.find('def emerge(win, base, origin=None):')
        emerge_end = self.content.find('def stop_emerge(win, base):')
        emerge_content = self.content[emerge_start:emerge_end]
        self.assertIn('step.value = POP_FROM  # start from POP_FROM (0.9)', emerge_content)

    def test_stop_emerge_initializes_with_1_0(self):
        """Test that stop_emerge initializes with 1.0 (fully visible)."""
        # This line appears in the stop_emerge function (line 437 in the current version)
        self.assertIn('step.value = 1.0', self.content)

    def test_spring_step_imported_from_glass_motion(self):
        """Test that spring_step is imported from glass_motion."""
        self.assertIn('from glass_motion import spring_step', self.content)

    def test_constants_defined(self):
        """Test that required constants are defined."""
        self.assertIn('POP_FROM = 0.90', self.content)
        # Also check that TAHOE constants are defined in glass_motion (they are)


if __name__ == '__main__':
    unittest.main()