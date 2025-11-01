# HATCH - Hardbox Annotated Transformation Caption Helper

**HATCH** is a Python tool for creating **DUCK** (Dink Universal Caption Keyframe) images - a format for encoding Dink Smallwood sprite frame metadata visually within the image itself.

## Features

- **Self-describing format**: Color palette stored in the first 5 pixels
- **Compact borders**: Only 2px left, 5px top overhead
- **Visual metadata**: Frame numbers, depth dot, and hardbox encoded visually
- **Bi-directional**: Full encode and decode support
- **Special frames**: Red border indicates special frames
- **Auto-expansion**: Transparent pixels indicate overflow beyond original content

## Installation

Requires Python 3.6+ and Pillow:

```bash
pip install Pillow
```

## DUCK Format Specification

### Border Layout

```
┌─────────────────────────────────┐
│ Color Strip (5px) │ Text Data   │  Rows 0-2: Frame metadata text
├─────────────────────────────────┤
│        Hardbox/Depth Vis         │  Rows 3-4: Visual markers
├──┬──────────────────────────────┤
│ H│                               │  Rows 5+: Original image content
│ B│      Original Image           │  Cols 2+: Original image content
│  │                               │
└──┴──────────────────────────────┘
 0-1 = Hardbox/Depth visualization (left)
```

### Color Strip (Column 0, Rows 0-4)

Each row stores a specific color used in the format:

- **Row 0**: Normal border color (white: 255,255,255)
- **Row 1**: Special border color (red: 255,0,0)
- **Row 2**: Text color (black: 0,0,0)
- **Row 3**: Depth dot color (yellow: 255,255,0)
- **Row 4**: Hardbox color (blue: 0,0,255)

### Text Encoding (Rows 0-2, Starting Column 5)

Frame numbers and delay encoded using 3x3 pixel font:
- **1 pixel gap**: Within same frame number (e.g., "50" = 5<1px>0)
- **2 pixel gap**: Between different frame numbers (e.g., "12 3" = 1<1px>2<2px>3)
- **Dash separator**: Separates frame numbers from delay (e.g., "1 2-50")

### Depth Dot & Hardbox Visualization

**2-pixel border** (rows 3-4 on top, columns 0-1 on left):
- **Depth dot**: Yellow marks at coordinates (dx, dy)
- **Hardbox**: Blue marks showing full hardbox extent
- **Overlap handling**: Outer pixel = hardbox, inner pixel = depth dot

**Coordinate System**:
- Depth dot: Absolute coordinates relative to image top-left
- Hardbox: Uses dink.ini format (left_x, top_y, right_x, bottom_y) - signed offsets from depth dot
  - Example: depth_dot=(16,24), hardbox=(-8,-12,8,4)
  - Negative values indicate offset to the left/top of depth dot
  - Positive values indicate offset to the right/bottom of depth dot
  - Actual bounds: x:[8,24], y:[12,28]

## Python API Usage

### Encoding

```python
from PIL import Image
import hatch

# Load your sprite
sprite = Image.open('my_sprite.png')

# Encode with metadata
# Note: Python API uses internal format (left, right, top, bottom) - positive distances
# CLI uses dink.ini format (left_x, top_y, right_x, bottom_y) - signed offsets
duck = hatch.encode(
    image=sprite,
    frame_numbers=[1, 5, 10],    # List of frame numbers
    depth_dot=(16, 24),           # (x, y) coordinates
    hardbox=(8, 8, 12, 4),        # Internal format: (left, right, top, bottom) - positive distances
    frame_delay=75,               # Optional frame delay (omit if None)
    special=False                 # Special frame flag
)

# Always save as PNG
duck.save('my_sprite_duck.png', 'PNG')
```

### Decoding

```python
from PIL import Image
import hatch

# Load DUCK image
duck_image = Image.open('my_sprite_duck.png')

# Decode metadata
metadata = hatch.decode(duck_image)

print(metadata['frame_numbers'])  # [1, 5, 10]
print(metadata['depth_dot'])      # (16, 24)
print(metadata['hardbox'])        # (8, 8, 12, 4)
print(metadata['frame_delay'])    # 75 or None
print(metadata['special'])        # True/False

# Extract original image
original = metadata['original_image']
original.save('extracted.png')
```

