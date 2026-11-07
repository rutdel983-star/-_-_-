"""Этап 2 (Вариант А): Валидация данных data.json по правилам контракта schema.json."""
import copy
import json
from typing import Any

def load_json_file(filename: str) -> dict[str, Any]:
    """Загружает любой JSON-файл с диска в словарь Python."""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

def validate_by_schema(data: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, list[str]]:
    """Проверяет словарь data по правилам, прочитанным из файла schema.json.

    Returns:
        Кортеж (True/False, список найденных нарушений контракта).
    """
    errors: list[str] = []
    req_fields: list[str] = schema.get("required", [])
    props: dict[str, Any] = schema.get("properties", {})

    # 1. Проверка наличия всех обязательных ключей из списка required
    for field in req_fields:
        if field not in data:
            errors.append(f"Отсутствует обязательное поле '{field}'")
    if errors:
        return False, errors

    # 2. Проверка строковых полей (minLength)
    for str_field in ("well_id", "field_name"):
        if str_field in data:
            if not isinstance(data[str_field], str) or len(data[str_field].strip()) < 1:
                errors.append(f"Поле '{str_field}' должно быть непустой строкой")

    # 3. Проверка целочисленной глубины depth_m по границам из schema.json
    d_rules = props["depth_m"]
    depth = data["depth_m"]
    if not isinstance(depth, int) or isinstance(depth, bool):
        errors.append("Поле 'depth_m' должно быть целым числом (integer)")
    elif not (d_rules["minimum"] <= depth <= d_rules["maximum"]):
        errors.append(
            f"Глубина depth_m={depth} вне границ схемы "
            f"[{d_rules['minimum']}; {d_rules['maximum']}]"
        )

    # 4. Проверка числовых полей q_liq и w_pct по границам из schema.json
    for num_field in ("q_liq", "w_pct"):
        rules = props[num_field]
        val = data[num_field]
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            errors.append(f"Поле '{num_field}' должно быть числом (number)")
        elif not (rules["minimum"] <= float(val) <= rules["maximum"]):
            errors.append(
                f"Поле {num_field}={val} вне границ схемы "
                f"[{rules['minimum']}; {rules['maximum']}]"
            )

    # 5. Проверка булева поля is_active
    if not isinstance(data["is_active"], bool):
        errors.append("Поле 'is_active' должно быть логическим типом (boolean)")

    # 6. Проверка вложенного объекта pump
    pump = data["pump"]
    pump_schema = props["pump"]
    if not isinstance(pump, dict):
        errors.append("Поле 'pump' должно быть вложенным словарём (object)")
    else:
        for p_req in pump_schema["required"]:
            if p_req not in pump:
                errors.append(f"Во вложенном блоке 'pump' отсутствует поле '{p_req}'")
        if "model" in pump and (not isinstance(pump["model"], str) or not pump["model"].strip()):
            errors.append("Поле 'pump.model' должно быть непустой строкой")
        if "power_kw" in pump:
            p_rules = pump_schema["properties"]["power_kw"]
            pw = pump["power_kw"]
            if not isinstance(pw, (int, float)) or isinstance(pw, bool):
                errors.append("Поле 'pump.power_kw' должно быть числом")
            elif not (p_rules["minimum"] <= float(pw) <= p_rules["maximum"]):
                errors.append(
                    f"Мощность pump.power_kw={pw} вне границ "
                    f"[{p_rules['minimum']}; {p_rules['maximum']}]"
                )

    return len(errors) == 0, errors

if __name__ == "__main__":
    schema_doc = load_json_file("schema.json")
    valid_data = load_json_file("data.json")

    print("=" * 64)
    print("ЗАПУСК ПРОВЕРКИ КОНТРАКТА ДАННЫХ ПО ФАЙЛУ schema.json (Вариант А)")
    print("=" * 64)

    # Сценарий 1: Проверка нашего эталонного файла data.json
    ok1, errs1 = validate_by_schema(valid_data, schema_doc)
    print(f"\n[Сценарий 1] Эталонный файл data.json -> "
          f"{'УСПЕШНО (VALID)' if ok1 else 'ОШИБКА'}")

    # Сценарий 2: Выход за физические границы (глубина -100 м и обводнённость 145%)
    bad_limits = copy.deepcopy(valid_data)
    bad_limits["depth_m"] = -100
    bad_limits["w_pct"] = 145.0
    ok2, errs2 = validate_by_schema(bad_limits, schema_doc)
    print(f"\n[Сценарий 2] Нарушение границ (depth=-100, w=145) -> "
          f"{'УСПЕШНО' if ok2 else 'ОТКЛОНЕНО'}")
    for e in errs2:
        print(f"  x {e}")

    # Сценарий 3: Потеря обязательного поля well_id
    missing_key = copy.deepcopy(valid_data)
    del missing_key["well_id"]
    ok3, errs3 = validate_by_schema(missing_key, schema_doc)
    print(f"\n[Сценарий 3] Удалено обязательное поле 'well_id' -> "
          f"{'УСПЕШНО' if ok3 else 'ОТКЛОНЕНО'}")
    for e in errs3:
        print(f"  x {e}")

    # Сценарий 4: Ошибка типа во вложенном объекте pump (текст вместо числа)
    bad_type = copy.deepcopy(valid_data)
    bad_type["pump"]["power_kw"] = "сто пятнадцать"
    ok4, errs4 = validate_by_schema(bad_type, schema_doc)
    print(f"\n[Сценарий 4] Текст вместо числа в pump.power_kw -> "
          f"{'УСПЕШНО' if ok4 else 'ОТКЛОНЕНО'}")
    for e in errs4:
        print(f"  x {e}")

    # Сценарий 5 (Челлендж № 2): проверка 'диверсии' напарника в broken_data.json
    try:
        broken = load_json_file("broken_data.json")
    except FileNotFoundError:
        print(f"\n[Сценарий 5] Файл broken_data.json не найден — "
              f"создайте его и запустите validator.py ещё раз")
    else:
        ok5, errs5 = validate_by_schema(broken, schema_doc)
        print(f"\n[Сценарий 5] 'Диверсия напарника' broken_data.json -> "
              f"{'УСПЕШНО' if ok5 else 'ОТКЛОНЕНО'}")
        for e in errs5:
            print(f"  x {e}")