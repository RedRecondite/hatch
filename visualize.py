#!/usr/bin/env python3
"""
Create a zoomed visualization of the DUCK format to show the metadata encoding
"""

from PIL import Image, ImageDraw, ImageFont
import hatch

# Create a small test sprite (16x16)
sprite = Image.new('RGBA', (16, 16), (200, 100, 100, 255))
draw = ImageDraw.Draw(sprite)
draw.rectangle([2, 2, 13, 13], fill=(150, 200, 150, 255))

# Encode with metadata
duck = hatch.encode(
    sprite,
    frame_numbers=[7, 42],
    depth_dot=(8, 10),
    hardbox=(4, 4, 6, 4),
    frame_delay=None,
    special=False
)

# Save the original small version
duck.save('duck_small.png')

# Create a 20x zoomed version to see the pixels clearly
zoom = 20
width, height = duck.size
zoomed = Image.new('RGBA', (width * zoom, height * zoom), (255, 255, 255, 255))
pixels = duck.load()

# Draw the zoomed pixels
for y in range(height):
    for x in range(width):
        color = pixels[x, y]
        for dy in range(zoom):
            for dx in range(zoom):
                zoomed.putpixel((x * zoom + dx, y * zoom + dy), color)

# Add grid lines
draw_zoom = ImageDraw.Draw(zoomed)
for x in range(width + 1):
    draw_zoom.line([(x * zoom, 0), (x * zoom, height * zoom)], fill=(200, 200, 200, 128), width=1)
for y in range(height + 1):
    draw_zoom.line([(0, y * zoom), (width * zoom, y * zoom)], fill=(200, 200, 200, 128), width=1)

# Highlight the borders
# Color strip (column 0, rows 0-4)
for y in range(5):
    draw_zoom.rectangle([0, y * zoom, zoom, (y + 1) * zoom], outline=(0, 0, 0, 255), width=3)

# Top border text area
draw_zoom.rectangle([5 * zoom, 0, width * zoom, 3 * zoom], outline=(0, 0, 0, 128), width=2)

# Depth/hardbox visualization area
draw_zoom.rectangle([0, 3 * zoom, width * zoom, 5 * zoom], outline=(0, 100, 0, 128), width=2)
draw_zoom.rectangle([0, 5 * zoom, 2 * zoom, height * zoom], outline=(0, 100, 0, 128), width=2)

# Original image area
draw_zoom.rectangle([2 * zoom, 5 * zoom, width * zoom, height * zoom], outline=(255, 0, 0, 128), width=3)

zoomed.save('duck_zoomed.png')
print(f"✓ Created duck_small.png (actual size: {duck.size})")
print(f"✓ Created duck_zoomed.png ({zoom}x zoom)")

# Create an annotated version
annotated = zoomed.copy()
draw_ann = ImageDraw.Draw(annotated)

# Try to add text annotations (might not have font, so wrap in try)
try:
    # Add labels
    annotations = [
        (zoom // 4, 0, "Color\nStrip", (0, 0, 0)),
        (5 * zoom, -zoom, "Frame Numbers: 7 42", (0, 0, 0)),
        (5 * zoom, 3.5 * zoom, "Hardbox (blue) + Depth Dot (yellow)", (0, 100, 0)),
        (2 * zoom, 5 * zoom + height * zoom // 2, "Original\nImage", (255, 0, 0)),
    ]
    
    # This will work if PIL has a default font
    for x, y, text, color in annotations:
        draw_ann.text((x, y), text, fill=color)
except:
    print("  (Could not add text annotations - no font available)")

annotated.save('duck_annotated.png')
print(f"✓ Created duck_annotated.png (with annotations)")

print("\nDUCK Format Structure:")
print("-" * 60)
print(f"Total size: {width}x{height} pixels")
print(f"Original sprite: 16x16 pixels")
print(f"Border overhead: {width - 16 - 2}px width, {height - 16 - 5}px height")
print("\nColor Strip (column 0, rows 0-4):")
print("  Row 0: White (normal border)")
print("  Row 1: Red (special border)")
print("  Row 2: Black (text color)")
print("  Row 3: Yellow (depth dot color)")
print("  Row 4: Blue (hardbox color)")
print("\nMetadata encoding visible in zoomed image!")
