import math
import time
import tkinter as tk
from tkinter import filedialog

import slint

from openFile import open_file
from surveyMath import (
    square_error_free_section, calculate_main_sections_error,
    calculate_main_giro_error, calculate_main_angle_error,
    calculate_shaft_height_error, calculate_underground_leveling_error
)

const_m_betta = 10
const_m_alpha = 30
const_rad = 206265

# Hidden root for native Tk file dialogs (never shown).
_tk_root = tk.Tk()
_tk_root.withdraw()


def _process_traverse(file_path, coord_K):
    """Run the geodetic pipeline for a single traverse file. Returns
    (m_sec, m_free, m_giro, m_line, line_list)."""
    points = open_file(file_path)
    main_section_list = sorted(list(set(
        p["section"] for p in points
        if p.get("section") is not None and p.get("section") != "Free" and p.get("section") != 0
    )))
    m_sec = calculate_main_sections_error(points, main_section_list, const_m_betta, const_rad)
    m_free = square_error_free_section(points, const_m_betta, const_rad, coord_K)
    m_giro = calculate_main_giro_error(points, main_section_list, const_m_alpha, const_rad, coord_K)
    m_line, line_list = calculate_main_angle_error(points, const_rad)
    return m_sec, m_free, m_giro, m_line, line_list


def run_calculation(coord_K, traverse1_path, traverse2_path, dual_shaft, depth_single, depth_1, depth_2):
    """Unified surveyMath pipeline. Returns (M_ozh, Mz_ozh, execution_time)."""
    start_time = time.perf_counter()

    m_sec_1, m_free_1, m_giro_1, m_line_1, line_list_1 = _process_traverse(traverse1_path, coord_K)
    m_sec_2, m_free_2, m_giro_2, m_line_2, line_list_2 = _process_traverse(traverse2_path, coord_K)

    sum_squares = (
        m_sec_1 + m_free_1 + m_giro_1 + m_line_1 +
        m_sec_2 + m_free_2 + m_giro_2 + m_line_2
    )
    M_ozh = 3 * math.sqrt(sum_squares)

    if dual_shaft:
        m2_shaft = calculate_shaft_height_error(depth_1) + calculate_shaft_height_error(depth_2)
    else:
        m2_shaft = calculate_shaft_height_error(depth_single)

    m2_way_1 = calculate_underground_leveling_error(line_list_1)
    m2_way_2 = calculate_underground_leveling_error(line_list_2)

    sum_squares_z = m2_shaft + m2_way_1 + m2_way_2
    Mz_ozh = 3 * math.sqrt(sum_squares_z)

    execution_time = time.perf_counter() - start_time
    return M_ozh, Mz_ozh, execution_time


class App(slint.loader.ui.MainWindow):

    @slint.callback
    def select_traverse1_file(self):
        path = filedialog.askopenfilename(
            title="Select Traverse 1 CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.traverse1_path = path

    @slint.callback
    def select_traverse2_file(self):
        path = filedialog.askopenfilename(
            title="Select Traverse 2 CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.traverse2_path = path

    @slint.callback
    def execute_calculation(self):
        try:
            coord_K = {
                "name": "K",
                "coord_X": float(self.coord_x),
                "coord_Y": float(self.coord_y),
                "section": "None",
            }

            dual_shaft = self.shaft_mode_index == 1
            depth_single = float(self.shaft_depth) if not dual_shaft else 0.0
            depth_1 = float(self.shaft_depth_1) if dual_shaft else 0.0
            depth_2 = float(self.shaft_depth_2) if dual_shaft else 0.0

            M_ozh, Mz_ozh, execution_time = run_calculation(
                coord_K,
                self.traverse1_path,
                self.traverse2_path,
                dual_shaft,
                depth_single,
                depth_1,
                depth_2,
            )

            self.result_m_ozh = f"{M_ozh:.4f}"
            self.result_mz_ozh = f"{Mz_ozh:.4f}"
            self.result_exec_time = f"{execution_time:.6f}"
            self.status_message = ""
        except FileNotFoundError as exc:
            self.status_message = f"Error: file not found - {exc}"
        except ValueError as exc:
            self.status_message = f"Error: invalid numeric input - {exc}"
        except Exception as exc:
            self.status_message = f"Error: {exc}"


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()

