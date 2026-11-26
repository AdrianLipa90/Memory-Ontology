"""Read-only visual projection of an explicitly supplied TCD affect state.

Presentation boundary only; no affect inference, new semantic registry or transport.
"""
from math import isfinite, fsum
from consciousness_dictionary.rifc import AffectiveField
from consciousness_dictionary.affect_detection import affect_phase36
from consciousness_dictionary.registry import Lexicon

TCD_SOURCE = "5fe9daa5e2b4841e598628aa5a1a7beadb0e70b1"
# Source labels and color names are from Book I. Hex values are UI choices.
PALETTE = (
    ("curiosity", "violet", "#8B5CF6", "CLX2-AFFECT-002", "RELATED_GENERAL"),
    ("fear", "pale blue", "#A8D8F0", "CLX2-AFFECT-006", "EXACT_NAME"),
    ("irritation", "red", "#E44545", "CLX2-AFFECTX-020", "RELATED"),
    ("happiness", "gold", "#E9B83F", "CLX2-AFFECTX-022", "RELATED"),
    ("calm", "green", "#49A66B", "CLX2-AFFECTX-030", "EXACT_NAME"),
    ("sadness", "deep blue", "#254B91", "CLX2-AFFECTX-021", "EXACT_NAME"),
)
FIELD_IDS = ("CLX2-AFFECTX-010", *(f"CLX2-AFFECTX-{i:03d}" for i in range(1,7)),
             "CLX2-AFFECTX-012", "CLX2-AFFECTX-013", "CLX2-AFFECTX-014")

def project_hair(identity: str, field: AffectiveField, intensities: dict,
                 lexicon: Lexicon, *, source_ref: str):
    if not isinstance(identity,str) or not identity.strip():
        raise ValueError("explicit identity required")
    if not isinstance(source_ref,str) or not source_ref.strip():
        raise ValueError("explicit affect source required")
    if not isinstance(field, AffectiveField):
        raise TypeError("imported TCD AffectiveField required")
    values = field.as_tuple()
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(v)
           for v in values) or not (-1 <= values[0] <= 1) or any(not 0 <= v <= 1 for v in values[1:]):
        raise ValueError("outside TCD field domain")
    if not isinstance(intensities,dict) or set(intensities) - {p[0] for p in PALETTE}:
        raise ValueError("unknown book palette label")
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(v) or v < 0
           for v in intensities.values()):
        raise ValueError("invalid explicit intensity")
    # Scale before summing to avoid overflow without discarding raw intensities.
    scale = max(intensities.values(), default=0)
    total = fsum(v/scale for v in intensities.values()) if scale else 0
    strands = []
    for label, color, rgb, term_id, relation in PALETTE:
        term = lexicon.get(term_id)
        w = intensities.get(label,0)
        if w > 0:
            strands.append({"label":label,"colour":color,"rgb":rgb,
                            "intensity":w,"share":(w/scale)/total,
                            "tcd_term_id":term.term_id,"tcd_name":term.canonical_name,
                            "relation":relation})
    return {"identity":identity, "source_ref":source_ref, "tcd_source":TCD_SOURCE,
            "field_term_ids":[lexicon.get(x).term_id for x in FIELD_IDS],
            "field":field, "phase36":affect_phase36(field),
            "intensities":dict(intensities), "strands":tuple(strands),
            "status":"PROJECTED" if strands else "UNSPECIFIED"}
