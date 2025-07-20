import xml.etree.ElementTree as ET
import os
from datetime import datetime
import re
import base64
import gzip
import io
import html

def clean_invalid_xml_chars(xml_str):
    """Удаление недопустимых символов из XML-строки"""
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', xml_str)

def decode_xml_content(content_type, content_text):
    """Декодирование содержимого XmlContent в зависимости от типа"""
    if not content_text:
        return content_text
        
    if content_type == "GZipCompressedBase64Xml":
        try:
            decoded = base64.b64decode(content_text)
            with gzip.GzipFile(fileobj=io.BytesIO(decoded)) as f:
                uncompressed = f.read()
            return uncompressed.decode('utf-8')
        except:
            return html.unescape(content_text)
    
    return html.unescape(content_text)

def parse_fileset(xml_root):
    """Парсинг Fileset XML с красивым форматированием"""
    result = ["=== Fileset XML ==="]
    namespace = {'ns': 'urn:schemas-agilent-com:Fileset'}
    
    # Основная информация о Fileset
    fileset_info = {
        "Identifier Algorithm": xml_root.get('IdentifierAlgorithm'),
        "Identifier": xml_root.get('Identifier')
    }
    result.append("\nFileset Information:")
    for key, value in fileset_info.items():
        result.append(f"  {key}: {value if value else 'N/A'}")
    
    # Детальная информация о файлах
    files = xml_root.findall('.//ns:File', namespace)
    if files:
        result.append("\nFiles:")
        for i, file in enumerate(files, 1):
            file_info = {
                "Path": file.get('Path'),
                "Identifier Algorithm": file.get('IdentifierAlgorithm'),
                "Identifier": file.get('Identifier')
            }
            
            # Свойства файла
            properties = {}
            for prop in file.findall('.//ns:Property', namespace):
                properties[prop.get('Name')] = prop.get('Value')
            
            result.append(f"\nFile #{i}:")
            for key, value in file_info.items():
                result.append(f"  {key}: {value}")
            
            if properties:
                result.append("  Properties:")
                for prop_name, prop_value in properties.items():
                    result.append(f"    {prop_name}: {prop_value}")
    
    # Полный XML для справки
    result.append("\nFull XML Content:")
    result.append(ET.tostring(xml_root, encoding='unicode', method='xml'))
    
    return "\n".join(result)

