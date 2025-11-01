#!/usr/bin/env python3
"""
Test script for HATCH - demonstrates encoding and decoding DUCK images
"""

from PIL import Image, ImageDraw
import hatch

# Create a simple test sprite (32x32 red square with a white border)
def create_test_sprite():
    img = Image.new('RGBA', (32, 32), (255, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 31, 31], outline=(255, 255, 255, 255), width=2)
    return img

# Test 1: Basic encoding
print("Test 1: Basic encoding with single frame")
print("-" * 50)
sprite = create_test_sprite()
duck = hatch.encode(
    sprite,
    frame_numbers=[42],
    depth_dot=(16, 16),
    hardbox=(8, 8, 8, 8),
    frame_delay=None,
    special=False
)
duck.save('test_basic.png')
print(f"✓ Created test_basic.png (size: {duck.size})")

# Test 2: Multiple frames with delay
print("\nTest 2: Multiple frames with frame delay")
print("-" * 50)
duck2 = hatch.encode(
    sprite,
    frame_numbers=[1, 12, 3],
    depth_dot=(10, 20),
    hardbox=(5, 5, 10, 10),
    frame_delay=50,
    special=False
)
duck2.save('test_multiple.png')
print(f"✓ Created test_multiple.png (size: {duck2.size})")

# Test 3: Special frame
print("\nTest 3: Special frame (red border)")
print("-" * 50)
duck3 = hatch.encode(
    sprite,
    frame_numbers=[99],
    depth_dot=(8, 8),
    hardbox=(4, 4, 4, 4),
    frame_delay=None,
    special=True
)
duck3.save('test_special.png')
print(f"✓ Created test_special.png (size: {duck3.size})")

# Test 4: Decode and verify
print("\nTest 4: Decode and verify metadata")
print("-" * 50)
decoded = hatch.decode(duck2)
print(f"Frame Numbers: {decoded['frame_numbers']}")
print(f"Depth Dot: {decoded['depth_dot']}")
print(f"Hardbox: {decoded['hardbox']}")
print(f"Frame Delay: {decoded['frame_delay']}")
print(f"Special: {decoded['special']}")
print(f"Original Image Size: {decoded['original_image'].size}")

# Verify
expected = {
    'frame_numbers': [1, 12, 3],
    'depth_dot': (10, 20),
    'hardbox': (5, 5, 10, 10),
    'frame_delay': 50,
    'special': False
}

all_match = True
for key, value in expected.items():
    if decoded[key] != value:
        print(f"✗ Mismatch in {key}: expected {value}, got {decoded[key]}")
        all_match = False

if all_match:
    print("✓ All metadata decoded correctly!")

# Save decoded original
decoded['original_image'].save('test_decoded_original.png')
print(f"✓ Saved decoded original image")

print("\n" + "=" * 50)
print("All tests completed successfully!")
print("=" * 50)
