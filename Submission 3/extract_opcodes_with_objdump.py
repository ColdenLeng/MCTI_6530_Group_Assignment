import os
import zipfile
import subprocess
from pathlib import Path
import shutil
import re

def save_disassembly_to_txt(file_path, output_txt_path):
    """Disassemble the binary file and save the output to a .txt file."""
    try:
        with open(output_txt_path, 'w') as f:
            subprocess.run(
                ["objdump", "-d", "-M", "intel", str(file_path)],
                stdout=f,
                text=True,
                check=True
            )
        print(f"Disassembly saved to {output_txt_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running objdump on {file_path}: {e}")

def extract_mnemonics_from_txt(txt_file_path, opcode_output_path):
    """Extract mnemonics from the disassembly .txt file and save to .opcode file."""
    mnemonics = []
    mnemonic_pattern = re.compile(r'^\s*[0-9a-f]+:\s+([0-9a-f]{2}\s+)+\s+([a-z]+)\b', re.IGNORECASE)

    try:
        with open(txt_file_path, 'r') as f:
            for line in f:
                match = mnemonic_pattern.search(line)
                if match:
                    mnemonic = match.group(2)
                    mnemonics.append(mnemonic)

        # Save mnemonics to .opcode file
        with open(opcode_output_path, 'w') as f:
            f.write("\n".join(mnemonics))
        print(f"Mnemonic sequence saved to {opcode_output_path}")

    except FileNotFoundError:
        print(f"Error: The file {txt_file_path} was not found.")

def process_zip_file(zip_path, opcode_result_dir):
    """Process the zip file, extract binary files, disassemble, and save mnemonics."""
    zip_path = Path(zip_path)
    zip_name = zip_path.stem  # Get the name of the ZIP file without the extension

    # Create subdirectories for txt files and opcode files
    txt_output_dir = zip_path.parent / "disassembly_txt"
    txt_output_dir.mkdir(exist_ok=True)

    # Create a specific folder for this ZIP's opcode files inside the opcode_result_dir
    opcode_zip_dir = opcode_result_dir / zip_name
    opcode_zip_dir.mkdir(parents=True, exist_ok=True)

    # Create a temporary directory for extracting the ZIP contents
    temp_dir = zip_path.parent / "temp_extract"
    temp_dir.mkdir(exist_ok=True)

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Look for the 'exe' folder within the extracted contents
    exe_folder = next(temp_dir.rglob("exe"), None)
    if not exe_folder:
        print(f"No 'exe' folder found in {zip_path.stem}")
        return

    # Process each file in the 'exe' folder
    for file_path in exe_folder.iterdir():
        if file_path.is_file() and not file_path.suffix:
            print(f"Processing file: {file_path.name}")

            # Define paths for the txt and opcode files
            disassembly_txt_path = txt_output_dir / f"{file_path.stem}.txt"
            opcode_file_path = opcode_zip_dir / f"{file_path.stem}.opcode"

            # Save disassembly to the txt file
            save_disassembly_to_txt(file_path, disassembly_txt_path)

            # Extract mnemonics and save to the opcode file
            extract_mnemonics_from_txt(disassembly_txt_path, opcode_file_path)

    # Clean up the temporary extraction directory
    shutil.rmtree(temp_dir)
    print(f"Temporary files cleaned up for {zip_path.stem}.")

def process_all_folders(root_directory, opcode_result_dir):
    """Process each folder in the root directory, looking for a single ZIP file in each."""
    root_path = Path(root_directory)
    opcode_result_dir = Path(opcode_result_dir)

    # Ensure the root path and opcode result directory exist
    if not root_path.exists():
        print(f"Error: The root directory '{root_path}' does not exist.")
        return
    opcode_result_dir.mkdir(parents=True, exist_ok=True)

    # Process each folder in the root directory
    for folder in root_path.iterdir():
        if folder.is_dir():
            # Find the first ZIP file in the folder
            zip_files = list(folder.glob("*.zip"))
            if zip_files:
                zip_file_path = zip_files[0]
                print(f"\nProcessing folder: {folder.name} with ZIP file: {zip_file_path.name}")
                process_zip_file(zip_file_path, opcode_result_dir)
            else:
                print(f"No ZIP file found in {folder.name}")

def main():
    root_directory = "/Users/haihai/Desktop/cybersecurity/MCTI/Payloads_xiaohai"  # Set to your root directory path
    opcode_result_dir = "/Users/haihai/Desktop/cybersecurity/MCTI/opcode_result"  # Path to save opcode files
    process_all_folders(root_directory, opcode_result_dir)

if __name__ == "__main__":
    main()
