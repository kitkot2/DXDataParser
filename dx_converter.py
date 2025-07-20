# dx_converter.py
import subprocess
import os
from typing import Optional

def convert_dx_to_csv(dx_file: str, mode: str = "clean", r_script_path: Optional[str] = None) -> None:
    """
    Конвертирует файл .dx в CSV и другие файлы, используя R-скрипт.
    
    Параметры:
        dx_file (str): Путь к .dx файлу для конвертации
        mode (str): Режим работы ("clean" или "full")
        r_script_path (str, optional): Путь к R-скрипту. Если None, ищется в той же директории.
    
    Возвращает:
        None
    """
    # Определяем путь к R-скрипту
    if r_script_path is None:
        r_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dx_converter.R")
    
    # Проверяем существование файлов
    if not os.path.exists(dx_file):
        raise FileNotFoundError(f"DX файл не найден: {dx_file}")
    if not os.path.exists(r_script_path):
        raise FileNotFoundError(f"R-скрипт не найден: {r_script_path}")
    
    # Формируем команду для выполнения
    cmd = [
        "Rscript",
        "--vanilla",
        r_script_path,
        dx_file,
        mode
    ]
    
    # Выполняем команду
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении R-скрипта: {e.stderr}")
        raise
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    # Пример использования
    import argparse
    
    parser = argparse.ArgumentParser(description="Конвертер DX файлов в CSV")
    parser.add_argument("dx_file", help="Путь к DX файлу")
    parser.add_argument("--mode", default="clean", choices=["clean", "full"], 
                       help="Режим работы: clean (только CSV) или full (все файлы)")
    args = parser.parse_args()
    
    convert_dx_to_csv(args.dx_file, args.mode)