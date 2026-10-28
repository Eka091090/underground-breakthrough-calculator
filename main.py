from openFile import open_file
import time
import math
from surveyMath import (
    square_error_free_section, get_section, calculate_main_sections_error, 
    calculate_main_giro_error, calculate_main_angle_error, 
    calculate_shaft_height_error, calculate_underground_leveling_error
)

start_time = time.perf_counter()

coord_K = {"name": "K", "coord_X": 24120.578, "coord_Y": 12777.635, "section": "None"} 
depth_Р = 900 # Глубина ствола

const_m_betta = 10
const_m_alpha = 30
const_rad = 206265

# --- ХОД №1 ---
points_1 = open_file("test.csv")
main_section_list_1 = sorted(list(set(
    p["section"] for p in points_1
    if p.get("section") is not None and p.get("section") != "Free" and p.get("section") != 0 
)))
m_sec_1 = calculate_main_sections_error(points_1, main_section_list_1, const_m_betta, const_rad)
m_free_1 = square_error_free_section(points_1, const_m_betta, const_rad, coord_K)
m_giro_1 = calculate_main_giro_error(points_1, main_section_list_1, const_m_alpha, const_rad, coord_K)
# Принимаем два значения: ошибку и список линий!
m_line_1, line_list_1 = calculate_main_angle_error(points_1, const_rad)

# --- ХОД №2 ---
points_2 = open_file("kanex.csv")
main_section_list_2 = sorted(list(set(
    p["section"] for p in points_2
    if p.get("section") is not None and p.get("section") != "Free" and p.get("section") != 0 
)))
m_sec_2 = calculate_main_sections_error(points_2, main_section_list_2, const_m_betta, const_rad)
m_free_2 = square_error_free_section(points_2, const_m_betta, const_rad, coord_K)
m_giro_2 = calculate_main_giro_error(points_2, main_section_list_2, const_m_alpha, const_rad, coord_K)
# Принимаем два значения: ошибку и список линий!
m_line_2, line_list_2 = calculate_main_angle_error(points_2, const_rad)

# Плановая ошибка
sum_squares = (
    m_sec_1 + m_free_1 + m_giro_1 + m_line_1 +
    m_sec_2 + m_free_2 + m_giro_2 + m_line_2
)
M_ozh = 3 * math.sqrt(sum_squares)

# --- ВЫСОТНАЯ ОШИБКА ---
m2_shaft_single = calculate_shaft_height_error(depth_Р)

m2_way_1 = calculate_underground_leveling_error(line_list_1)
m2_way_2 = calculate_underground_leveling_error(line_list_2)

sum_squares_z = m2_shaft_single + m2_way_1 + m2_way_2

Mz_ozh = 3 * math.sqrt(sum_squares_z)

end_time = time.perf_counter()
execution_time = end_time - start_time  

print(f"--- ИТОГОВЫЙ РАСЧЕТ СБОЙКИ ВСТРЕЧНЫХ ЗАБОЕВ ---")
print(f"Ожидаемая предельная ошибка схождения в плане Mож: {M_ozh:.4f} м")
print(f"Ожидаемая предельная ошибка схождения по высоте Mz_ож: {Mz_ozh:.4f} м")
print(f"Время выполнения алгоритма (Execution Time): {execution_time:.6f} сек.")
