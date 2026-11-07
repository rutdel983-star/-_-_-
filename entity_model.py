"Этап 1 (Вариант А): Моделирование карточки скважины, сохранение и чтение JSON."
import json
from typing import Any

# ===== ИНДИВИДУАЛЬНЫЕ ЧИСЛА (Раздел 4.1 методички) =====
N = 13 # ПОДСТАВЬТЕ СВОЮ СУММУ: N = N1 + N2 (номера студентов пары по журналу)

WELL_ID = f"W-{100 + N}"                      # код скважины
DEPTH_M = 1500 + 50 * (N % 40)                # глубина скважины, м (int)
Q_LIQ = 45.0 + 3.5 * (N % 30)                 # дебит жидкости, м3/сут (float)
W_PCT = 12.0 + 2.0 * (N % 35)                 # обводнённость, % (float)
POWER_KW = 40.0 + 5.0 * (N % 20)              # мощность насоса ЭЦН, кВт (float)

def build_well_passport() -> dict[str, Any]:
    """Создаёт словарь паспорта скважины с индивидуальными данными пары."""
    return {
        "well_id": WELL_ID,
        "depth_m": DEPTH_M,
        "q_liq": Q_LIQ,
        "w_pct": W_PCT,
        "is_active": True,
        # Челлендж № 1: новое поле по просьбе заказчика
        "field_name": "Приобское",
        "pump": {
            "model": "ЭЦН5-80-1800",
            "power_kw": POWER_KW,
        },
    }

def save_to_json(data: dict[str, Any], filename: str = "data.json") -> None:
    "Сериализует словарь Python в текстовый файл формата JSON."
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_from_json(filename: str = "data.json") -> dict[str, Any]:
    "Десериализует (читает) JSON-файл с диска обратно в словарь Python"
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

def print_passport_summary(passport: dict[str, Any]) -> None:
    "Выводит сводку по прочитанному паспорту и считает дебит чистой нефти"
    q_oil = passport["q_liq"] * (1.0 - passport["w_pct"] / 100.0)
    pump_info = passport["pump"]
    print("=" * 56)
    print(f"ПАСПОРТ СКВАЖИНЫ ИЗ JSON: {passport['well_id']}")
    print("=" * 56)
    print(f"Месторождение:  {passport['field_name']}")
    print(f"Глубина:        {passport['depth_m']} м")
    print(f"Дебит жидкости: {passport['q_liq']:.2f} м3/сут"
          f"(обводнённость {passport['w_pct']:.1f}%)")
    print(f"Расчёт чистой нефти: {q_oil:.2f} м3/сут")
    print(f"Насосная установка: {pump_info['model']} (мощность {pump_info['power_kw']} кВт)")
    print("=" * 56)

if __name__ == "__main__":
    # 1. Формируем словарь в памяти Python
    my_passport = build_well_passport()

    # 2. Сохраняем его в файл data.json (сериализация)
    save_to_json(my_passport, "data.json")
    print("[OK] Файл 'data.json' успешно записан на диск!")

    # 3. Читаем файл обратно с диска (десериализация)
    loaded_passport = load_from_json("data.json")
    assert loaded_passport == my_passport, "Ошибка: прочитанный словарь не совпадает с исходным!"
    print("[OK] Обратное чтение через json.load() прошло без потерь!")

    print_passport_summary(loaded_passport)