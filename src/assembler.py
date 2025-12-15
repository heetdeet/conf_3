import re
import argparse

# Коды операций из спецификации
OPCODES = {
    "load_const": 43,
    "read_mem": 31,
    "write_mem": 58,
    "ror": 24  # ror = циклический сдвиг вправо
}

def parse_assembly(file_path):
    """
    Парсит JSON-файл с программой и возвращает промежуточное представление.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    intermediate = []
    line_num = 0
    for line in lines:
        line_num += 1
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        if '#' in line:
            line = line.split('#')[0].strip()
        
        match_load = re.match(r'R(\d+)\s*=\s*(-?\d+)$', line)
        if match_load:
            reg = int(match_load.group(1))
            const = int(match_load.group(2))
            if const < 0:
                const = const & 0x3FFF
            intermediate.append({
                "op": "load_const",
                "opcode": OPCODES["load_const"],
                "fields": {"A": OPCODES["load_const"], "B": const, "C": reg}
            })
            continue
        
        match_read = re.match(r'R(\d+)\s*=\s*\[\s*R(\d+)\s*\]$', line)
        if match_read:
            dst_reg = int(match_read.group(1))
            src_reg = int(match_read.group(2))
            if src_reg is None or dst_reg is None:
                raise ValueError("read_mem: missing 'src_reg' or 'dst_reg'")
            intermediate.append({
                "op": "read_mem",
                "opcode": OPCODES["read_mem"],
                "fields": {"A": OPCODES["read_mem"], "B": src_reg, "C": dst_reg}
            })
            continue
        
        match_write = re.match(r'\[\s*R(\d+)\s*\+\s*(-?\d+)\s*\]\s*=\s*R(\d+)$', line)
        if match_write:
            offset = int(match_write.group(2))
            base_reg = int(match_write.group(1))
            src_reg = int(match_write.group(3))
            if offset < 0:
                offset = offset & 0xFFFF
            intermediate.append({
                "op": "write_mem",
                "opcode": OPCODES["write_mem"],
                "fields": {"A": OPCODES["write_mem"], "B": offset, "C": base_reg, "D": src_reg}
            })
            continue
        
        match_ror = re.match(r'R(\d+)\s*=\s*R(\d+)\s*>>\s*R(\d+)$', line)
        if match_ror:
            src1_reg = int(match_ror.group(2))
            src2_reg = int(match_ror.group(3))
            dst_reg = int(match_ror.group(1))
            intermediate.append({
                "op": "ror",
                "opcode": OPCODES["ror"],
                "fields": {"A": OPCODES["ror"], "B": src1_reg, "C": src2_reg, "D": dst_reg}
            })
            continue
        
        raise ValueError(f"Строка {line_num}: Неизвестная команда или синтаксическая ошибка: '{line}'")

    
    return intermediate

def print_intermediate_test_format(intermediate):
    """
    Выводит промежуточное представление в формате полей и значений,
    как в тесте из спецификации УВМ.
    """
    print("=== Внутреннее представление (формат полей и значений) ===")
    for i, cmd in enumerate(intermediate):
        print(f"Команда {i}: {cmd['op']}")
        fields = cmd['fields']
        for field, value in fields.items():
            print(f"  {field}={value}")
        print()

def create_test_program():
    """
    Создает тестовую программу из спецификации в алгебраическом формате.
    """
    test_code = """# Тестовая программа из спецификации УВМ (вариант 16)
# Загрузка константы: A=43, B=536, C=0 -> 0x2B, 0x0C, 0x01
R0 = 536

# Чтение из памяти: A=31, B=5, C=1 -> 0x9F, 0x06
R1 = [R5]

# Запись в память: A=58, B=402, C=1, D=3 -> 0x3A, 0xC9, 0x80, 0x0C
[R1 + 402] = R3

# Циклический сдвиг вправо: A=24, B=1, C=2, D=6 -> 0x98, 0xC8
R6 = R1 >> R2
"""
    
    with open("test_program.asm", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    return test_code

def main():
    parser = argparse.ArgumentParser(description="Ассемблер УВМ (вариант 16) - Этап 1")
    parser.add_argument("input", help="Путь к исходному файлу с текстом программы (.asm)")
    parser.add_argument("output", help="Путь к двоичному файлу-результату (на этапе 1 не используется)")
    parser.add_argument("--test", action="store_true", help="Режим тестирования")
    
    args = parser.parse_args()
    
    if args.test:
        print("=== РЕЖИМ ТЕСТИРОВАНИЯ ===")
        print("1. Создание тестовой программы из спецификации...")
        
        # Создаем тестовую программу
        test_code = create_test_program()
        print("Создан файл test_program.asm")
        print("\nСодержимое тестовой программы:")
        print("-" * 40)
        print(test_code)
        print("-" * 40)
        
        print("\n2. Парсинг тестовой программы...")
        try:
            test_intermediate = parse_assembly("test_program.asm")
            print_intermediate_test_format(test_intermediate)
            
            # Сравнение с ожидаемыми значениями
            expected_values = [
                {"A": 43, "B": 536, "C": 0},
                {"A": 31, "B": 5, "C": 1},
                {"A": 58, "B": 402, "C": 1, "D": 3},
                {"A": 24, "B": 1, "C": 2, "D": 6}
            ]
            
            print("3. Сравнение с ожидаемыми значениями:")
            all_correct = True
            for i, (cmd, expected) in enumerate(zip(test_intermediate, expected_values)):
                if cmd['fields'] == expected:
                    print(f"  Команда {i}: OK")
                else:
                    print(f"  Команда {i}: ОШИБКА")
                    print(f"    Ожидалось: {expected}")
                    print(f"    Получено:  {cmd['fields']}")
                    all_correct = False
            
            if all_correct:
                print("\nВсе тестовые команды соответствуют спецификации!")
            else:
                print("\nОбнаружены несоответствия!")
        
        except Exception as e:
            print(f"Ошибка при парсинге: {e}")
            return 1
        
        print("\n4. Тестирование пользовательской программы...")
    
    # jбработка пользовательской программы
    try:
        intermediate = parse_assembly(args.input)
        print(f"Успешно разобрано {len(intermediate)} команд из файла '{args.input}'.")
        
        if args.test:
            print_intermediate_test_format(intermediate)
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return 1
    
    # На этапе 1 файл output не создается
    print(f"Файл '{args.output}' будет создан на этапе 2 (формирование машинного кода).")
    
    return 0

if __name__ == "__main__":
    exit(main())