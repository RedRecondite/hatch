#!/usr/bin/env python3
"""
HATCH - Hardbox Annotated Transformation Caption Helper
Creates DUCK (Dink Universal Caption Keyframe) images with visual metadata borders
for Dink Smallwood sprite frames.
"""

from PIL import Image, ImageDraw
import argparse
import sys
from typing import List, Tuple, Optional, Dict, Any

# 3x3 font patterns (1 = filled pixel, 0 = empty pixel)
FONT_3X3 = {
    '0': [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ],
    '1': [
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 0]
    ],
    '2': [
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 1]
    ],
    '3': [
        [1, 1, 1],
        [0, 1, 1],
        [1, 1, 1]
    ],
    '4': [
        [1, 0, 1],
        [1, 1, 1],
        [0, 0, 1]
    ],
    '5': [
        [0, 1, 1],
        [0, 1, 0],
        [1, 1, 0]
    ],
    '6': [
        [1, 0, 0],
        [1, 1, 1],
        [1, 1, 1]
    ],
    '7': [
        [1, 1, 1],
        [0, 1, 1],
        [0, 0, 1]
    ],
    '8': [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ],
    '9': [
        [1, 1, 1],
        [1, 1, 1],
        [0, 0, 1]
    ],
    '-': [
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ]
}

# Color definitions
COLOR_NORMAL_BORDER = (255, 255, 255)  # White
COLOR_SPECIAL_BORDER = (255, 0, 0)     # Red
COLOR_TEXT = (0, 0, 0)                 # Black
COLOR_DEPTH_DOT = (255, 255, 0)        # Yellow
COLOR_HARDBOX = (0, 0, 255)            # Blue
COLOR_TRANSPARENT = (0, 0, 0, 0)       # Transparent


def render_3x3_char(char: str, color: Tuple[int, int, int]) -> List[List[Optional[Tuple[int, int, int]]]]:
    """
    Render a single character using 3x3 font.
    Returns a 3x3 list where None = transparent, color tuple = filled pixel.
    """
    if char not in FONT_3X3:
        raise ValueError(f"Character '{char}' not supported in 3x3 font")
    
    pattern = FONT_3X3[char]
    result = []
    for row in pattern:
        result_row = []
        for pixel in row:
            result_row.append(color if pixel == 1 else None)
        result.append(result_row)
    return result


def encode_frame_numbers_with_spacing(frame_numbers: List[int], frame_delay: Optional[int] = None) -> str:
    """
    Encode frame numbers into a string with special spacing markers.
    We'll use '|' as internal marker for 2-pixel gaps between frame numbers.
    """
    # Join frame numbers with a marker for 2-pixel gaps
    text = '|'.join(str(f) for f in frame_numbers)
    
    if frame_delay is not None:
        text += f"-{frame_delay}"
    
    return text


def render_text_with_special_spacing(text: str, color: Tuple[int, int, int]) -> List[List[Optional[Tuple[int, int, int]]]]:
    """
    Render text with special spacing rules:
    - '|' marker = 2 pixel gap (not rendered)
    - Normal characters = 1 pixel gap between them
    """
    result = [[], [], []]
    
    i = 0
    while i < len(text):
        char = text[i]
        
        if char == '|':
            # 2-pixel gap between frame numbers
            for row_idx in range(3):
                result[row_idx].extend([None] * 2)
        else:
            # Render character
            char_pixels = render_3x3_char(char, color)
            
            for row_idx in range(3):
                result[row_idx].extend(char_pixels[row_idx])
            
            # Add 1-pixel gap after character (if not last and next is not '|')
            if i < len(text) - 1 and text[i + 1] != '|':
                for row_idx in range(3):
                    result[row_idx].append(None)
        
        i += 1
    
    return result


