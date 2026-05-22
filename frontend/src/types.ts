export interface SegmentDetail {
  s_id: number;
  type: string;
  size_2d: string;
  size_3d: string;
  bend_angle: number | null;
  stacking: string;
  stacking_path: any[];
  sequence: string;
}

export interface JunctionDetails {
  stacking_status: string;
  coaxial_pairs: any[];
  all_angles: Record<string, number | null>;
  stems?: any;
  components?: any[];
  json_data?: any;
}

export interface Result {
  id: number;
  pdb_id: string;
  molecule?: string;
  organism?: string;
  resolution?: number;
  method?: string;
  total_nt: number;
  global_bend_angle: number | null;
  segment_count_folder: string;
  path_svg: string | null;
  path_cif: string;
  path_pml: string;
  path_json: string;
  type: 'helix' | 'junction';
  details?: {
    db_segments?: SegmentDetail[];
    json_data?: any;
    components?: any[];
    stacking_status?: string;
    coaxial_pairs?: any[];
    all_angles?: Record<string, number | null>;
    stems?: any;
  };
}

export const SEGMENT_TYPES = [
  { label: 'Helices (2 segments)', value: '2-segment-helis' },
  { label: 'Helices (3 segments)', value: '3-segment-helis' },
  { label: 'Helices (4 segments)', value: '4-segment-helis' },
  { label: 'Helices (5 segments)', value: '5-segment-helis' },
  { label: 'Helices (6 segments)', value: '6-segment-helis' },
  { label: '3-way Junctions', value: '3-way-junctions' },
  { label: '4-way Junctions', value: '4-way-junctions' },
  { label: '5-way Junctions', value: '5-way-junctions' },
  { label: '6-way Junctions', value: '6-way-junctions' },
  { label: '7-way Junctions', value: '7-way-junctions' },
  { label: 'Other Junctions (8+)', value: '8plus-junctions' },
];

export const API_BASE = import.meta.env.PROD 
  ? window.location.origin 
  : 'http://localhost:8000';