def parse_acaml(xml_root):
    """Parse ACAML XML with detailed formatting in English"""
    result = ["=== ACAML XML ==="]
    namespace = {'ns': 'urn:schemas-agilent-com:acaml21'}
    
    # 1. Basic Information
    result.append("\n--- BASIC INFORMATION ---")
    
    # Checksum
    checksum = xml_root.find('.//ns:Checksum', namespace)
    if checksum is not None:
        result.append("\n* Checksum:")
        result.append(f"  Algorithm: {checksum.get('Algorithm')}")
        result.append(f"  Value: {checksum.find('.//ns:Value', namespace).text}")
    
    # Migration History
    migrations = xml_root.findall('.//ns:MigrationStep', namespace)
    if migrations:
        result.append("\n* Migration History:")
        for i, migration in enumerate(migrations, 1):
            result.append(f"\n  Migration #{i}:")
            result.append(f"    From: {migration.find('.//ns:FromNamespace', namespace).text}")
            result.append(f"    To: {migration.find('.//ns:ToNamespace', namespace).text}")
            result.append(f"    Date: {migration.find('.//ns:Date', namespace).text}")
            result.append(f"    Application: {migration.find('.//ns:Application', namespace).text}")
    
    # 2. Document Information
    doc_info = xml_root.find('.//ns:DocInfo', namespace)
    if doc_info is not None:
        result.append("\n--- DOCUMENT INFORMATION ---")
        result.append(f"\n* Document ID: {xml_root.find('.//ns:DocID', namespace).text}")
        result.append(f"* Description: {doc_info.find('.//ns:Description', namespace).text}")
        result.append(f"* Created by user: {doc_info.find('.//ns:CreatedByUser', namespace).text}")
        
        # Application information
        app_info = doc_info.find('.//ns:AgilentApp', namespace)
        if app_info is not None:
            result.append("\n* Created by application:")
            result.append(f"  Name: {app_info.find('.//ns:Name', namespace).text}")
            result.append(f"  Version: {app_info.find('.//ns:Version', namespace).text}")
        
        result.append(f"* Creation date: {doc_info.find('.//ns:CreationDate', namespace).text}")
        result.append(f"* Client: {doc_info.find('.//ns:ClientName', namespace).text}")
        
        # Custom Fields
        custom_fields = doc_info.findall('.//ns:CustomField', namespace)
        if custom_fields:
            result.append("\n* Custom Fields:")
            for field in custom_fields:
                name = field.get('Name')
                value = field.find('.//ns:Value', namespace).text if field.find('.//ns:Value', namespace) is not None else ""
                result.append(f"  {name}: {value}")
                
                # Special handling for InjectionMetaDataItems
                if name == "InjectionMetaDataItems":
                    xml_content = field.find('.//ns:Xml', namespace)
                    if xml_content is not None and xml_content.text:
                        decoded = decode_xml_content(None, xml_content.text)
                        result.append("  Decoded XML content:")
                        result.append(decoded)
    
    # 3. Resources (Instruments)
    resources = xml_root.find('.//ns:Resources', namespace)
    if resources is not None:
        result.append("\n--- RESOURCES ---")
        
        # Instruments
        instruments = resources.findall('.//ns:Instrument', namespace)
        if instruments:
            result.append("\n* Instruments:")
            for instrument in instruments:
                result.append(f"\n  Instrument: {instrument.find('.//ns:Name', namespace).text}")
                result.append(f"    ID: {instrument.get('id')}")
                result.append(f"    Technique: {instrument.find('.//ns:Technique', namespace).text}")
                
                # Modules
                modules = instrument.findall('.//ns:Module', namespace)
                if modules:
                    result.append("\n    Modules:")
                    for module in modules:
                        result.append(f"\n      - Name: {module.find('.//ns:Name', namespace).text}")
                        result.append(f"        Type: {module.find('.//ns:Type', namespace).text}")
                        result.append(f"        Manufacturer: {module.find('.//ns:Manufacturer', namespace).text}")
                        result.append(f"        Part No: {module.find('.//ns:PartNo', namespace).text}")
                        result.append(f"        Serial No: {module.find('.//ns:SerialNo', namespace).text}")
                        result.append(f"        Firmware Revision: {module.find('.//ns:FirmwareRevision', namespace).text}")
                        result.append(f"        Connection Info: {module.find('.//ns:ConnectionInfo', namespace).text}")
                        result.append(f"        Instance: {module.find('.//ns:Instance', namespace).text}")
    
    # 4. Injections
    injections = xml_root.findall('.//ns:InjectionMetaData', namespace)
    if injections:
        result.append("\n--- INJECTION INFORMATION ---")
        for i, injection in enumerate(injections, 1):
            result.append(f"\n* Injection #{i}:")
            result.append(f"  HPLC Method: {injection.get('AcqMethodName')}")
            result.append(f"  Sample Name: {injection.get('SampleName')}")
            result.append(f"  Sample Description: {injection.get('SampleDescription')}")
            result.append(f"  Injector Position: {injection.get('InjectorPosition')}")
            result.append(f"  Vial Number: {injection.get('VialNumber')}")
            result.append(f"  Date/Time: {injection.get('InjectionAcqDateTime')}")
            result.append(f"  Data File: {injection.get('RawDataFileName')}")
            
            # Include all injection metadata
            for attr, value in injection.items():
                if attr not in ['AcqMethodName', 'SampleName', 'SampleDescription', 
                               'InjectorPosition', 'VialNumber', 'InjectionAcqDateTime', 
                               'RawDataFileName']:
                    result.append(f"  {attr}: {value}")
            
            # Include child elements
            for child in injection:
                if child.tag not in ['{urn:schemas-agilent-com:acaml21}Dil', 
                                   '{urn:schemas-agilent-com:acaml21}LimsIds']:
                    result.append(f"  {child.tag.split('}')[-1]}: {child.text}")
    
    # 5. Signals
    signals = xml_root.findall('.//ns:Signal', namespace)
    if signals:
        result.append("\n--- SIGNALS ---")
        result.append(f"Total signals: {len(signals)}")
        
        # Group by signal type
        signal_types = {}
        for signal in signals:
            sig_type = signal.find('.//ns:Type', namespace).text
            if sig_type not in signal_types:
                signal_types[sig_type] = []
            signal_types[sig_type].append(signal)
        
        for sig_type, sig_list in signal_types.items():
            result.append(f"\n* Signal Type: {sig_type} ({len(sig_list)} signals)")
            for signal in sig_list:
                result.append(f"\n  - Name: {signal.find('.//ns:Name', namespace).text}")
                result.append(f"    Description: {signal.find('.//ns:Description', namespace).text}")
                result.append(f"    Trace ID: {signal.find('.//ns:TraceID', namespace).text}")
                result.append(f"    Detector: {signal.find('.//ns:DetectorName', namespace).text}")
                result.append(f"    Channel: {signal.find('.//ns:ChannelName', namespace).text}")
                
                # Binary data references
                binary_data = signal.findall('.//ns:DataItem', namespace)
                if binary_data:
                    result.append("\n    Data References:")
                    for data in binary_data:
                        result.append(f"      Name: {data.find('.//ns:Name', namespace).text}")
                        result.append(f"      Path: {data.find('.//ns:Path', namespace).text}")
    
    # 6. Full XML content
    result.append("\n--- FULL XML CONTENT ---")
    full_xml = ET.tostring(xml_root, encoding='unicode', method='xml')
    result.append(full_xml)
    
    return "\n".join(result)

