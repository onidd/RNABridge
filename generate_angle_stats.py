import os
import json
import glob
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, Optional

# Zakładamy, że config.py jest dostępny w tym samym kontekście lub poprzez PYTHONPATH
from config import OUTPUT_DIR, MAX_BEND_ANGLE

def get_category_label(segment_count_folder: str) -> Optional[str]:
    """
    Mapuje nazwę folderu (segment_count_folder) na uproszczoną etykietę kategorii,
    zgodnie z żądaniem dla kolumn tabeli.
    """
    if "segment-helis" in segment_count_folder:
        try:
            num = int(segment_count_folder.split('-')[0])
            if num == 2:
                return "2seg"
            elif num == 3:
                return "3seg"
            elif num >= 4:
                return "4seg+"
            # Inne 'segment-helis' (np. 1-seg) nie będą pasować do tych kategorii
        except ValueError:
            pass
    elif "way-junctions" in segment_count_folder:
        try:
            num = int(segment_count_folder.split('-')[0])
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
    # Definiowanie przedziałów kątów (np. "0-5°", "5-10°", ..., "45-50°")
    # Zapewniamy, że ostatni przedział to "45-50°" i obejmuje on kąt 50.0
    angle_bins = [f"{i}-{i+5}°" for i in range(0, 45, 5)] + ["45-50°"]

    # Definiowanie kategorii kolumn zgodnie z żądaniem użytkownika
    column_categories = ["2seg", "3seg", "4seg+", "3-way", "4-way", "5-way", "6-way+"]

    # Inicjalizacja tabeli statystyk: stats[etykieta_przedziału][etykieta_kategorii] = liczba
    stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # Iteracja przez wszystkie pliki JSON w katalogu wynikowym
    for filepath in glob.glob(str(result_dir / "**/*.json"), recursive=True):
        if "_varna.json" in filepath:  # Pomijanie plików JSON specyficznych dla VARNA
            continue

        try:
            with open(filepath, "r", encoding="UTF-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Błąd podczas ładowania pliku {filepath}: {e}")
            continue

        # Przetwarzanie Helis
        for helix in data.get("helices", []):
            angle = helix.get("global_bend_angle")
            folder = helix.get("segment_count_folder")
            
            if angle is None or folder is None:
                continue
            
            category_label = get_category_label(folder)
            if category_label not in column_categories:  # Liczymy tylko dla żądanych kategorii
                continue
            
            # Określenie przedziału kątów
            # min(int(angle // 5) * 5, 45) zapewnia, że kąt 50.0 spada do przedziału 45-50.
            bin_start = min(int(angle // 5) * 5, 45) 
            bin_label = f"{bin_start}-{bin_start+5}°"

            stats[bin_label][category_label] += 1

        # Przetwarzanie Złącz
        for junction in data.get("junctions", []):
            angle = junction.get("global_bend_angle")
            folder = junction.get("segment_count_folder")
            
            if angle is None or folder is None:
                continue

            category_label = get_category_label(folder)
            if category_label not in column_categories:  # Liczymy tylko dla żądanych kategorii
                continue
            
            # Określenie przedziału kątów
            bin_start = min(int(angle // 5) * 5, 45)
            bin_label = f"{bin_start}-{bin_start+5}°"

            stats[bin_label][category_label] += 1

    # Przygotowanie do wyświetlenia danych
    # Upewnienie się, że wszystkie przedziały i kategorie są obecne, nawet jeśli liczniki wynoszą 0
    full_table: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for bin_label in angle_bins:
        for category_label in column_categories:
            full_table[bin_label][category_label] = stats[bin_label][category_label]

    # Obliczanie sum
    row_totals: Dict[str, int] = defaultdict(int)
    col_totals: Dict[str, int] = defaultdict(int)
    grand_total = 0

    for bin_label in angle_bins:
        for category_label in column_categories:
            count = full_table[bin_label][category_label]
            row_totals[bin_label] += count
            col_totals[category_label] += count
            grand_total += count

    # Wypisywanie tabeli w formacie przyjaznym dla LaTeX
    print("\\begin{tabular}{|l|" + "|".join(["r"] * len(column_categories)) + "|r|}")
    print("\\hline")
    print("Kąt / Typ & " + " & ".join(column_categories) + " & TOTAL \\\\")
    print("\\hline")

    for bin_label in angle_bins:
        row_values = [str(full_table[bin_label][cat]) for cat in column_categories]
        print(f"{bin_label} & " + " & ".join(row_values) + f" & {row_totals[bin_label]} \\\\")
    
    print("\\hline")
    col_total_values = [str(col_totals[cat]) for cat in column_categories]
    print("TOTAL & " + " & ".join(col_total_values) + f" & {grand_total} \\\\")
    print("\\hline")
    print("\\end{tabular}")

if __name__ == "__main__":
    generate_angle_distribution_table(OUTPUT_DIR, MAX_BEND_ANGLE)
