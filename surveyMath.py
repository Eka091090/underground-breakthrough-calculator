import math
def square_error_free_section(points, const_m_betta, const_rad, coord_K):
    first_free_index = None
    for i, p in enumerate(points):
        if p.get("section") == "Free":
            first_free_index = i
            break

    if first_free_index is None:
        return

    before_free_point = None
    if first_free_index > 0:
        before_free_point = points[first_free_index - 1]

    free_section_points = [p for p in points if p.get("section") == "Free"]

    result_free_section_points = []
    if before_free_point is not None:
        result_free_section_points.append(before_free_point)
    result_free_section_points.extend(free_section_points)

    rY = 0
    sum_rY = 0
    for point in result_free_section_points:
        if point["coord_Y"] > coord_K["coord_Y"]:
            rY = point["coord_Y"] - coord_K["coord_Y"]
            sum_rY += rY

        else:
            rY = coord_K["coord_Y"] - point["coord_Y"]
            sum_rY += rY

    m_error_free_section = (pow(const_m_betta, 2) / (2 * pow(const_rad, 2))) * pow(sum_rY, 2)

    return m_error_free_section

def get_section(points, section):
    first_index = None
    for i, p in enumerate(points):
        if p.get("section") == section:
            first_index = i
            break

    if first_index is None:
        return

    before_point = None
    if first_index > 0:
        before_point = points[first_index - 1]

    section_points = [p for p in points if p.get("section") == section]

    result_section_points = []
    if before_point is not None:
        result_section_points.append(before_point)
    result_section_points.extend(section_points)

    return result_section_points

def calculate_main_sections_error(points, sections, const_m_betta, const_rad):
    total_sum_rY_sq = 0
    
    for sec_id in sections:
        sec_points = get_section(points, sec_id)
        calculation_points = sec_points[:-1]

        sum_X = sum(p["coord_X"] for p in calculation_points)
        sum_Y = sum(p["coord_Y"] for p in calculation_points)
        giro_centerX = sum_X / len(calculation_points)
        giro_centerY = sum_Y / len(calculation_points)

        sum_rY = 0
        for point in calculation_points:
            if point["coord_Y"] > giro_centerY:
                rY = point["coord_Y"] - giro_centerY
                sum_rY += rY
        
            else:
                rY = giro_centerY - point["coord_Y"]
                sum_rY += rY

        sec_rY_squared = pow(sum_rY, 2) * pow(const_m_betta, 2)

        total_sum_rY_sq += sec_rY_squared


    m_error_section = (1 / pow(const_rad, 2)) * total_sum_rY_sq
    return m_error_section

def calculate_main_giro_error(points, sections, const_m_alpha, const_rad, coord_K):
    giro_list = []
    
    for sec_id in sections:
        sec_points = get_section(points, sec_id)
        calculation_points = sec_points[:-1]

        sum_X = sum(p["coord_X"] for p in calculation_points)
        sum_Y = sum(p["coord_Y"] for p in calculation_points)
        giro_centerX = sum_X / len(calculation_points)
        giro_centerY = sum_Y / len(calculation_points)

        giro_list.append((giro_centerX, giro_centerY))

    k_X = coord_K["coord_X"]
    k_Y = coord_K["coord_Y"]
    giro_list.append((k_X, k_Y))

    sum_giro_error = 0
    for i in range(len(giro_list) - 1):
        y1 = giro_list[i][1]
        y2 = giro_list[i+1][1]
        sum_giro_error += pow((y1 - y2), 2) * pow(const_m_alpha, 2)

    giro_error = (1/pow(const_rad, 2)) * sum_giro_error

    return giro_error

def calculate_main_angle_error(points, const_rad):
    line_list = []
    
    for i in range(len(points) - 1):
        p1 = points[i]      
        p2 = points[i + 1]  
        
        dx = p2["coord_X"] - p1["coord_X"]
        dy = p2["coord_Y"] - p1["coord_Y"]
        
        distance = math.sqrt(pow(dx, 2) + pow(dy, 2))
        rumb_rad = math.atan(abs(dy / dx))

        if dx > 0 and dy > 0:
            side = "Northeast"
            alpha = rumb_rad
        elif dx < 0 and dy > 0:
            side = "Southeast"
            alpha = math.pi - rumb_rad
        elif dx < 0 and dy < 0:
            side = "Southwest"
            alpha = math.pi + rumb_rad
        elif dx > 0 and dy < 0:
            side = "Northwest"
            alpha = (2 * math.pi) - rumb_rad

        angle_error = (1/2) * (pow(0.001, 2) * pow(math.cos(alpha), 2))

        
        line_list.append((distance, dx, dy, rumb_rad, side, alpha, angle_error))
    sum_angle_error = sum(item[6] for item in line_list)

    e_center = 0.0015
    n_points = len(points)
    center_error = (2 * pow(e_center, 2) / pow(const_rad, 2)) * n_points
    return sum_angle_error + center_error, line_list

def calculate_shaft_height_error(depth_H):
    m_z_mm = (10 + (0.2 * depth_H)) / 4
    return pow(m_z_mm / 1000, 2)  

def calculate_underground_leveling_error(line_list):
    total_length_meters = sum(item[0] for item in line_list)
    
    L_km = total_length_meters / 1000
    
    m_hp_mm = (20 * math.sqrt(L_km)) / 4
    
    return pow(m_hp_mm / 1000, 2) 