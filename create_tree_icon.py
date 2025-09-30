from PIL import Image, ImageDraw

# Create a 512x512 image with transparent background
size = 512
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Tree colors
trunk_color = (139, 69, 19)  # Brown
leaves_color = (34, 139, 34)  # Forest green
leaves_highlight = (50, 205, 50)  # Lime green

# Draw trunk
trunk_width = size // 8
trunk_height = size // 3
trunk_x = (size - trunk_width) // 2
trunk_y = size - trunk_height - 50
draw.rectangle([trunk_x, trunk_y, trunk_x + trunk_width, trunk_y + trunk_height], fill=trunk_color)

# Draw tree leaves (multiple circles for a natural look)
leaf_centers = [
    (size // 2, trunk_y - 100),  # Main top
    (size // 2 - 80, trunk_y - 60),  # Left side
    (size // 2 + 80, trunk_y - 60),  # Right side
    (size // 2 - 40, trunk_y - 120),  # Left top
    (size // 2 + 40, trunk_y - 120),  # Right top
    (size // 2, trunk_y - 160),  # Top tip
]

for center in leaf_centers:
    radius = 60
    # Main leaf circle
    draw.ellipse([center[0] - radius, center[1] - radius, 
                   center[0] + radius, center[1] + radius], 
                  fill=leaves_color)
    
    # Highlight circle
    highlight_radius = radius - 15
    draw.ellipse([center[0] - highlight_radius, center[1] - highlight_radius - 10, 
                   center[0] + highlight_radius, center[1] + highlight_radius - 10], 
                  fill=leaves_highlight)

# Save as PNG
img.save('tree_icon.png')
print("Tree icon created: tree_icon.png") 