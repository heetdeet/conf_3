import json
import argparse

# Коды операций из спецификации
OPCODES = {
    "load_const": 43,
    "read_mem": 31,
    "write_mem": 58,
    "ror": 24  # ror = циклический сдвиг вправо
}

def parse_assembly(json_file_path):
    """
    Парсит JSON-файл с программой и возвращает промежуточное представление.
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        program = json.load(f)
    
    intermediate = []
    for cmd in program:
        op = cmd.get("op")
        
        if op == "load_const":
            const = cmd.get("const")
            reg = cmd.get("reg")
            if const is None or reg is None:
                raise ValueError("load_const: missing 'const' or 'reg'")
            intermediate.append({
                "op": op,
                "opcode": OPCODES[op],
                "fields": {"A": OPCODES[op], "B": const, "C": reg}
            })
        
        elif op == "read_mem":
            src_reg = cmd.get("src_reg")
            dst_reg = cmd.get("dst_reg")
            if src_reg is None or dst_reg is None:
                raise ValueError("read_mem: missing 'src_reg' or 'dst_reg'")
            intermediate.append({
                "op": op,
                "opcode": OPCODES[op],
                "fields": {"A": OPCODES[op], "B": src_reg, "C": dst_reg}
            })
        
        elif op == "write_mem":
            offset = cmd.get("offset")
            base_reg = cmd.get("base_reg")
            src_reg = cmd.get("src_reg")
            if offset is None or base_reg is None or src_reg is None:
                raise ValueError("write_mem: missing 'offset', 'base_reg' or 'src_reg'")
            intermediate.append({
                "op": op,
                "opcode": OPCODES[op],
                "fields": {"A": OPCODES[op], "B": offset, "C": base_reg, "D": src_reg}
            })
        
        elif op == "ror":
            src1_reg = cmd.get("src1_reg")
            src2_reg = cmd.get("src2_reg")
            dst_reg = cmd.get("dst_reg")
            if src1_reg is None or src2_reg is None or dst_reg is None:
                raise ValueError("ror: missing 'src1_reg', 'src2_reg' or 'dst_reg'")
            intermediate.append({
                "op": op,
                "opcode": OPCODES[op],
                "fields": {"A": OPCODES[op], "B": src1_reg, "C": src2_reg, "D": dst_reg}
            })
        
        else:
            raise ValueError(f"Unknown operation: {op}")
    
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

def test_specification_commands():
    """
    Тестовая программа из спецификации УВМ.
    Возвращает промежуточное представление для тестовых команд.
    """
    test_program = [
        {
            "op": "load_const",
            "const": 536,
            "reg": 0
        },
        {
            "op": "read_mem",
            "src_reg": 5,
            "dst_reg": 1
        },
        {
            "op": "write_mem",
            "offset": 402,
            "base_reg": 1,
            "src_reg": 3
        },
        {
            "op": "ror",
            "src1_reg": 1,
            "src2_reg": 2,
            "dst_reg": 6
        }
    ]
    
    # сохраняем тестовую программу в файл
    with open("test_spec.json", "w", encoding="utf-8") as f:
        json.dump(test_program, f, indent=2)
    
    return parse_assembly("test_spec.json")

def main():
    parser = argparse.ArgumentParser(description="Ассемблер УВМ - Этап 1")
    parser.add_argument("input", help="Путь к исходному файлу с текстом программы (JSON)")
    parser.add_argument("output", help="Путь к двоичному файлу-результату (на этапе 1 не используется)")
    parser.add_argument("--test", action="store_true", help="Режим тестирования")
    
    args = parser.parse_args()
    
    if args.test:
        print("=== ТЕСТИРОВАНИЕ ===")
        print("1. Проверка команд из спецификации УВМ...")
        
        # тест 1: Проверяем команды из спецификации
        test_intermediate = test_specification_commands()
        print_intermediate_test_format(test_intermediate)
        
        # сравнение с ожидаемыми значениями
        expected_values = [
            {"A": 43, "B": 536, "C": 0},      # load_const
            {"A": 31, "B": 5, "C": 1},        # read_mem
            {"A": 58, "B": 402, "C": 1, "D": 3},  # write_mem
            {"A": 24, "B": 1, "C": 2, "D": 6}     # ror
        ]
        
        print("2. Сравнение с ожидаемыми значениями:")
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
        
        print("\n3. Тестирование пользовательской программы...")
    
    # обработка пользовательской программы
    try:
        intermediate = parse_assembly(args.input)
        print(f"Успешно разобрано {len(intermediate)} команд из файла '{args.input}'.")
        
        if args.test:
            print_intermediate_test_format(intermediate)
            
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return 1
    
    print(f"Файл '{args.output}' будет создан на этапе 2 (формирование машинного кода).")
    
    return 0

if __name__ == "__main__":
    exit(main())