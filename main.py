import os
import shutil
import glob
import sys
from datetime import datetime

def copy_input_folders():
    """Copies all folders from Data_to_parse to Output directory"""
    input_dir = "Data_to_parse"
    output_dir = "Output"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    input_folders = [f for f in glob.glob(os.path.join(input_dir, '*')) 
                   if os.path.isdir(f)]
    
    print("\n=== Copying input folders ===")
    for folder in input_folders:
        folder_name = os.path.basename(folder)
        dest = os.path.join(output_dir, folder_name)
        
        if os.path.exists(dest):
            shutil.rmtree(dest)
            print(f"Cleaned existing: {dest}")
        
        shutil.copytree(folder, dest)
        print(f"Copied: {folder} → {dest}")
    
    return output_dir

def process_dx_files(root_dir):
    """Processes all .dx files with proper cleanup"""
    from dx_converter import convert_dx_to_csv
    
    print("\n=== Processing .dx files ===")
    dx_files = []
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.dx'):
                dx_files.append(os.path.join(dirpath, filename))
    
    for dx_file in dx_files:
        try:
            print(f"\nProcessing: {dx_file}")
            convert_dx_to_csv(dx_file, mode="clean")
            
            output_dir = os.path.splitext(dx_file)[0]
            if os.path.exists(output_dir):
                os.remove(dx_file)
                print(f"Successfully converted and removed: {dx_file}")
            else:
                print(f"Warning: Output folder not found: {output_dir}")
                
        except Exception as e:
            print(f"Error processing {dx_file}: {str(e)}")

def process_scml_files(root_dir):
    """Converts SCML to XML with proper suffix and cleanup"""
    from scml_to_xml import scml_to_xml
    
    print("\n=== Processing .scml files ===")
    scml_files = []
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.scml'):
                scml_files.append(os.path.join(dirpath, filename))
    
    for scml_file in scml_files:
        try:
            print(f"\nProcessing: {scml_file}")
            xml_file = f"{os.path.splitext(scml_file)[0]}_scml.xml"
            
            scml_to_xml(scml_file, xml_file)
            
            if os.path.exists(xml_file):
                os.remove(scml_file)
                print(f"Converted to: {xml_file}")
                print(f"Removed original: {scml_file}")
            else:
                print(f"Error: Output file not created: {xml_file}")
                
        except Exception as e:
            print(f"Error converting {scml_file}: {str(e)}")

def process_acaml_acmd_mfx_files(root_dir):
    """Converts acaml/acmd/mfx files to XML with format suffix and proper cleanup"""
    from acaml_acmd_mfx_to_xml import rename_to_xml
    
    print("\n=== Processing acaml/acmd/mfx files ===")
    target_exts = ['.acaml', '.acmd', '.mfx']
    target_files = []
    
    # First collect all target files
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in target_exts:
                target_files.append(os.path.join(dirpath, filename))
    
    # Then process them with verification
    for file_path in target_files:
        try:
            print(f"\nProcessing: {file_path}")
            
            # Generate new filename with original extension marker
            base_name = os.path.splitext(file_path)[0]
            original_ext = os.path.splitext(file_path)[1][1:]  # Remove dot
            xml_file = f"{base_name}_{original_ext}.xml"
            
            # Skip if the converted file already exists (from previous run)
            if os.path.exists(xml_file):
                print(f"Skipping - already converted: {xml_file}")
                continue
                
            # Perform the conversion
            if rename_to_xml(file_path, os.path.dirname(file_path), os.path.basename(xml_file)):
                # Verify the new file was created
                if os.path.exists(xml_file):
                    # Remove original only after successful conversion
                    try:
                        os.remove(file_path)
                        print(f"Successfully converted to: {xml_file}")
                        print(f"Removed original: {file_path}")
                    except Exception as remove_error:
                        print(f"Converted but failed to remove original: {file_path}")
                        print(f"Error: {str(remove_error)}")
                else:
                    print(f"Conversion failed - output not created: {xml_file}")
            else:
                print(f"Conversion failed for: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

def process_xml_files(root_dir):
    """Processes XML files to TXT with proper cleanup"""
    from xml_parser import parse_xml, save_to_txt
    
    print("\n=== Processing XML files ===")
    xml_files = []
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.xml'):
                xml_files.append(os.path.join(dirpath, filename))
    
    for xml_file in xml_files:
        try:
            print(f"\nProcessing: {xml_file}")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            txt_file = f"{os.path.splitext(xml_file)[0]}_{timestamp}.txt"
            
            parsed_content = parse_xml(xml_file)
            save_to_txt(parsed_content, txt_file)
            
            if os.path.exists(txt_file):
                os.remove(xml_file)
                print(f"Converted to: {txt_file}")
                print(f"Removed original: {xml_file}")
            else:
                print(f"Error: Output file not created: {txt_file}")
                
        except Exception as e:
            print(f"Error processing {xml_file}: {str(e)}")

def main():
    print("=== Starting Data Processing Pipeline ===")
    
    try:
        # Step 1: Copy folders
        output_root = copy_input_folders()
        
        # Step 2: Process .dx files
        process_dx_files(output_root)
        
        # Step 3: Process .scml files
        process_scml_files(output_root)
        
        # Step 4: Process acaml/acmd/mfx files
        process_acaml_acmd_mfx_files(output_root)
        
        # Step 5: Process XML files
        process_xml_files(output_root)
        
        print("\n=== Processing Complete ===")
        print("All files processed successfully with proper cleanup.")
        
    except Exception as e:
        print(f"\n!!! Processing Failed !!!")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()