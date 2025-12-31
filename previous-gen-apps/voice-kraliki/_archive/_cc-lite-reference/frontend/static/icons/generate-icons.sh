#!/bin/bash
# Generate PWA icons from SVG or PNG source
# This script creates placeholder icons for development
# Replace with actual icon generation in production

echo "Generating PWA icon placeholders..."

sizes=(72 96 128 144 152 192 384 512)

for size in "${sizes[@]}"; do
  # Create a simple colored square as placeholder
  # In production, use ImageMagick or similar to convert from source
  echo "Creating ${size}x${size} icon..."

  # This creates a simple SVG that can be viewed in browsers
  cat > "icon-${size}.png.svg" << EOF
<svg width="$size" height="$size" xmlns="http://www.w3.org/2000/svg">
  <rect width="$size" height="$size" fill="#3b82f6"/>
  <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-size="${size/2}" font-family="Arial, sans-serif" font-weight="bold">CC</text>
</svg>
EOF
done

echo "✅ Icon placeholders generated!"
echo "Note: Replace these with actual PNG icons using:"
echo "  - ImageMagick: convert source.svg -resize 192x192 icon-192.png"
echo "  - Or use an online tool like realfavicongenerator.net"