def calculate_required_dimensions(
    original_width: int,
    original_height: int,
    frame_numbers: List[int],
    frame_delay: Optional[int],
    depth_dot: Tuple[int, int],
    hardbox: Tuple[int, int, int, int]
) -> Tuple[int, int, bool]:
    """
    Calculate required dimensions for the DUCK image.
    Returns (width, height, needs_expansion) where needs_expansion indicates
    if we exceeded the standard border size.
    """
    # Standard borders
    left_border = 2
    top_border = 5
    
    # Calculate text width
    text = encode_frame_numbers_with_spacing(frame_numbers, frame_delay)
    text_pixels = render_text_with_special_spacing(text, COLOR_TEXT)
    text_width = len(text_pixels[0]) if text_pixels[0] else 0
    
    # Color strip takes 5 pixels at start
    required_top_width = 5 + text_width
    
    # Calculate hardbox bounds (relative to image, converted from depth-dot-relative)
    dx, dy = depth_dot
    hb_left, hb_right, hb_top, hb_bottom = hardbox
    
    # Absolute coordinates of hardbox edges
    hb_x_min = dx - hb_left
    hb_x_max = dx + hb_right
    hb_y_min = dy - hb_top
    hb_y_max = dy + hb_bottom
    
    # Check if depth dot or hardbox exceed original dimensions
    max_x = max(dx, hb_x_max)
    max_y = max(dy, hb_y_max)
    
    needs_expansion = (required_top_width > left_border + original_width or
                      max_x >= original_width or
                      max_y >= original_height)
    
    # Calculate final dimensions
    width = max(left_border + original_width, required_top_width)
    height = top_border + max(original_height, max_y + 1)
    
    return width, height, needs_expansion


def encode(
    image: Image.Image,
    frame_numbers: List[int],
    depth_dot: Tuple[int, int],
    hardbox: Tuple[int, int, int, int],
    frame_delay: Optional[int] = None,
    special: bool = False
) -> Image.Image:
    """
    Encode a Dink Smallwood frame with metadata border.
    
    Args:
        image: Source PIL Image (should be in RGB or RGBA mode)
        frame_numbers: List of frame numbers
        depth_dot: (x, y) coordinates of depth dot
        hardbox: (left, right, top, bottom) relative to depth dot
        frame_delay: Optional frame delay value
        special: Whether this is a special frame
    
    Returns:
        New PIL Image with DUCK metadata border
    """
    # Convert to RGBA if needed
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    original_width, original_height = image.size
    
    # Calculate required dimensions
    width, height, needs_expansion = calculate_required_dimensions(
        original_width, original_height,
        frame_numbers, frame_delay,
        depth_dot, hardbox
    )
    
    # Create new image
    border_color = COLOR_SPECIAL_BORDER if special else COLOR_NORMAL_BORDER
    
    # If needs expansion, use transparent for the expanded region
    if needs_expansion:
        duck = Image.new('RGBA', (width, height), COLOR_TRANSPARENT)
    else:
        duck = Image.new('RGBA', (width, height), border_color + (255,))
    
    # Paste original image at offset (2, 5)
    duck.paste(image, (2, 5))
    
    # Draw color strip (pixels 0,0 to 0,4)
    pixels = duck.load()
    pixels[0, 0] = COLOR_NORMAL_BORDER + (255,)
    pixels[0, 1] = COLOR_SPECIAL_BORDER + (255,)
    pixels[0, 2] = COLOR_TEXT + (255,)
    pixels[0, 3] = COLOR_DEPTH_DOT + (255,)
    pixels[0, 4] = COLOR_HARDBOX + (255,)
    
    # Fill standard border area with correct color (if not expansion)
    if not needs_expansion:
        # Top 5 rows, after color strip
        for x in range(5, min(width, 2 + original_width)):
            for y in range(5):
                pixels[x, y] = border_color + (255,)
        
        # Left 2 columns
        for x in range(2):
            for y in range(5, 5 + original_height):
                pixels[x, y] = border_color + (255,)
    else:
        # Fill only the standard region with border color
        for x in range(5, min(width, 2 + original_width)):
            for y in range(5):
                if x < 2 + original_width and y < 5:
                    pixels[x, y] = border_color + (255,)
        
        for x in range(2):
            for y in range(5, min(height, 5 + original_height)):
                pixels[x, y] = border_color + (255,)
    
    # Render text in top border (rows 0-2, starting at column 5)
    text = encode_frame_numbers_with_spacing(frame_numbers, frame_delay)
    text_pixels = render_text_with_special_spacing(text, COLOR_TEXT)
    
    for row_idx in range(3):
        for col_idx, pixel_color in enumerate(text_pixels[row_idx]):
            if pixel_color is not None:
                x = 5 + col_idx
                y = row_idx
                if x < width:
                    pixels[x, y] = pixel_color + (255,)
    
    # Draw hardbox (2-pixel border: rows 3-4 top, columns 0-1 left)
    dx, dy = depth_dot
    hb_left, hb_right, hb_top, hb_bottom = hardbox
    
    # Calculate absolute coordinates
    hb_x_min = dx - hb_left
    hb_x_max = dx + hb_right
    hb_y_min = dy - hb_top
    hb_y_max = dy + hb_bottom
    
    # Draw hardbox on top border (rows 3-4)
    for x in range(hb_x_min, hb_x_max + 1):
        if 0 <= x < original_width:
            for y in [3, 4]:
                border_x = 2 + x
                if border_x < width:
                    # Check if depth dot will override this
                    if x != dx:
                        pixels[border_x, y] = COLOR_HARDBOX + (255,)
    
    # Draw hardbox on left border (columns 0-1)
    for y in range(hb_y_min, hb_y_max + 1):
        if 0 <= y < original_height:
            for x in [0, 1]:
                border_y = 5 + y
                if border_y < height:
                    # Check if depth dot will override this
                    if y != dy:
                        pixels[x, border_y] = COLOR_HARDBOX + (255,)
    
    # Draw depth dot (takes precedence, with special handling for overlap)
    # Depth dot on top border (rows 3-4)
    if 0 <= dx < original_width:
        border_x = 2 + dx
        if border_x < width:
            # Check if hardbox is also here (overlap case)
            if hb_x_min <= dx <= hb_x_max and hb_y_min <= dy <= hb_y_max:
                # Overlap: outer pixel (row 3) = hardbox, inner pixel (row 4) = depth dot
                pixels[border_x, 3] = COLOR_HARDBOX + (255,)
                pixels[border_x, 4] = COLOR_DEPTH_DOT + (255,)
            else:
                # No overlap: both pixels are depth dot
                pixels[border_x, 3] = COLOR_DEPTH_DOT + (255,)
                pixels[border_x, 4] = COLOR_DEPTH_DOT + (255,)
    
    # Depth dot on left border (columns 0-1)
    if 0 <= dy < original_height:
        border_y = 5 + dy
        if border_y < height:
            # Check if hardbox is also here (overlap case)
            if hb_x_min <= dx <= hb_x_max and hb_y_min <= dy <= hb_y_max:
                # Overlap: outer pixel (column 0) = hardbox, inner pixel (column 1) = depth dot
                pixels[0, border_y] = COLOR_HARDBOX + (255,)
                pixels[1, border_y] = COLOR_DEPTH_DOT + (255,)
            else:
                # No overlap: both pixels are depth dot
                pixels[0, border_y] = COLOR_DEPTH_DOT + (255,)
                pixels[1, border_y] = COLOR_DEPTH_DOT + (255,)
    
    return duck


