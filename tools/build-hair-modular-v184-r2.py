"""Robust entry point for v18.4 modular hair.

Blender may rename appended datablocks when the shipping scene already contains a historical object with
the same display name.  Keep canonical dictionary keys from the requested donor names instead of using
post-append object.name for identity.  Geometry and face-lock behavior are delegated unchanged to v18.4.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import bpy

BASE = Path(__file__).with_name("build-hair-modular-v184.py")
spec = importlib.util.spec_from_file_location("hair_v184_base", BASE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {BASE}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def append_overscore_stable(path):
    wanted = ["Curtain Bangs", "High Ponytail"]
    with bpy.data.libraries.load(str(Path(path).resolve()), link=False) as (src, dst):
        missing = [name for name in wanted if name not in src.objects]
        if missing:
            raise RuntimeError("OverScore exact hair objects missing: " + ", ".join(missing))
        dst.objects = wanted
    loaded = [o for o in dst.objects if o]
    if len(loaded) != len(wanted):
        raise RuntimeError(f"OverScore append count mismatch: wanted={wanted!r}, loaded={[o.name for o in loaded]!r}")
    result = {}
    for expected, obj in zip(wanted, loaded):
        if obj.type != "MESH":
            raise RuntimeError(f"OverScore {expected} loaded as {obj.type}, not MESH")
        if not obj.users_collection:
            bpy.context.scene.collection.objects.link(obj)
        else:
            try:
                bpy.context.scene.collection.objects.link(obj)
            except RuntimeError:
                pass
        mod.apply_modifiers(obj)
        result[expected] = obj
        print("V184_OVERSCORE_MAP", expected, "->", obj.name)
    return result


mod.append_overscore = append_overscore_stable

if __name__ == "__main__":
    mod.main()
