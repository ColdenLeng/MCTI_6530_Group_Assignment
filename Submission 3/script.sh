#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
    echo "Please provide the path to either MCTI_6530_Group_Assignment-main directory or MCTI_6530_Group_Assignment-main.zip"
    exit 1
fi

# Get the path from the argument
input_path="$1"

# Check if it's a directory
if [ -d "$input_path" ]; then
    echo "Directory detected: $input_path"
    cd "$input_path/submission2/executables" || {
        echo "Failed to navigate to submission2/executables"
        exit 1
    }
    echo "Navigated to $(pwd)"
# Check if it's a zip file
elif [[ "$input_path" == *.zip ]]; then
    echo "ZIP file detected: $input_path"
    unzip -P infected "$input_path" -d "$(dirname "$input_path")" || {
        echo "Failed to unzip the file"
        exit 1
    }
    # Navigate to the extracted directory
    extracted_dir="${input_path%.zip}"
    cd "$extracted_dir/submission2/executables" || {
        echo "Failed to navigate to submission2/executables after unzipping"
        exit 1
    }
    echo "Navigated to $(pwd)"
else
    echo "Invalid input. Please provide either a directory or a .zip file"
    exit 1
fi

# Create opcode directories with the same structure as submission2/executables
opcode_hex_dir="../../opcode_hex"
opcode_mnemonic_dir="../../opcode_mnemonic"
mkdir -p "$opcode_hex_dir" "$opcode_mnemonic_dir"
echo "Created opcode directories at $opcode_hex_dir and $opcode_mnemonic_dir"

# Find and process each zip file within subdirectories
find . -mindepth 2 -type f -name "*.zip" | while read -r zip_file; do
    echo "Processing $zip_file"
    
    # Create corresponding directories in opcode_hex and opcode_mnemonic directories
    relative_path="${zip_file#./}"
    subdir_path=$(dirname "$relative_path")
    mkdir -p "$opcode_hex_dir/$subdir_path" "$opcode_mnemonic_dir/$subdir_path"
    
    # Unzip with possible password "infected" into a temporary directory
    temp_dir=$(mktemp -d)
    unzip -P infected "$zip_file" -d "$temp_dir" >/dev/null 2>&1

    # Process unzipped content
    for unzipped_file in "$temp_dir"/*; do
        if [ -f "$unzipped_file" ]; then
            # Check if it's not a directory, zip, or APK
            if [[ ! "$unzipped_file" == *.zip && ! "$unzipped_file" == *.apk ]]; then
                # Generate opcode file names
                opcode_hex_file="${unzipped_file##*/}.opcode_hex"
                opcode_mnemonic_file="${unzipped_file##*/}.opcode_mnemonic"
                opcode_hex_path="$opcode_hex_dir/$subdir_path/$opcode_hex_file"
                opcode_mnemonic_path="$opcode_mnemonic_dir/$subdir_path/$opcode_mnemonic_file"

                # Disassemble to extract hex opcodes
                objdump -d "$unzipped_file" | grep -oP '^\s*[0-9a-f]+:\s+\K([0-9a-f]{2}\s+)+' | awk '{print $1}' > "$opcode_hex_path" 2>/dev/null || {
                    echo "Failed to extract hex opcodes from $unzipped_file"
                    continue
                }
                echo "Hex opcode saved at $opcode_hex_path"

                # Disassemble to extract mnemonic opcodes
                objdump -d "$unzipped_file" | grep -oP '^\s*[0-9a-f]+:\s+[0-9a-f\s]+\s+\K(\w+)' > "$opcode_mnemonic_path" 2>/dev/null || {
                    echo "Failed to extract mnemonic opcodes from $unzipped_file"
                    continue
                }
                echo "Mnemonic opcode saved at $opcode_mnemonic_path"
            fi
        fi
    done
    
    # Remove the temporary unzipped content
    rm -rf "$temp_dir"
    echo "Cleaned up temporary files for $zip_file"
done

# Zip the opcode_hex and opcode_mnemonic directories
cd ../../
zip -r opcode_hex.zip opcode_hex >/dev/null 2>&1
zip -r opcode_mnemonic.zip opcode_mnemonic >/dev/null 2>&1
echo "Zipped opcode_hex to opcode_hex.zip and opcode_mnemonic to opcode_mnemonic.zip"

echo "Process completed. Zipped files are saved as opcode_hex.zip and opcode_mnemonic.zip."
