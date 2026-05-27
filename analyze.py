import json
import sys
import os
import rnabridge
from rnabridge import HelicesBuilder, GeometryCalculator, Utils
from config import MAX_BEND_ANGLE, JUNCTION_MAX_DIST

def get_motif_sort_key(m):
    """
    Returns a sorting key for motifs based on the first nucleotide position.
    """
    d = m["data"]
    strands = d.get("strands") or [d.get("strand")]
    if not strands or not strands[0]: return 0
    return Utils.to_int(strands[0].get("first")) or 0

def stems_match_strict(s1, s2):
    """
    Performs a strict comparison between two stems using the serial index of the first nucleotide.
    """
    try: 
        ser1 = s1.get("strand5p", {}).get("first", {}).get("serial")
        ser2 = s2.get("strand5p", {}).get("first", {}).get("serial")
        return ser1 is not None and ser2 is not None and str(ser1) == str(ser2)
    except: return False

def main():
    """
    Main analysis pipeline:
    1. Loads RNA annotation data.
    2. Identifies and classifies structural motifs (SLS).
    3. Groups motifs into super-helices based on stacking and geometry.
    4. Identifies junctions and calculates their extensions.
    """
    if len(sys.argv) < 4:
        print("Usage: python analyze.py <annotator_json> <output_helices_json> <input_cif> [max_angle]")
        sys.exit(1)

    input_json, output_file, cif_path = sys.argv[1], sys.argv[2], sys.argv[3]
    # Use config default if max_angle not provided via CLI
    max_angle_limit = float(sys.argv[4]) if len(sys.argv) > 4 else MAX_BEND_ANGLE

    try:
        with open(input_json, "r", encoding="UTF-8") as f: data = json.load(f)
    except Exception as e:
        print(f"ERROR loading {input_json}: {e}"); sys.exit(1)

    # 1. Indexing data from annotator
    pairs_idx = rnabridge.Core.build_pairs_index(data)
    stacking_idx = rnabridge.Stacking.build_stacking_index(data.get("stackings", []), data)
    stems_end_map, stems_start_map = {}, {}
    for s in data.get("stems", []):
        Utils.enrich_motif_data(s, data) 
        for k in ["strand5p", "strand3p"]:
            if k in s:
                l, f = Utils.to_int(s[k]["last"]), Utils.to_int(s[k]["first"])
                if l: stems_end_map[l] = s
                if f: stems_start_map[f] = s

    all_raw = [{"type": "LOOP", "data": l} for l in data.get("loops", [])] + \
              [{"type": "HAIRPIN", "data": h} for h in data.get("hairpins", [])]
    all_raw.sort(key=get_motif_sort_key)
    sls_motifs = []

    # 2. Motif Analysis (SLS Phase)
    for raw_m in all_raw:
        m_data = raw_m["data"]
        if raw_m["type"] == "LOOP":
            Utils.enrich_motif_data(m_data, data)
            m_type = rnabridge.Core.classify_motif(m_data["strands"])
            if not m_type: continue
            
            sorted_s = sorted(m_data["strands"], key=lambda x: Utils.to_int(x['first']))
            l_start, l_end = Utils.to_int(sorted_s[0]['first']), Utils.to_int(sorted_s[0]['last'])
            if l_start is None or l_end is None: continue

            stem1 = stems_end_map.get(l_start) or stems_end_map.get(l_start - 1)
            stem2 = stems_start_map.get(l_end) or stems_start_map.get(l_end + 1)
            if not (stem1 and stem2): continue

            interactions = rnabridge.Core.find_interactions(m_data["strands"], pairs_idx)
            if "WAY_JUNCTION" in m_type:
                if len(set(s.get("first", {}).get("chain") for s in m_data["strands"])) > 1: continue
                if not GeometryCalculator.validate_junction_compactness(cif_path, m_data["strands"], max_dist=JUNCTION_MAX_DIST): continue

                stems_data = {}
                for i in range(len(m_data["strands"])):
                    curr_end = Utils.to_int(m_data["strands"][i]['last'])
                    next_start = Utils.to_int(m_data["strands"][(i + 1) % len(m_data["strands"])]['first'])
                    st = stems_start_map.get(curr_end) or stems_start_map.get(curr_end + 1) or \
                         stems_end_map.get(next_start) or stems_end_map.get(next_start - 1)
                    stems_data[f"stem_{i+1}"] = {"strand5p": st.get("strand5p", {}), "strand3p": st.get("strand3p", {})} if st else {}

                bend_angles = GeometryCalculator.get_junction_bend_angles(cif_path, stems_data)
                motif_result = { 
                    "meta": { "id": len(sls_motifs) + 1, "type": m_type }, 
                    "location": { "strands": m_data["strands"], "context": stems_data }, 
                    "modules": { 
                        "interactions": { "category": rnabridge.Analysis.categorize_junction_interaction(m_data, interactions), "count": len(interactions), "details": interactions }, 
                        "stacking": rnabridge.Stacking.check_junction_stacking({"location": {"strands": m_data["strands"]}}, stacking_idx), "geometry": {"bend_angles": bend_angles}
                    } 
                }
                Utils.enrich_motif_data(motif_result, data)
                sls_motifs.append(motif_result)
            else:
                category = rnabridge.Analysis.categorize_bulge_interaction(m_data, interactions) if m_type == "BULGE" else rnabridge.Analysis.categorize_interaction(m_data, interactions)
                stacking = rnabridge.Stacking.check_general_coaxiality(m_data, stacking_idx) if m_type == "BULGE" else rnabridge.Stacking.check_internal_coaxiality(m_data, stacking_idx)
                
                u_data = {"strand5p": stem1.get("strand5p", {}), "strand3p": stem1.get("strand3p", {})}
                d_data = {"strand5p": stem2.get("strand5p", {}), "strand3p": stem2.get("strand3p", {})}
                v1 = GeometryCalculator.get_stem_axis_cached(cif_path, u_data, label="tmp_u")
                v2 = GeometryCalculator.get_stem_axis_cached(cif_path, d_data, label="tmp_d")
                
                motif_result = { 
                    "meta": { "id": len(sls_motifs) + 1, "type": m_type }, 
                    "location": { "strands": m_data["strands"], "context": {"upstream": u_data, "downstream": d_data}}, 
                    "modules": { 
                        "interactions": { "category": category, "count": len(interactions), "details": interactions }, 
                        "stacking": stacking, "geometry": {"bend_angle": GeometryCalculator.calculate_bend_angle(v1, v2)}
                    } 
                }
                Utils.enrich_motif_data(motif_result, data)
                sls_motifs.append(motif_result)

        elif raw_m["type"] == "HAIRPIN":
            m_data["strands"] = [m_data["strand"]]
            Utils.enrich_motif_data(m_data, data)
            f, l = Utils.to_int(m_data["strand"]["first"]), Utils.to_int(m_data["strand"]["last"])
            if f is None or l is None: continue
            stem1 = stems_end_map.get(f) or stems_start_map.get(l)
            if stem1:
                interactions = rnabridge.Core.find_interactions(m_data["strands"], pairs_idx)
                u_data = {"strand5p": stem1.get("strand5p", {}), "strand3p": stem1.get("strand3p", {})}
                motif_result = { 
                    "meta": { "id": len(sls_motifs) + 1, "type": "HAIRPIN" }, 
                    "location": { "strands": m_data["strands"], "context": {"upstream": u_data, "downstream": {}}}, 
                    "modules": { 
                        "interactions": { "category": rnabridge.Analysis.categorize_hairpin_interaction(m_data, interactions), "count": len(interactions), "details": interactions }, 
                        "stacking": rnabridge.Stacking.check_hairpin_stacking(m_data, stacking_idx), "geometry": {"bend_angle": None}
                    } 
                }
                Utils.enrich_motif_data(motif_result, data)
                sls_motifs.append(motif_result)

    # 3. Super-Helix Building
    raw_helices = HelicesBuilder.extract_helices(sls_motifs)
    final_helices, h_counter = [], 1

    for rh in raw_helices:
        cur_comps, cur_hist, step = [], [], 1
        for comp in rh["components"]:
            motif = next(m for m in sls_motifs if m["meta"]["id"] == comp["m_id"])
            loc_angle = motif["modules"]["geometry"].get("bend_angle")
            m_type, st_stat = motif["meta"]["type"], motif["modules"]["stacking"]["status"]
            safe_loc = round(loc_angle, 2) if loc_angle is not None else None
            
            if not cur_comps:
                accepted = (m_type == "HAIRPIN" and st_stat == "SKIPPED") or (m_type != "HAIRPIN" and loc_angle is not None and loc_angle < max_angle_limit)
                log = {"step": step, "phase": "INIT", "m_id": [comp["m_id"]], "checks": {"bend_angle": safe_loc, "stacking": st_stat}, "status": "ACCEPTED" if accepted else "REJECTED"}
                if accepted: cur_comps = [comp]; step += 1
                cur_hist.append(log); continue
            
            if m_type == "HAIRPIN":
                if st_stat == "SKIPPED": cur_comps.append(comp); step += 1; status = "ACCEPTED"
                else: 
                    status = "REJECTED_STACKING"; final_helices.append({"components": cur_comps, "history": cur_hist})
                    cur_comps, cur_hist, step = [], [], 1
                cur_hist.append({"step": step, "phase": "EXTENSION", "m_id": [cur_comps[-1]["m_id"] if cur_comps else None, comp["m_id"]], "checks": {"stacking": st_stat}, "status": status}); continue

            if loc_angle is None or loc_angle >= max_angle_limit:
                cur_hist.append({"step": step, "phase": "EXTENSION", "m_id": [cur_comps[-1]["m_id"], comp["m_id"]], "checks": {"bend_angle": safe_loc}, "status": "REJECTED_BEND_ANGLE"})
                final_helices.append({"components": cur_comps, "history": cur_hist})
                cur_comps, cur_hist, step = [], [], 1; continue
            
            first_m = next(m for m in sls_motifs if m["meta"]["id"] == cur_comps[0]["m_id"])
            glob_angle = HelicesBuilder.get_global_angle(cif_path, first_m, motif)
            safe_glob = round(glob_angle, 2) if glob_angle is not None else None
            log = {"step": step, "phase": "EXTENSION", "m_id": [cur_comps[-1]["m_id"], comp["m_id"]], "checks": {"bend_angle": safe_loc, "global_measures": {"angle": safe_glob}}}
            
            if glob_angle is None or glob_angle >= max_angle_limit:
                log["status"] = "REJECTED_GLOBAL_BEND_ANGLE"; cur_hist.append(log)
                final_helices.append({"components": cur_comps, "history": cur_hist}); cur_comps, cur_hist, step = [comp], [], 1
            else:
                log["status"] = "ACCEPTED"; cur_comps.append(comp); step += 1; log["status"] = "ACCEPTED"; cur_hist.append(log)

        if cur_comps: final_helices.append({"components": cur_comps, "history": cur_hist})

    formatted_helices = []
    for h_data in final_helices:
        comps = h_data["components"]
        if not comps: continue 
        first_m, last_m = next(m for m in sls_motifs if m["meta"]["id"] == comps[0]["m_id"]), next(m for m in sls_motifs if m["meta"]["id"] == comps[-1]["m_id"])
        glob_angle = HelicesBuilder.get_global_angle(cif_path, first_m, last_m)
        
        enriched = []
        for c in comps:
            m = next(m for m in sls_motifs if m["meta"]["id"] == c["m_id"])
            new_c = {**c, "metrics": {**c.get("metrics", {}), "bend_angle": m["modules"]["geometry"].get("bend_angle")}, "interactions": m["modules"]["interactions"]["details"], "internal_stem": m["location"]["context"]["downstream"]}
            enriched.append(new_c)

        formatted_helices.append({
            "h_id": h_counter, "total_nt": Utils.get_helix_unique_nt([next(m for m in sls_motifs if m["meta"]["id"] == c["m_id"]) for c in comps]),
            "strands": {"upstream": first_m["location"]["context"]["upstream"], "downstream": last_m["location"]["context"]["downstream"]},
            "components": enriched, "global_measures": {"angle": round(glob_angle, 2) if glob_angle is not None else None, "between": [comps[0]["m_id"], comps[-1]["m_id"]]},
            "history_log": h_data["history"]
        }); h_counter += 1

    # 4. Junctions and Extensions
    junctions_output = []
    for m in [mot for mot in sls_motifs if "WAY_JUNCTION" in mot["meta"]["type"]]:
        cp, ba = m["modules"]["stacking"].get("coaxial_pairs", []), m["modules"]["geometry"].get("bend_angles", {})
        if any(ba.get(f"stem_{p[0].split('_')[-1]}_{p[1].split('_')[-1]}") is not None and ba[f"stem_{p[0].split('_')[-1]}_{p[1].split('_')[-1]}"] <= max_angle_limit for p in cp):
            junctions_output.append({"j_id": len(junctions_output) + 1, "total_nt": Utils.get_helix_unique_nt([m]), "location": m["location"]["strands"], "context": m["location"]["context"], "modules": m["modules"]})

    for junc in junctions_output:
        junc["extended_helices"] = [h for h in formatted_helices if any(stems_match_strict(js, h["strands"]["upstream"]) or stems_match_strict(js, h["strands"]["downstream"]) for k, js in junc["context"].items() if "stem" in k)]
        unique_nts = set()
        def add_to_set(s_dict):
            if not s_dict: return
            f, l = s_dict.get("first", {}).get("serial"), s_dict.get("last", {}).get("serial")
            if f is not None and l is not None: unique_nts.update(range(min(int(f), int(l)), max(int(f), int(l)) + 1))
        for s in junc["location"]: add_to_set(s)
        for st in junc["context"].values():
            if isinstance(st, dict): add_to_set(st.get("strand5p")); add_to_set(st.get("strand3p"))
        for eh in junc["extended_helices"]:
            for k in ["upstream", "downstream"]: add_to_set(eh["strands"][k].get("strand5p")); add_to_set(eh["strands"][k].get("strand3p"))
            for comp in eh["components"]:
                for loc in comp["location"]: add_to_set(loc)
                add_to_set(comp["internal_stem"].get("strand5p")); add_to_set(comp["internal_stem"].get("strand3p"))
        junc["total_nt"] = len(unique_nts)

    # Ensure output directory exists using absolute path
    abs_output = os.path.abspath(output_file)
    out_dir = os.path.dirname(abs_output)
    
    if not os.path.exists(out_dir):
        print(f"DEBUG: Directory {out_dir} does not exist. Creating...")
        os.makedirs(out_dir, exist_ok=True)
    
    try:
        with open(abs_output, 'w', encoding="UTF-8") as f: 
            json.dump({"helices": formatted_helices, "junctions": junctions_output}, f, indent=4)
    except Exception as e:
        print(f"ERROR: Could not save result to {abs_output}: {e}")
        sys.exit(1)
        
    print(f"Finished. Saved {len(formatted_helices)} helices and {len(junctions_output)} junctions.")

if __name__ == "__main__":
    main()
