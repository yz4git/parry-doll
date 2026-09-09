from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V28' in s:
    print('Blender heroine generator already carries REFERENCE_V28')
    raise SystemExit(0)
if '# REFERENCE_V27' not in s:
    raise SystemExit('REFERENCE_V27 generator required before v2.8')
s=s.replace('# REFERENCE_V27: asymmetric fringe, clean forehead and layered-volume ponytail.','# REFERENCE_V27: asymmetric fringe, clean forehead and layered-volume ponytail.\n# REFERENCE_V28: low-specular black hair and staggered fringe roots.',1)

# Hair should read dark brown/black even under the model-viewer key light, never metallic silver.
s=s.replace("HAIR=material('Hair',(0.010,0.009,0.013),.02,.40)","HAIR=material('Hair',(0.007,0.006,0.010),0.0,.52)",1)
s=s.replace("HAIR_HI=material('Hair Highlight',(0.040,0.030,0.040),.02,.34)","HAIR_HI=material('Hair Highlight',(0.026,0.020,0.030),0.0,.46)",1)
needle="HAIR_HI=material('Hair Highlight',(0.026,0.020,0.030),0.0,.46)\n"
insert=needle+"""# Reduce Principled specular so dark hair does not blow out to a silver ribbon under bright sky lighting.
for _hair_mat,_spec in ((HAIR,.14),(HAIR_HI,.18)):
 _bsdf=_hair_mat.node_tree.nodes.get('Principled BSDF')
 if _bsdf:
  _ior=_bsdf.inputs.get('Specular IOR Level')
  _old=_bsdf.inputs.get('Specular')
  if _ior:_ior.default_value=_spec
  elif _old:_old.default_value=_spec
"""
if needle not in s: raise SystemExit('hair material anchor not found')
s=s.replace(needle,insert,1)

# Stagger major bang roots vertically and narrow their root widths so they cannot merge into a horizontal forehead bar.
a=s.index('# Asymmetric five-lock fringe:')
b=s.index('# Longer side fringe frames',a)
fringe="""# Asymmetric five-lock fringe with staggered roots; no continuous root band across the forehead.
bang_z=face_z+.019
fringe_data=[
 (-.118,-.100,-.095,.030,.054,.132),
 (-.072,-.056,-.046,.050,.050,.124),
 (-.018,-.008,-.004,-.012,.043,.141),
 (.036,.046,.040,.040,.048,.128),
 (.092,.102,.100,.052,.053,.136)
]
for i,(rootx,midx,tipx,tipy,w,rooty) in enumerate(fringe_data):
 add_ribbon(HEAD,f'FringeMajorV28_{i}',[(rootx,rooty,head_d*.02),(midx,rooty-.016,head_d*.28),(tipx,.086,face_z*.75),(tipx*.98,tipy,bang_z)],[w*.48,w,w*.70,w*.16],.0038,HAIR_HI if i in(1,3) else HAIR)
# Irregular wisps cross the major locks at different heights, producing a soft broken lower edge.
for i,(sx,tx,ty,sy) in enumerate(((-.104,-.088,.042,.116),(-.058,-.038,.025,.108),(.004,.010,.012,.121),(.054,.070,.044,.110),(.110,.120,.034,.118))):
 add_ribbon(HEAD,f'FringeWispV28_{i}',[(sx,sy,head_d*.30),((sx+tx)*.5,sy-.025,face_z*.70),(tx,ty,bang_z+.001)],[.018,.013,.0035],.0025,HAIR_HI if i in(0,4) else HAIR)
# Narrow crown flows bridge scalp to the staggered roots without forming a visible rim.
for i,(lane,sy) in enumerate(((-.28,.143),(-.13,.136),(.015,.146),(.16,.138),(.30,.142))):
 add_ribbon(HEAD,f'CrownFlowV28_{i}',[(lane*head_w,sy,-head_d*.23),(lane*head_w*.95,sy-.009,-head_d*.04),(lane*head_w*.88,sy-.020,head_d*.15),(lane*head_w*.80,sy-.032,face_z*.42)],[.019,.023,.019,.0065],.0024,HAIR_HI if i in(1,3) else HAIR)
add_ribbon(HEAD,'TempleWispV28L',[(-.120,.084,bang_z),(-.132,.046,bang_z),(-.138,-.010,bang_z-.004)],[.016,.010,.0035],.0025,HAIR)
add_ribbon(HEAD,'TempleWispV28R',[(.120,.084,bang_z),(.132,.046,bang_z),(.138,-.010,bang_z-.004)],[.016,.010,.0035],.0025,HAIR)
"""
s=s[:a]+fringe+s[b:]

# Slightly stagger pony roots so the upper cascade reads as overlapping locks rather than parallel reflective strips.
a=s.index('pony_specs=[')
b=s.index('# Rebuild the cascade with nine visible bundles plus three darker under-layers.') if '# Rebuild the cascade with nine visible bundles plus three darker under-layers.' in s else -1
# The comment is before pony_specs in the generated source, so locate the end from the limb anchor instead.
b=s.index('# === LIMBS ===',a)
pony=s[a:b]
pony=pony.replace("for i,(rx,mx,ex,endy,w,zoff) in enumerate(pony_specs):\n sway=(-1 if i%2==0 else 1)*.016\n add_ribbon(PONY,f'PonyBundleV27_{i}',[(rx,.146,-head_d*.50+zoff),(rx*.92,.020,-head_d*.78+zoff)","for i,(rx,mx,ex,endy,w,zoff) in enumerate(pony_specs):\n sway=(-1 if i%2==0 else 1)*.016\n root_y=.146-(i%3)*.010\n add_ribbon(PONY,f'PonyBundleV28_{i}',[(rx,root_y,-head_d*.50+zoff),(rx*.92,.020-(i%2)*.008,-head_d*.78+zoff)",1)
if "PonyBundleV28" not in pony: raise SystemExit('pony bundle replacement failed')
s=s[:a]+pony+s[b:]

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V28: low-specular black hair and staggered fringe roots')