## Command-Line Usage

### Encode Command

```bash
python hatch.py encode input.png output.png \
    -f "1,12,3" \
    -d "16,24" \
    -hb=-8,-12,8,4 \
    -fd 75 \
    -s
```

**Arguments:**
- `input`: Input image path (any PIL-supported format)
- `output`: Output path (will be saved as PNG)
- `-f, --frames`: Comma-separated frame numbers (e.g., "1,12,3")
- `-d, --depth-dot`: Depth dot coordinates as "x,y"
- `-hb, --hardbox`: Hardbox in dink.ini format "left_x,top_y,right_x,bottom_y" (signed offsets from depth dot)
  - **Important**: Use `=` syntax for negative values: `-hb=-14,-9,14,10` (not `-hb -14,-9,14,10`)
- `-fd, --frame-delay`: Optional frame delay value
- `-s, --special`: Flag for special frame (adds red border)

### Decode Command

```bash
python hatch.py decode duck_image.png -o extracted.png
```

**Arguments:**
- `input`: DUCK image path
- `-o, --output`: Optional output path for extracted original image

## Examples

### Example 1: Single Frame

```python
import hatch
from PIL import Image

sprite = Image.open('hero_walk_1.png')
duck = hatch.encode(
    sprite,
    frame_numbers=[42],
    depth_dot=(16, 30),
    hardbox=(10, 10, 20, 8),  # Internal format: (left, right, top, bottom) distances
    special=False
)
duck.save('hero_walk_1_duck.png')
```

### Example 2: Multiple Frames with Delay

```python
duck = hatch.encode(
    sprite,
    frame_numbers=[1, 12, 3],  # Frames 1, 12, and 3
    depth_dot=(8, 8),
    hardbox=(5, 5, 5, 5),
    frame_delay=50,
    special=False
)
```

### Example 3: Special Frame

```python
duck = hatch.encode(
    sprite,
    frame_numbers=[99],
    depth_dot=(16, 16),
    hardbox=(12, 12, 12, 12),
    special=True  # Uses red border
)
```

## Understanding Coordinates

### Dink.ini Format (CLI)
For a 32x32 sprite with depth dot at (16, 24) and hardbox in dink.ini format: `-8,-12,8,4`

The signed offsets mean:
- **left_x = -8**: Left edge at 16 + (-8) = pixel 8
- **top_y = -12**: Top edge at 24 + (-12) = pixel 12
- **right_x = 8**: Right edge at 16 + 8 = pixel 24
- **bottom_y = 4**: Bottom edge at 24 + 4 = pixel 28

The hardbox creates a collision area from (8,12) to (24,28).

### Internal Format (Python API)
The same hardbox in the Python API uses positive distances: `(8, 8, 12, 4)` representing:
- Left distance: 8 pixels
- Right distance: 8 pixels
- Top distance: 12 pixels
- Bottom distance: 4 pixels

## Format Validation

A valid DUCK image must have:
1. Minimum size of 5x5 pixels
2. Color strip matching expected values at pixels (0,0) through (0,4)
3. Valid 3x3 font encoding in text area
4. Depth dot and hardbox markers in visualization area

## Technical Details

### 3x3 Font

The format uses a compact 3x3 pixel font supporting digits 0-9 and dash (-):

```
0: ███   1: ██░   2: ██░   3: ███   4: █░█
   █░█      ░█░      ░█░      ░██      ███
   ███      ░█░      ░██      ███      ░░█

5: ░██   6: █░░   7: ███   8: ███   9: ███
   ░█░      ███      ░██      ███      ███
   ██░      ███      ░░█      ███      ░░█

-: ░░░
   ███
   ░░░
```

### Expansion Handling

If metadata or hardbox exceeds original image bounds:
- Image expands to accommodate
- Expanded region uses **transparent pixels** as background
- Indicates content exceeds standard sprite dimensions

## License

This tool is provided as-is for use with Dink Smallwood sprite processing.

## References

- [Dink Smallwood Graphics Reference](https://dinkcreference.netlify.app/guide/graphics.html)
- dink.ini file format documentation
