from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V146' in s:
    print('Blender heroine generator already carries REFERENCE_V146')
    raise SystemExit(0)
if '# REFERENCE_V145' not in s:
    raise SystemExit('REFERENCE_V145 generator required before v13.16')

marker="# REFERENCE_V145: portrait-eye/lip realism pass reduces the front/three-quarter doll-eye vertical aperture and iris dominance, while enlarging only the exact-profile eye aperture and adding restrained lip volume for the supplied elegant side portrait."
if marker not in s:
    raise SystemExit('v13.16 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V146: visible-profile ornament pass moves the previously buried side hair hardware onto the outer hair surface and rebuilds it as a segmented black/silver vertical spine with a crown cap and pony-root bands, matching the supplied reference silhouette.",1)

old="""for _side in (-1,1):
 add_box(HEAD,f'ProfileHairOrnamentV136_{_side}',(_side*.105,.090,-head_d*.365),(.011,.145,.013),SILVER,.0025,rot=(0,0,-_side*.055))
 add_box(HEAD,f'ProfileHairOrnamentTipV136_{_side}',(_side*.106,.016,-head_d*.365),(.016,.026,.016),SILVER,.003)
add_box(HEAD,'HairTieV59',(.014,.138,-head_d*.530),(.072,.017,.027),SILVER,.003)
"""
new="""for _side in (-1,1):
 # Dark backing keeps the ornament readable against bright sky while the silver faces catch highlights.
 add_box(HEAD,f'ProfileHairOrnamentBackV146_{_side}',(_side*.140,.092,-head_d*.350),(.014,.154,.016),BLACK,.0030,rot=(0,0,-_side*.050))
 add_box(HEAD,f'ProfileHairOrnamentTopV146_{_side}',(_side*.141,.159,-head_d*.348),(.026,.034,.022),SILVER,.0040,rot=(0,0,-_side*.050))
 add_box(HEAD,f'ProfileHairOrnamentSegAV146_{_side}',(_side*.142,.126,-head_d*.347),(.011,.041,.019),SILVER,.0024,rot=(0,0,-_side*.050))
 add_box(HEAD,f'ProfileHairOrnamentSegBV146_{_side}',(_side*.143,.083,-head_d*.346),(.011,.036,.018),SILVER,.0024,rot=(0,0,-_side*.050))
 add_box(HEAD,f'ProfileHairOrnamentSegCV146_{_side}',(_side*.144,.045,-head_d*.345),(.010,.030,.017),SILVER,.0022,rot=(0,0,-_side*.050))
 add_box(HEAD,f'ProfileHairOrnamentTipV146_{_side}',(_side*.145,.020,-head_d*.344),(.017,.020,.019),SILVER,.0030,rot=(0,0,-_side*.050))
 # A narrow cyan inset makes the hardware feel integrated with the existing futuristic suit language.
 add_box(HEAD,f'ProfileHairOrnamentInsetV146_{_side}',(_side*.149,.126,-head_d*.340),(.0030,.020,.0065),GLOW,.0010,rot=(0,0,-_side*.050))
 # Side-visible pony root clamps bridge the ornament into the high pony instead of leaving it floating.
 add_box(HEAD,f'PonyRootBandV146_{_side}',(_side*.052,.141,-head_d*.528),(.030,.024,.035),SILVER,.0040,rot=(0,0,-_side*.035))
add_box(HEAD,'HairTieV59',(.014,.138,-head_d*.530),(.072,.017,.027),SILVER,.003)
"""
if old not in s:
    raise SystemExit('v13.16 ornament anchor missing')
s=s.replace(old,new,1)

old="ROOT['character_revision']='v13.15';"
new="ROOT['character_revision']='v13.16';"
if old not in s:
    raise SystemExit('v13.16 revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("HEAD_ASSET['reference_profile_silhouette']='v13.15'","HEAD_ASSET['reference_profile_silhouette']='v13.16'",1)
s=s.replace("HAIR_ASSET['reference_profile_hair_revision']='v13.14'","HAIR_ASSET['reference_profile_hair_revision']='v13.16'",1)
s=s.replace("HAIR_ASSET['metal_ornament_revision']='v13.6'","HAIR_ASSET['metal_ornament_revision']='v13.16'",1)
needle="FACE_ASSET['expression_ready']=True;"
if needle in s:
    s=s.replace(needle,"HAIR_ASSET['profile_ornament_visibility_revision']='v13.16';"+needle,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V146: outward segmented profile hair ornament and pony-root clamps')
