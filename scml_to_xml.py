import base64
import gzip
import io
import xml.etree.ElementTree as ET
import os

def decode_and_expand(xml_content_base64: str) -> str:
    """
    Decodes from Base64, decompresses GZip and returns decoded XML as string.
    """
    # decode Base64
    compressed = base64.b64decode(xml_content_base64)
    # decompress GZip
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as gz:
        decompressed = gz.read()
    return decompressed.decode('utf-8')

def scml_to_xml(input_scml_path: str, output_xml_path: str = None):
    """
    Reads SCML (XML with encoded blocks), decodes all <XmlContent>,
    and saves the result as a regular XML file.
    
    Args:
        input_scml_path: Path to input SCML file
        output_xml_path: Optional output path. If None, will create name with '_scml.xml' suffix
    """
    # Set default output path if not provided
    if output_xml_path is None:
        base_name = os.path.splitext(input_scml_path)[0]
        output_xml_path = f"{base_name}_scml.xml"

    # Parse the input file
    try:
        tree = ET.parse(input_scml_path)
        root = tree.getroot()

        # Find all XmlContent elements
        for elem in root.iter('XmlContent'):
            # Get raw Base64 data
            raw_b64 = elem.text.strip()
            # Decode and decompress
            decoded_xml = decode_and_expand(raw_b64)
            # Replace the content
            elem.clear()
            elem.text = decoded_xml

        # Save the new file
        tree.write(output_xml_path, encoding='utf-8', xml_declaration=True)
        print(f"Successfully converted: {input_scml_path} -> {output_xml_path}")
        return output_xml_path

    except Exception as e:
        print(f"Error processing {input_scml_path}: {str(e)}")
        raise

if __name__ == '__main__':
    # Example usage
    input_file = 'Sampler_1_DEAEQ99892_2.scml'
    output_file = 'Sampler_1_DEAEQ99892_2_scml.xml'  # Note the '_scml.xml' suffix
    
    scml_to_xml(input_file, output_file)
    print('Conversion complete')