def decode(duck_image: Image.Image) -> Dict[str, Any]:
    """
    Decode metadata from a DUCK image.
    
    Args:
        duck_image: DUCK format image
    
    Returns:
        Dictionary with keys: frame_numbers, depth_dot, hardbox, frame_delay, special, original_image
    """
    if duck_image.mode != 'RGBA':
        duck_image = duck_image.convert('RGBA')
    
    width, height = duck_image.size
    pixels = duck_image.load()
    
    # Validate color strip
    if width < 5 or height < 5:
        raise ValueError("Image too small to be a DUCK image")
    
    color_strip = [
        pixels[0, 0][:3],
        pixels[0, 1][:3],
        pixels[0, 2][:3],
        pixels[0, 3][:3],
        pixels[0, 4][:3]
    ]
    
    # Check if color strip has expected colors
    expected_strip = [
        COLOR_NORMAL_BORDER,
        COLOR_SPECIAL_BORDER,
        COLOR_TEXT,
        COLOR_DEPTH_DOT,
        COLOR_HARDBOX
    ]
    
    if color_strip != expected_strip:
        raise ValueError("Invalid DUCK image: color strip mismatch")
    
    # Read colors from strip
    normal_border_color = color_strip[0]
    special_border_color = color_strip[1]
    text_color = color_strip[2]
    depth_dot_color = color_strip[3]
    hardbox_color = color_strip[4]
    
    # Determine if special frame
    # Check border pixels to see which color is used
    border_sample = pixels[5, 0][:3]  # Sample from top border
    special = (border_sample == special_border_color)
    
    # Extract text from rows 0-2, starting at column 5
    text_data = [[], [], []]
    for x in range(5, width):
        for y in range(3):
            pixel = pixels[x, y][:3]
            if pixel == text_color:
                text_data[y].append(1)
            else:
                text_data[y].append(0)
    
    # Decode text
    frame_numbers, frame_delay = decode_text(text_data, text_color)
    
    # Find depth dot
    depth_dot = find_depth_dot(duck_image, depth_dot_color)
    
    # Find hardbox
    hardbox = find_hardbox(duck_image, hardbox_color, depth_dot)
    
    # Extract original image
    original_image = duck_image.crop((2, 5, width, height))
    
    # Trim to original size by finding where transparent pixels start
    # (indicating expansion beyond original content)
    orig_width = original_image.size[0]
    orig_height = original_image.size[1]
    
    # Find actual content bounds
    for x in range(orig_width - 1, -1, -1):
        has_content = False
        for y in range(orig_height):
            if original_image.getpixel((x, y))[3] > 0:  # Check alpha
                has_content = True
                break
        if has_content:
            orig_width = x + 1
            break
    
    for y in range(orig_height - 1, -1, -1):
        has_content = False
        for x in range(orig_width):
            if original_image.getpixel((x, y))[3] > 0:
                has_content = True
                break
        if has_content:
            orig_height = y + 1
            break
    
    original_image = original_image.crop((0, 0, orig_width, orig_height))
    
    return {
        'frame_numbers': frame_numbers,
        'depth_dot': depth_dot,
        'hardbox': hardbox,
        'frame_delay': frame_delay,
        'special': special,
        'original_image': original_image
    }


