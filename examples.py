#!/usr/bin/env python3
"""
Example usage of HATCH for Dink Smallwood sprite processing
"""

from PIL import Image
import hatch

# Example 1: Processing from Python
print("Example 1: Python API Usage")
print("=" * 60)

# Load your sprite
sprite = Image.open('my_sprite.png')

# Encode with metadata
duck_image = hatch.encode(
    image=sprite,
    frame_numbers=[1, 5, 10],  # Multiple frame numbers
    depth_dot=(16, 24),         # Depth dot at x=16, y=24
    hardbox=(8, 8, 12, 4),      # Left=8, Right=8, Top=12, Bottom=4 (relative to depth dot)
    frame_delay=75,             # Optional frame delay
    special=False               # Not a special frame
)

# Save as PNG (always save as PNG regardless of input format)
duck_image.save('my_sprite_duck.png', 'PNG')
print("✓ Encoded sprite saved as 'my_sprite_duck.png'")

# Later, decode the metadata
decoded = hatch.decode(duck_image)
print(f"\nDecoded metadata:")
print(f"  Frame numbers: {decoded['frame_numbers']}")
print(f"  Depth dot: {decoded['depth_dot']}")
print(f"  Hardbox: {decoded['hardbox']}")
print(f"  Frame delay: {decoded['frame_delay']}")
print(f"  Special: {decoded['special']}")

# Get back the original image
original = decoded['original_image']
original.save('extracted_original.png')
print(f"  Original image size: {original.size}")

print("\n" + "=" * 60)
print("Example 2: Command-Line Usage")
print("=" * 60)
print("""
# Encode a sprite
python hatch.py encode input.png output.png \\
    -f "1,12,3" \\
    -d "16,24" \\
    -hb "8,8,12,4" \\
    -fd 75

# Encode a special frame
python hatch.py encode input.png output.png \\
    -f "99" \\
    -d "16,16" \\
    -hb "10,10,10,10" \\
    -s

# Decode a DUCK image
python hatch.py decode duck_image.png -o extracted.png
""")

print("=" * 60)
print("Example 3: Understanding Coordinates")
print("=" * 60)
print("""
For a 32x32 sprite:
  - Depth dot at (16, 24) means center-bottom of sprite
  - Hardbox (8, 8, 12, 4) means:
    * Left edge: 16 - 8 = pixel 8
    * Right edge: 16 + 8 = pixel 24
    * Top edge: 24 - 12 = pixel 12
    * Bottom edge: 24 + 4 = pixel 28
    
The hardbox visualization appears in the 2-pixel border:
  - Blue lines on top border (rows 3-4) show horizontal extent
  - Blue lines on left border (cols 0-1) show vertical extent
  - Yellow marks show depth dot location
  - If they overlap, outer pixel = blue, inner pixel = yellow
""")

print("\n" + "=" * 60)
print("Example 4: DUCK Format Features")
print("=" * 60)
print("""
✓ Self-describing: Color palette stored in first 5 pixels
✓ Compact: Minimal border overhead (2px left, 5px top)
✓ Visual: Metadata is human-readable at pixel level
✓ Expandable: Transparent regions indicate overflow
✓ Reversible: Full encode/decode support
✓ Special frames: Red border for special frames
""")
