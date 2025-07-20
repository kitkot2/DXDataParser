import os
import shutil

def rename_to_xml(input_path, output_dir, output_name=None):
    """Renames file to XML format with content copy and verification"""
    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}")
        return False

    try:
        # Determine output filename
        if output_name is None:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_name = f"{base_name}.xml"
        
        output_path = os.path.join(output_dir, output_name)
        
        # Skip if output already exists
        if os.path.exists(output_path):
            print(f"Warning: Output file already exists: {output_path}")
            return False
            
        # Copy with new extension (not just rename)
        with open(input_path, 'rb') as src, open(output_path, 'wb') as dst:
            dst.write(src.read())
        
        # Verify copy was successful
        if os.path.exists(output_path):
            return True
        else:
            print(f"Error: Failed to create output file: {output_path}")
            return False
            
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False