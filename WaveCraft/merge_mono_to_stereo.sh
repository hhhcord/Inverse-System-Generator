#!/bin/bash

# Display an error message if input files are not provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <left_channel_file> <right_channel_file>"
    exit 1
fi

# Get the input file names
left_file="$1"
right_file="$2"

# Get the base name of the output file
base_name="${left_file%_L.wav}"

# Output file name for the stereo file
stereo_output="${base_name}_stereo.wav"

# Use ffmpeg to merge left and right mono files into a stereo file
ffmpeg -i "$left_file" -i "$right_file" -filter_complex \
"[0:a][1:a]amerge=inputs=2,pan=stereo|c0<c0|c1<c1" -ac 2 "$stereo_output"

# Completion message
echo "The mono files have been merged into a stereo file: $stereo_output"
