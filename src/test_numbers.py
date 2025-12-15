# test_numbers.py
import re

def test_number_parsing():
    """Тестирование корректности интерпретации чисел"""
    
    test_cases = [
        # load_const (константа 0..16383)
        ("R0 = 0", {"op": "load_const", "const": 0, "reg": 0}),
        ("R7 = 16383", {"op": "load_const", "const": 16383, "reg": 7}),
        ("R3 = 100", {"op": "load_const", "const": 100, "reg": 3}),
        
        # read_mem (регистры 0..7)
        ("R0 = [R0]", {"op": "read_mem", "src": 0, "dst": 0}),
        ("R7 = [R7]", {"op": "read_mem", "src": 7, "dst": 7}),
        ("R3 = [R5]", {"op": "read_mem", "src": 5, "dst": 3}),
        
        # write_mem (смещение 0..65535)
        ("[R0 + 0] = R0", {"op": "write_mem", "base": 0, "offset": 0, "src": 0}),
        ("[R7 + 65535] = R7", {"op": "write_mem", "base": 7, "offset": 65535, "src": 7}),
        ("[R2 + 1000] = R3", {"op": "write_mem", "base": 2, "offset": 1000, "src": 3}),
        
        # ror (регистры 0..7)
        ("R0 = R0 >> R0", {"op": "ror", "src1": 0, "src2": 0, "dst": 0}),
        ("R7 = R7 >> R7", {"op": "ror", "src1": 7, "src2": 7, "dst": 7}),
        ("R3 = R1 >> R2", {"op": "ror", "src1": 1, "src2": 2, "dst": 3}),
    ]
    
    print("=== Тестирование парсинга чисел ===")
    
    for i, (code, expected) in enumerate(test_cases):
        print(f"\nТест {i+1}: {code}")
        
        # Проверяем load_const
        if "op" in expected and expected["op"] == "load_const":
            match = re.match(r'R(\d+)\s*=\s*(-?\d+)$', code)
            if match:
                reg = int(match.group(1))
                const = int(match.group(2))
                print(f"  Найдено: reg={reg}, const={const}")
                print(f"  Ожидалось: reg={expected['reg']}, const={expected['const']}")
                assert reg == expected['reg'], f"Ошибка регистра: {reg} != {expected['reg']}"
                assert const == expected['const'], f"Ошибка константы: {const} != {expected['const']}"
                print("  ✓ OK")
        
        # Аналогично для других команд...