def parse_sample_container(xml_root):
    """Парсинг SampleContainerInfo XML"""
    result = ["=== SampleContainerInfo XML ==="]
    
    # Информация об устройстве
    device_info = xml_root.find('.//ContainerDeviceInfo')
    if device_info is not None:
        result.append("\nDevice Info:")
        result.append(f"Module ID: {device_info.get('ModuleId')}")
        result.append(f"Serial: {device_info.find('.//SerialNumber').text}")
        result.append(f"Part: {device_info.find('.//PartNumber').text}")
        
        # Декодированное содержимое
        container_device = device_info.find('.//SampleContainerDevice')
        if container_device is not None:
            decoded = decode_xml_content(
                container_device.get('ContentType'),
                container_device.find('.//XmlContent').text)
            result.append("\nDecoded Device Content:")
            result.append(decoded[:1000] + ("..." if len(decoded) > 1000 else ""))
    
    # Полный XML
    result.append("\nFull XML Content:")
    result.append(ET.tostring(xml_root, encoding='unicode', method='xml'))
    
    return "\n".join(result)

def parse_content_types(xml_root):
    """Парсинг Content Types XML с красивым форматированием"""
    result = ["=== Content Types XML ==="]
    namespace = {'ns': 'http://schemas.openxmlformats.org/package/2006/content-types'}
    
    # Форматированная таблица
    defaults = xml_root.findall('.//ns:Default', namespace)
    if defaults:
        result.append("\nContent Type Mappings:")
        result.append("+------------+--------------------------------------------------------------+")
        result.append("| Extension  | Content Type                                                 |")
        result.append("+------------+--------------------------------------------------------------+")
        
        for default in defaults:
            ext = default.get('Extension')
            ct = default.get('ContentType')
            result.append(f"| {ext.ljust(10)} | {ct.ljust(60)} |")
        
        result.append("+------------+--------------------------------------------------------------+")
    
    # Полный XML
    result.append("\nFull XML Content:")
    result.append(ET.tostring(xml_root, encoding='unicode', method='xml'))
    
    return "\n".join(result)

def parse_acmd(xml_root):
    """Parse ACMD XML with detailed formatting and no truncation"""
    result = ["=== ACMD XML ==="]
    namespace = {'ns': 'urn:schemas-agilent-com:acmd20'}
    
    # 1. Injection Information
    injection = xml_root.find('.//ns:InjectionInfo', namespace)
    if injection is not None:
        result.append("\n--- INJECTION INFORMATION ---")
        result.append("\n* Sample Details:")
        result.append(f"  - Name: {injection.find('.//ns:SampleName', namespace).text}")
        result.append(f"  - Location: {injection.find('.//ns:Location', namespace).text}")
        result.append(f"  - Operator: {injection.find('.//ns:RunOperator', namespace).text}")
        result.append(f"  - Run Time: {injection.find('.//ns:RunDateTime', namespace).text}")
        
        result.append("\n* Injection Parameters:")
        result.append(f"  - Volume: {injection.find('.//ns:InjectionVolume', namespace).text} "
                     f"{injection.find('.//ns:InjectionVolumeUnits', namespace).text}")
        result.append(f"  - Sequence Line: {injection.find('.//ns:SequenceLine', namespace).text}")
        result.append(f"  - Replicate: {injection.find('.//ns:Replicate', namespace).text}")
        result.append(f"  - Source: {injection.find('.//ns:InjectionSource', namespace).text}")
        
        method = injection.find('.//ns:AcquisitionMethod', namespace)
        if method is not None:
            result.append("\n* Method:")
            result.append(f"  {method.text}")
        
        barcode = injection.find('.//ns:Barcode', namespace)
        if barcode is not None and barcode.text:
            result.append("\n* Barcode:")
            result.append(f"  {barcode.text}")

    # 2. Signal Analysis - Show ALL signals without truncation
    signals = xml_root.findall('.//ns:Signal', namespace)
    if signals:
        result.append("\n--- SIGNAL ANALYSIS ---")
        result.append(f"Total signals detected: {len(signals)}")
        
        # Group by device type
        devices = {}
        for signal in signals:
            device = signal.find('.//ns:DeviceName', namespace).text
            if device not in devices:
                devices[device] = []
            devices[device].append(signal)
        
        for device, sig_list in devices.items():
            result.append(f"\n* Device: {device} ({len(sig_list)} signals)")
            
            for sig in sig_list:
                result.append("\n  - Channel: " + (sig.find('.//ns:ChannelName', namespace).text or "N/A"))
                result.append(f"    Description: {sig.find('.//ns:Description', namespace).text}")
                result.append(f"    Type: {sig.find('.//ns:Encoding', namespace).text.split('/')[-1]}")
                result.append(f"    Units: {sig.find('.//ns:Units', namespace).text}")
                result.append(f"    Data Points: {sig.find('.//ns:NumberOfValues', namespace).text}")
                result.append(f"    Time Range: {sig.find('.//ns:TimeStart', namespace).text}-"
                            f"{sig.find('.//ns:TimeEnd', namespace).text}")
                result.append(f"    Value Range: {sig.find('.//ns:Minimum', namespace).text}-"
                            f"{sig.find('.//ns:Maximum', namespace).text}")
                result.append(f"    Trace ID: {sig.find('.//ns:TraceId', namespace).text}")
                
                # Additional signal properties
                result.append(f"    Device Number: {sig.find('.//ns:DeviceNumber', namespace).text}")
                result.append(f"    Slope: {sig.find('.//ns:Slope', namespace).text}")
                result.append(f"    Scale Factor: {sig.find('.//ns:ScaleFactor', namespace).text}")
                result.append(f"    Detector Type: {sig.find('.//ns:DetectorType', namespace).text}")
                
                # Highlight integrable signals
                if sig.find('.//ns:IsIntegrable', namespace).text.lower() == 'true':
                    result.append("    NOTE: This signal is integrable")
    
    # 3. External References
    ext_refs = xml_root.findall('.//ns:ExternalElementPaths', namespace)
    if any(ref.text for ref in ext_refs):
        result.append("\n--- EXTERNAL REFERENCES ---")
        result.append("Linked data files:")
        for ref in (r.text for r in ext_refs if r.text):
            result.append(f"  - {ref}")

    # 4. Full XML (uncompressed)
    result.append("\n--- FULL XML CONTENT ---")
    full_xml = ET.tostring(xml_root, encoding='unicode', method='xml')
    result.append(full_xml)
    
    return "\n".join(result)

