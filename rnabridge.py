@staticmethod
def get_global_angle(
    cif_path: str, motif_start: Dict, motif_end: Dict
) -> Optional[float]:
    """Calculates the bend angle between the first and last stem of a super-helix."""
    if motif_start == motif_end:
        return 0.0
    # ...
