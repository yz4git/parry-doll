"""Safe entrypoint for Hair Donor v18.0.

The first dry run proved the external High Ponytail import/fitting works, but also exposed that broad
substring matching such as `cap` can mistake body meshes (ToeCap) for hair. This wrapper narrows the
classification before delegating to the v18.0 Blender authoring script.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tools/build-hair-donor-v180.py"

spec = importlib.util.spec_from_file_location("hair_donor_v180_base", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load v18.0 hair builder")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

# Hair-only identifiers. Deliberately excludes generic words such as `cap` and `rear`, which are
# also used by footwear/costume meshes in the shipping character.
HAIR_NAME_TOKENS = (
    "hair", "fringe", "bang", "crown", "temporal", "temple", "ponytail", "pony",
    "wisp", "nape", "strand", "cascade", "profileeyeframe",
)
HAIR_EXACTISH_TOKENS = (
    "keyartbang", "herocrown", "heropony", "ponymass", "ponyfan", "ponyfoundation",
    "ponywing", "ponyrootband", "hairtiev", "hairtopcap", "hairrearshell", "temporalunder",
    "referencewisp", "profileswisp", "profilewisp", "templesweep", "templeribbon",
    "templefine", "templelayer", "crownlayer", "fringesurface", "fringefine",
    "eyerevealfringe", "earfrontwisp", "profilehairornament",
)
FACE_PREFIXES = (
    "headshell", "bl_eyelid", "eyelight", "iris", "pupil", "sclera", "outerlash",
    "upperlash", "lowerlid", "profilelash", "wrappedcanthuslash", "eyewetline",
    "innercanthus", "upperskinrim", "lowerskinrim", "brow", "beautymark", "upperlip",
    "lowerlip", "mouth", "nose", "earantihelix", "earconcha", "earhelix", "earlobefold",
    "eartragus", "earring", "davidonizaki",
)


def under_head(obj):
    cur = obj
    while cur:
        if cur.name == "BL_HEAD":
            return True
        cur = cur.parent
    return False


def material_is_hair(obj):
    mats = [m.name.lower() for m in getattr(obj.data, "materials", []) if m]
    return bool(mats) and all("hair" in name for name in mats)


def style_hint(obj):
    if obj.type != "MESH":
        return False
    n = obj.name.lower()
    # Facial lashes/brows can legitimately use the same dark material as hair; name wins first.
    if any(n.startswith(prefix) for prefix in FACE_PREFIXES):
        return False
    if any(token in n for token in HAIR_EXACTISH_TOKENS):
        return True
    if any(token in n for token in HAIR_NAME_TOKENS):
        return True
    return under_head(obj) and material_is_hair(obj)


def safe_face_locked(obj):
    # Strong invariant: every mesh under the head hierarchy is protected unless it is positively
    # identified as hairstyle geometry. This also protects generically named ear/eye helper meshes.
    return obj.type == "MESH" and under_head(obj) and not style_hint(obj)


def safe_old_style_hair(obj):
    return style_hint(obj)


base.is_face_locked = safe_face_locked
base.is_old_style_hair = safe_old_style_hair
base.STYLE_NAME_TOKENS = HAIR_NAME_TOKENS
base.main()