def decode_text(text_pixels: List[List[int]], text_color: Tuple[int, int, int]) -> Tuple[List[int], Optional[int]]:
    """
    Decode 3x3 font text from pixel data.
    Returns (frame_numbers, frame_delay)
    """
    # This is a simplified decoder - in production you'd want more robust OCR
    # For now, we'll parse the structure we know we created
    
    chars = []
    i = 0
    
    while i < len(text_pixels[0]):
        # Try to match a 3x3 character
        if i + 2 >= len(text_pixels[0]):
            break
        
        char_pattern = [
            text_pixels[0][i:i+3],
            text_pixels[1][i:i+3],
            text_pixels[2][i:i+3]
        ]
        
        # Match against known patterns
        matched = False
        for char, pattern in FONT_3X3.items():
            if char_pattern == pattern:
                chars.append(char)
                matched = True
                break
        
        if matched:
            i += 3
            
            # Check for gap (1 or 2 pixels)
            gap_size = 0
            while i < len(text_pixels[0]) and text_pixels[0][i] == 0 and text_pixels[1][i] == 0 and text_pixels[2][i] == 0:
                gap_size += 1
                i += 1
            
            # 2-pixel gap = frame number separator
            if gap_size == 2:
                chars.append('|')
        else:
            i += 1
    
    # Parse the character string
    text = ''.join(chars)
    parts = text.split('-')
    
    frame_text = parts[0]
    frame_delay = int(parts[1]) if len(parts) > 1 else None
    
    # Split by '|' to get individual frame numbers
    frame_numbers = [int(f) for f in frame_text.split('|') if f]
    
    return frame_numbers, frame_delay


def find_depth_dot(duck_image: Image.Image, depth_dot_color: Tuple[int, int, int]) -> Tuple[int, int]:
    """Find depth dot coordinates from border visualization."""
    pixels = duck_image.load()
    width, height = duck_image.size
    
    # Search top border (rows 3-4) for depth dot
    dx = None
    for x in range(2, width):
        if pixels[x, 4][:3] == depth_dot_color:  # Inner pixel (row 4)
            dx = x - 2
            break
    
    # Search left border (columns 0-1) for depth dot
    dy = None
    for y in range(5, height):
        if pixels[1, y][:3] == depth_dot_color:  # Inner pixel (column 1)
            dy = y - 5
            break
    
    if dx is None or dy is None:
        raise ValueError("Could not find depth dot in DUCK image")
    
    return (dx, dy)


