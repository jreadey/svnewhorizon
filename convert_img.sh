#!/bin/bash

# Hugo Photo Optimization Script
# Usage: ./optimize-photos.sh [directory_path]

TARGET_DIR="${1:-.}"
MAX_DIM=1600

echo "Scanning directory: $TARGET_DIR (Target Max Width/Height: ${MAX_DIM}px)"

# Step 1: Convert any HEIC files to JPG
for img in "$TARGET_DIR"/*.{heic,HEIC}; do
    [ -e "$img" ] || continue
    filename="${img%.*}"
    echo "Converting HEIC: $(basename "$img") -> $(basename "$filename").jpg"
    sips -s format jpeg "$img" --out "${filename}.jpg" > /dev/null
    # Uncomment the line below if you want to delete the original HEIC files after conversion
    rm "$img"
done

# Step 2: Resize all JPG and PNG images
for img in "$TARGET_DIR"/*.{jpg,JPG,jpeg,JPEG,png,PNG}; do
    [ -e "$img" ] || continue
    echo "Resizing: $(basename "$img")"
    sips -Z $MAX_DIM "$img" > /dev/null
done

echo "All images successfully optimized and resized!"