def parse_xml(file_path):
    try:
        with open(file_path, 'rb') as f:
            xml_str = clean_invalid_xml_chars(f.read().decode('utf-8', errors='ignore'))
        
        tree = ET.parse(io.StringIO(xml_str))
        root = tree.getroot()
        
        if root.tag.endswith('Fileset') or 'urn:schemas-agilent-com:Fileset' in root.tag:
            return parse_fileset(root)
        elif root.tag.endswith('ACAML') or 'urn:schemas-agilent-com:acaml21' in root.tag:
            return parse_acaml(root)
        elif root.tag == 'SampleContainerInfo':
            return parse_sample_container(root)
        elif root.tag.endswith('Types') or 'http://schemas.openxmlformats.org/package/2006/content-types' in root.tag:
            return parse_content_types(root)
        elif root.tag.endswith('ACMD') or 'urn:schemas-agilent-com:acmd20' in root.tag:
            return parse_acmd(root)
        else:
            return f"Unknown XML type: {root.tag}\n\nFull Content:\n{xml_str}"
    
    except Exception as e:
        return f"Error processing file: {str(e)}\n\nFile content:\n{open(file_path, 'r', errors='ignore').read()}"

def save_to_txt(content, output_path):
    """Сохраняет результат в текстовый файл"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Результат сохранён в: {output_path}")
    

def process_test_files():
    test_folder = "./Test_xml"
    if not os.path.exists(test_folder):
        print(f"Test folder not found: {test_folder}")
        return
    
    # Создаем папку для результатов, если её нет
    output_folder = os.path.join(test_folder, "results")
    os.makedirs(output_folder, exist_ok=True)
    
    # Получаем список XML файлов в тестовой папке
    xml_files = [f for f in os.listdir(test_folder) if f.lower().endswith('.xml')]
    
    if not xml_files:
        print(f"No XML files found in {test_folder}")
        return
    
    print(f"Found {len(xml_files)} XML files to process:")
    
    for xml_file in xml_files:
        xml_path = os.path.join(test_folder, xml_file)
        print(f"\nProcessing: {xml_file}")
        
        try:
            # Парсим XML
            parsed = parse_xml(xml_path)
            
            # Сохраняем результат
            output_file = os.path.join(output_folder, 
                                     f"{os.path.splitext(xml_file)[0]}_"
                                     f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            save_to_txt(parsed, output_file)
            print(f"Successfully processed. Results saved to: {os.path.basename(output_file)}")
        
        except Exception as e:
            print(f"Error processing {xml_file}: {str(e)}")

if __name__ == "__main__":
    # Запускаем обработку тестовых файлов вместо ввода пути вручную
    process_test_files()