def find_hardbox(duck_image: Image.Image, hardbox_color: Tuple[int, int, int], depth_dot: Tuple[int, int]) -> Tuple[int, int, int, int]:
    """Find hardbox coordinates from border visualization."""
    pixels = duck_image.load()
    width, height = duck_image.size
    dx, dy = depth_dot
    
    # Find hardbox bounds on top border (row 3 or 4)
    x_min = None
    x_max = None
    for x in range(2, width):
        if pixels[x, 3][:3] == hardbox_color or pixels[x, 4][:3] == hardbox_color:
            if x_min is None:
                x_min = x - 2
            x_max = x - 2
    
    # Find hardbox bounds on left border (column 0 or 1)
    y_min = None
    y_max = None
    for y in range(5, height):
        if pixels[0, y][:3] == hardbox_color or pixels[1, y][:3] == hardbox_color:
            if y_min is None:
                y_min = y - 5
            y_max = y - 5
    
    if x_min is None or x_max is None or y_min is None or y_max is None:
        raise ValueError("Could not find hardbox in DUCK image")
    
    # Convert to depth-dot-relative coordinates
    left = dx - x_min
    right = x_max - dx
    top = dy - y_min
    bottom = y_max - dy
    
    return (left, right, top, bottom)


def main():
    """Command-line interface for HATCH."""
    parser = argparse.ArgumentParser(
        description='HATCH - Hardbox Annotated Transformation Caption Helper\n'
                    'Creates DUCK (Dink Universal Caption Keyframe) images',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode image with metadata')
    encode_parser.add_argument('input', help='Input image path')
    encode_parser.add_argument('output', help='Output image path (PNG format)')
    encode_parser.add_argument('-f', '--frames', required=True, help='Frame numbers (comma-separated, e.g., "1,12,3")')
    encode_parser.add_argument('-d', '--depth-dot', required=True, help='Depth dot coordinates (x,y)')
    encode_parser.add_argument('-hb', '--hardbox', required=True, help='Hardbox in dink.ini format (left_x,top_y,right_x,bottom_y). Use -hb=-14,-9,14,10 for negative values')
    encode_parser.add_argument('-fd', '--frame-delay', type=int, help='Frame delay value')
    encode_parser.add_argument('-s', '--special', action='store_true', help='Special frame flag')
    
    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode DUCK image metadata')
    decode_parser.add_argument('input', help='Input DUCK image path')
    decode_parser.add_argument('-o', '--output', help='Output original image path (optional)')
    
    args = parser.parse_args()
    
    if args.command == 'encode':
        # Load input image
        try:
            image = Image.open(args.input)
        except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return 1
        
        # Parse arguments
        try:
            frame_numbers = [int(f.strip()) for f in args.frames.split(',')]
            dx, dy = map(int, args.depth_dot.split(','))
            # Parse hardbox in dink.ini format: left_x,top_y,right_x,bottom_y
            # Convert to internal format: left,right,top,bottom (positive distances)
            left_x, top_y, right_x, bottom_y = map(int, args.hardbox.split(','))
            hb_left = -left_x  # distance to left edge
            hb_top = -top_y    # distance to top edge
            hb_right = right_x  # distance to right edge
            hb_bottom = bottom_y  # distance to bottom edge
        except Exception as e:
            print(f"Error parsing arguments: {e}", file=sys.stderr)
            return 1
        
        # Encode
        try:
            duck = encode(
                image,
                frame_numbers=frame_numbers,
                depth_dot=(dx, dy),
                hardbox=(hb_left, hb_right, hb_top, hb_bottom),
                frame_delay=args.frame_delay,
                special=args.special
            )
            duck.save(args.output, 'PNG')
            print(f"DUCK image saved to {args.output}")
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return 1
    
    elif args.command == 'decode':
        # Load DUCK image
        try:
            duck_image = Image.open(args.input)
        except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return 1
        
        # Decode
        try:
            metadata = decode(duck_image)

            # Convert hardbox from internal format to dink.ini format
            hb_left, hb_right, hb_top, hb_bottom = metadata['hardbox']
            left_x = -hb_left
            top_y = -hb_top
            right_x = hb_right
            bottom_y = hb_bottom
            hardbox_dink_format = f"{left_x},{top_y},{right_x},{bottom_y}"

            print("DUCK Image Metadata:")
            print(f"  Frame Numbers: {', '.join(map(str, metadata['frame_numbers']))}")
            print(f"  Depth Dot: {metadata['depth_dot']}")
            print(f"  Hardbox (dink.ini format): {hardbox_dink_format}")
            print(f"  Frame Delay: {metadata['frame_delay']}")
            print(f"  Special: {metadata['special']}")
            
            if args.output:
                metadata['original_image'].save(args.output, 'PNG')
                print(f"\nOriginal image saved to {args.output}")
        
        except Exception as e:
            print(f"Error decoding image: {e}", file=sys.stderr)
            return 1
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
