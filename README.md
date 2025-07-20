# Agilent HPLC Data Processing Pipeline

## About
Automated pipeline for converting Agilent HPLC proprietary data formats to open standards. TESTED ONLY WITH DATA FROM Agilent HPLC 1260 II.

### Features
- Batch processing of multiple files
- Preserves original folder structure

### Supported Formats
| Input Format | Output Format |
|--------------|---------------|
| .dx          | .csv          |
| .scml        | _scml.txt     |
| .acaml       | _acaml.txt    |
| .acmd        | _acmd.txt     |
| .mfx         | _mfx.txt      |
| .xml         | .txt.         |

## Disclaimer
⚠️ **Important Notice**:
- Not affiliated with Agilent Technologies
- Requires creator permission for use

## Installation

### Clone repository
```bash
git clone https://github.com/kitkot2/DXDataParser.git
```
```bash
cd DXDataParser
```
Create virtual environment
```bash
python -m venv venv
```
```bash
source venv/bin/activate  # Linux/MacOS
.\venv\Scripts\activate   # Windows
```
Install dependencies
```bash
pip install -r requirements.txt
```
### Install R

## ▶️ Usage

1. Place your input data folders inside the `Data_to_parse/` directory. Each folder can contain any combination of the following file types:
   - `.dx`, `.uv`
   - `.scml`
   - `.acaml`, `.acmd`, `.mfx`
   - `.xml`

2. Run the main pipeline script from the root directory:

```bash
python main.py
```

3. The script will execute the following steps:
    - Copy all folders from Data_to_parse/ to Output/
    - Process each file type in sequence:
        * .dx, .uv → .csv
        * .scml → _scml.xml
        * .acaml, .acmd, .mfx → _acaml/acmd/mfx.xml
        * .xml → timestamped .txt
    - Delete intermediate files after successful conversion
    - Print detailed logs for every operation

4. The final results will appear in the Output/ folder with cleaned .txt and .csv files.

## 📬 Contacts

**Nikita Kotenko** – kotenko.na@phystech.edu  
GitHub Profile: [https://github.com/kitkot2](https://github.com/kitkot2)  
Project Repository: [https://github.com/kitkot2/DXDataParser](https://github.com/kitkot2/DXDataParser)