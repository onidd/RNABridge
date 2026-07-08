import os
import json
import glob
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, Optional

# Zakładamy, że config.py jest dostępny w tym samym kontekście lub poprzez PYTHONPATH
from config import OUTPUT_DIR, MAX_BEND_ANGLE

def get_category_label(folder_name: str) -> Optional[str]:
    """
    Mapuje nazwę folderu na uproszczoną etykietę kategorii,
    zgodnie z żądaniem dla kolumn tabeli.
    """
    if "segment-helis" in folder_name:
        try:
            num = int(folder_name.split('-')[0])
            if num == 2:
                return "2seg"
            elif num == 3:
                return "3seg"
            elif num >= 4:
                return "4seg+"
        except ValueError:
            pass
    elif "way-junctions" in folder_name:
        try:
            num = int(folder_name.split('-')[0])
            if num == 3:
                return "3-way"
            elif num == 4:
                return "4-way"
            elif num == 5:
                return "5-way"
            elif num >= 6:
                return "6-way+"
        except ValueError:
            pass
    return None

def generate_angle_distribution_table(result_dir: Path, max_angle_limit: float):
    """
    Generuje tabelę rozkładów kątów dla helis i złącz z plików JSON
    znajdujących się w katalogu wynikowym.
    """
    angle_bins = [f"{i}-{i+5}°" for i in range(0, 45, 5)] + ["45-50°"]
    column_categories = ["2seg", "3seg", "4seg+", "3-way", "4-way", "5-way", "6-way+"]
    stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # Iteracja przez wszystkie pliki JSON w katalogu wynikowym, rekursywnie
    for filepath in glob.glob(str(result_dir / "**/*.json"), recursive=True):
        if "_varna.json" in filepath:
            continue

        try:
            with open(filepath, "r", encoding="UTF-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Błąd podczas ładowania pliku {filepath}: {e}")
            continue

        # Pobieranie nazwy folderu z filepath
        # np. result/2-segment-helis/pdb_h1_2-segment.json -> "2-segment-helis"
        folder_name = Path(filepath).parent.name
        
        # Przetwarzanie Helis
        for helix in data.get("helices", []):
            angle = helix.get("global_measures", {}).get("angle")
            
            if angle is None:
                continue
            
            category_label = get_category_label(folder_name)
            if category_label not in column_categories:
                continue
            
            bin_start = min(int(angle // 5) * 5, 45) 
            bin_label = f"{bin_start}-{bin_start+5}°"

            stats[bin_label][category_label] += 1

        # Przetwarzanie Złącz
        for junction in data.get("junctions", []):
            bend_angles = junction.get("modules", {}).get("geometry", {}).get("bend_angles", {})
            valid_angles = [v for v in bend_angles.values() if v is not None]
            angle = min(valid_angles) if valid_angles else None
            
            if angle is None:
                continue

            category_label = get_category_label(folder_name)
            if category_label not in column_categories:
                continue
            
            bin_start = min(int(angle // 5) * 5, 45)
            bin_label = f"{bin_start}-{bin_start+5}°"

            stats[bin_label][category_label] += 1

    full_table: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for bin_label in angle_bins:
        for category_label in column_categories:
            full_table[bin_label][category_label] = stats[bin_label][category_label]

    row_totals: Dict[str, int] = defaultdict(int)
    col_totals: Dict[str, int] = defaultdict(int)
    grand_total = 0

    for bin_label in angle_bins:
        for category_label in column_categories:
            count = full_table[bin_label][category_label]
            row_totals[bin_label] += count
            col_totals[category_label] += count
            grand_total += count

    # Wypisywanie tabeli w formacie LaTeX z booktabs
    print("\\usepackage{booktabs}")
    print("\\begin{tabular}{l" + "".join(["r"] * len(column_categories)) + "r}")
    print("\\toprule")
    print("Kąt / Typ & " + " & ".join(column_categories) + " & TOTAL \\\\")
    print("\\midrule")

    for bin_label in angle_bins:
        row_values = [str(full_table[bin_label][cat]) for cat in column_categories]
        print(f"{bin_label} & " + " & ".join(row_values) + f" & {row_totals[bin_label]} \\\\")
    
    print("\\midrule")
    col_total_values = [str(col_totals[cat]) for cat in column_categories]
    print("TOTAL & " + " & ".join(col_total_values) + f" & {grand_total} \\\\")
    print("\\bottomrule")
    print("\\end{tabular}")

if __name__ == "__main__":
    generate_angle_distribution_table(OUTPUT_DIR, MAX_BEND_ANGLE)
