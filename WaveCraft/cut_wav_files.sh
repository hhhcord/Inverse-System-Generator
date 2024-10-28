#!/bin/bash

# Define the directory to search for .wav files
DIR="."

# Loop through all .wav files in the directory
for file in "$DIR"/*.wav; do
    # Check if the file exists
    if [[ -f "$file" ]]; then
        # Get the base name of the file (without extension)
        base_name=$(basename "$file" .wav)
        
        # Define the output file name with "_cut" added
        output_file="${base_name}_cut.wav"
        
        # Use ffmpeg to trim the first 4 seconds of the file
        ffmpeg -i "$file" -ss 00:00:04 -acodec copy "$output_file"
        
        # Print a message indicating the file has been processed
        echo "Processed: $file -> $output_file"
    fi
done
