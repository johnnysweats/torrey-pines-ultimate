#!/usr/bin/env python3
from PIL import Image, ImageDraw
import os

# Create a 512x512 icon (standard Mac app icon size)
size = 512
img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Draw a simple tree (Torrey Pine style)
# Tree trunk (brown)
trunk_color = (139, 69, 19)
draw.rectangle([size//2 - 20, size//2 + 40, size//2 + 20, size//2 + 120], fill=trunk_color)

# Tree foliage (dark green for Torrey Pine)
foliage_color = (34, 139, 34)
# Main tree body
draw.ellipse([size//2 - 80, size//2 - 60, size//2 + 80, size//2 + 60], fill=foliage_color)
# Top of tree
draw.ellipse([size//2 - 60, size//2 - 100, size//2 + 60, size//2 - 20], fill=foliage_color)

# Save as PNG
img.save('torrey_pines_icon.png', 'PNG')
print("Icon created: torrey_pines_icon.png") 