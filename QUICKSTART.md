# HATCH Quick Start Guide

## What You've Got

**HATCH** (Hardbox Annotated Transformation Caption Helper) - Your tool for creating DUCK images!

**DUCK** (Dink Universal Caption Keyframe) - The format that stores sprite metadata visually.

## Files Included

1. **hatch.py** - The main tool (both CLI and Python module)
2. **README.md** - Complete documentation
3. **test_hatch.py** - Test suite demonstrating functionality
4. **examples.py** - Usage examples
5. **visualize.py** - Creates zoomed visualizations of DUCK format
6. **test_multiple.png** - Example DUCK image
7. **duck_zoomed.png** - 20x zoomed view showing pixel structure

## Quick Start: Command Line

### Encode a sprite:
```bash
python hatch.py encode sprite.png output.png \
    -f "1,5,10" \
    -d "16,24" \
    -hb "-8,-12,8,4"
```
(Note: hardbox uses dink.ini format with signed offsets: left_x,top_y,right_x,bottom_y)

### Decode a DUCK image:
```bash
python hatch.py decode duck_image.png -o extracted.png
```

## Quick Start: Python API

```python
from PIL import Image
import hatch

# Encode
sprite = Image.open('sprite.png')
duck = hatch.encode(
    sprite,
    frame_numbers=[1, 5, 10],
    depth_dot=(16, 24),
    hardbox=(8, 8, 12, 4)
)
duck.save('sprite_duck.png')

# Decode
metadata = hatch.decode(duck)
print(metadata['frame_numbers'])  # [1, 5, 10]
print(metadata['depth_dot'])      # (16, 24)
```

## Understanding the Visualization

Look at `duck_zoomed.png` to see how metadata is encoded:

- **Top-left corner (5 pixels)**: Color palette strip
- **Top row (rows 0-2)**: Frame numbers in 3x3 font
- **Rows 3-4**: Blue hardbox lines + yellow depth dot
- **Columns 0-1**: Blue hardbox lines + yellow depth dot  
- **Main area**: Your original sprite

## Key Concepts

### Frame Numbers
Multiple frame numbers = `[1, 12, 3]`
With delay = `[1, 12, 3]` and `frame_delay=50`

### Depth Dot
The "center point" for collision/positioning: `(x, y)` coordinates

### Hardbox
**CLI**: Uses dink.ini format `(left_x, top_y, right_x, bottom_y)` - signed offsets from depth dot
- Example: `(-8, -12, 8, 4)` means left edge at -8, top at -12, right at +8, bottom at +4

**Python API**: Uses internal format `(left, right, top, bottom)` - positive distances
- Example: `(8, 8, 12, 4)` creates box 8px left, 8px right, 12px up, 4px down from depth dot

### Special Frames
Set `special=True` to use red border instead of white

## Test It!

```bash
# Run the test suite
python test_hatch.py

# Create visualizations
python visualize.py

# See examples
python examples.py
```

## Next Steps

1. Read `README.md` for complete documentation
2. Look at `test_hatch.py` for working examples
3. Try encoding your own Dink Smallwood sprites!

## Format At A Glance

```
DUCK Image = Original Sprite + Visual Metadata Border

Border Contents:
├─ Color Strip (5 pixels) - Self-describing palette
├─ Frame Text (3x3 font) - Frame numbers & delay
├─ Depth Dot (yellow) - Positioning anchor
└─ Hardbox (blue) - Collision bounds

Everything you need is visible in the pixels!
```

Happy sprite processing! 🦆
