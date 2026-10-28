def open_file(file_name):
    points = []
    section_id = 0
    is_pair = False
    with open(file_name, "r", encoding="utf-8-sig") as file:
        for line in file:
            clean_line = line.strip()
            parts = clean_line.split(";")
            if len(parts) < 3 or parts[1] == "" or parts[2] == "":
                continue
            name = parts[0].lower()
            x_coord = float(parts[1].replace(",", "."))
            y_coord = float(parts[2].replace(",", "."))
            points.append({"name": name.replace("g", ""), "coord_X": x_coord, "coord_Y": y_coord, "section": section_id})
            if "g" in parts[3].lower():
                if is_pair == False:
                    is_pair = True
                else:
                    section_id += 1
                    is_pair = False
    for point in points:
        if point["section"] == section_id:
            point["section"] = "Free"
    return points