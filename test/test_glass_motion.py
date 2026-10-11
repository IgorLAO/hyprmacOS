#!/usr/bin/env python3
"""Test script for glass_motion.py module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shell'))

try:
    import glass_motion
    print("✓ Successfully imported glass_motion module")
    
    # Test spring_step function
    value, velocity = glass_motion.spring_step(0.0, 0.0, 1.0, 0.016)  # 60fps frame
    print(f"✓ spring_step test: value={value:.6f}, velocity={velocity:.6f}")
    
    # Test with zero dt
    value, velocity = glass_motion.spring_step(0.5, 0.1, 1.0, 0.0)
    assert value == 0.5 and velocity == 0.1
    print("✓ Zero dt test passed")
    
    # Test with negative dt (should clamp to 0)
    value, velocity = glass_motion.spring_step(0.5, 0.1, 1.0, -0.01)
    assert value == 0.5 and velocity == 0.1
    print("✓ Negative dt test passed")
    
    # Test convergence
    value, velocity = 0.0, 0.0
    for i in range(100):
        value, velocity = glass_motion.spring_step(value, velocity, 1.0, 0.016, frequency=2.0, damping=0.8)
    
    print(f"✓ Convergence test: value={value:.6f}, velocity={velocity:.6f}")
    assert abs(value - 1.0) < 0.01, f"Value {value} not close enough to target 1.0"
    assert abs(velocity) < 0.1, f"Velocity {velocity} not close enough to 0"
    
    print("✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Test failed: {e}")
    sys.exit(1)
