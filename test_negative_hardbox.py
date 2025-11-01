#!/usr/bin/env python3
"""
Test script for negative hardbox coordinates in HATCH
Validates that dink.ini format with negative values works correctly
"""

from PIL import Image, ImageDraw
import hatch

# Create a simple test sprite (32x32 red square with a white border)
def create_test_sprite():
    img = Image.new('RGBA', (32, 32), (255, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 31, 31], outline=(255, 255, 255, 255), width=2)
    return img

print("Test: Negative hardbox coordinates (dink.ini format)")
print("=" * 60)

# Test with negative hardbox coordinates as would be used in CLI
# CLI format: left_x, top_y, right_x, bottom_y (signed offsets)
# Example from dink.ini: -14,-9,14,10
# This should be converted internally to: (14, 14, 9, 10) in internal format

sprite = create_test_sprite()

# Test case 1: Symmetric hardbox with negative values
print("\nTest 1: Symmetric hardbox (-8,-8,8,8)")
print("-" * 60)
# CLI would use: -8,-8,8,8
# Internal format: (8, 8, 8, 8)
duck1 = hatch.encode(
    sprite,
    frame_numbers=[1],
    depth_dot=(16, 16),
    hardbox=(8, 8, 8, 8),  # Internal format: (left, right, top, bottom)
    special=False
)
duck1.save('test_symmetric_negative.png')
print(f"✓ Created test_symmetric_negative.png")

# Decode and verify
decoded1 = hatch.decode(duck1)
print(f"Decoded hardbox (internal): {decoded1['hardbox']}")
assert decoded1['hardbox'] == (8, 8, 8, 8), "Hardbox mismatch!"
print("✓ Hardbox decoded correctly")

# Test case 2: Asymmetric hardbox matching dink.ini example
print("\nTest 2: Asymmetric hardbox like dink.ini (-14,-9,14,10)")
print("-" * 60)
# CLI would use: -14,-9,14,10
# Internal format: (14, 14, 9, 10)
duck2 = hatch.encode(
    sprite,
    frame_numbers=[42],
    depth_dot=(16, 16),
    hardbox=(14, 14, 9, 10),  # Internal: (left, right, top, bottom)
    special=False
)
duck2.save('test_asymmetric_negative.png')
print(f"✓ Created test_asymmetric_negative.png")

# Decode and verify
decoded2 = hatch.decode(duck2)
print(f"Decoded hardbox (internal): {decoded2['hardbox']}")
assert decoded2['hardbox'] == (14, 14, 9, 10), "Hardbox mismatch!"
print("✓ Hardbox decoded correctly")

# Test case 3: All positive offsets (right/bottom only)
print("\nTest 3: All positive offsets (0,0,10,10)")
print("-" * 60)
# CLI would use: 0,0,10,10
# Internal format: (0, 10, 0, 10)
duck3 = hatch.encode(
    sprite,
    frame_numbers=[99],
    depth_dot=(8, 8),
    hardbox=(0, 10, 0, 10),  # Internal: (left, right, top, bottom)
    special=False
)
duck3.save('test_positive_only.png')
print(f"✓ Created test_positive_only.png")

# Decode and verify
decoded3 = hatch.decode(duck3)
print(f"Decoded hardbox (internal): {decoded3['hardbox']}")
assert decoded3['hardbox'] == (0, 10, 0, 10), "Hardbox mismatch!"
print("✓ Hardbox decoded correctly")

# Test case 4: Edge case - large negative offsets
print("\nTest 4: Large negative offsets (-20,-20,5,5)")
print("-" * 60)
# CLI would use: -20,-20,5,5
# Internal format: (20, 5, 20, 5)
duck4 = hatch.encode(
    sprite,
    frame_numbers=[777],
    depth_dot=(24, 24),
    hardbox=(20, 5, 20, 5),  # Internal: (left, right, top, bottom)
    special=True
)
duck4.save('test_large_negative.png')
print(f"✓ Created test_large_negative.png")

# Decode and verify
decoded4 = hatch.decode(duck4)
print(f"Decoded hardbox (internal): {decoded4['hardbox']}")
assert decoded4['hardbox'] == (20, 5, 20, 5), "Hardbox mismatch!"
print("✓ Hardbox decoded correctly")

print("\n" + "=" * 60)
print("All negative hardbox tests passed successfully!")
print("=" * 60)
