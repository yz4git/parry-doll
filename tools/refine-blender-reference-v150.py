from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V150' in s:
    print('Blender heroine generator already carries REFERENCE_V150')
    raise SystemExit(0)
if '# REFERENCE_V149' not in s:
    raise SystemExit('REFERENCE_V149 generator required before v13.20')

marker="# REFERENCE_V149: lower profile refinement increases the rear-side lift while preserving the accepted front silhouette."
if marker not in s:
    raise SystemExit('v13.20 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V150: facial-plane refinement deepens the orbital bowl, strengthens the zygomatic plane and adds restrained alar, mouth-corner and jaw-angle breaks for a more premium three-quarter read without changing frontal proportions.",1)

# Strengthen only the portrait-head surface planes. These are shallow depth offsets, not width edits.
for old,new in (
    ("z-=fm*.0068*math.exp(-((x-temple_x)/(head_w*.105))**2-((yy-.055)/.050)**2)",
     "z-=fm*.0075*math.exp(-((x-temple_x)/(head_w*.105))**2-((yy-.055)/.050)**2)"),
    ("z+=fm*.0125*math.exp(-((x-cheek_x)/(head_w*.112))**2-((yy+.010)/.045)**2)",
     "z+=fm*.0139*math.exp(-((x-cheek_x)/(head_w*.110))**2-((yy+.010)/.043)**2)"),
    ("z-=fm*.0165*math.exp(-((x-eye_x)/(head_w*.124))**2-((yy-.030)/.027)**2)",
     "z-=fm*.0180*math.exp(-((x-eye_x)/(head_w*.123))**2-((yy-.030)/.027)**2)"),
    ("z+=fm*.0048*math.exp(-((x-eye_x)/(head_w*.120))**2-((yy-.068)/.024)**2)",
     "z+=fm*.00535*math.exp(-((x-eye_x)/(head_w*.118))**2-((yy-.068)/.023)**2)"),
    ("z+=fm*.0030*math.exp(-((x-eye_x)/(head_w*.115))**2-((yy+.002)/.020)**2)",
     "z+=fm*.00345*math.exp(-((x-eye_x)/(head_w*.113))**2-((yy+.002)/.019)**2)"),
    ("z-=fm*.0048*math.exp(-((x-side*head_w*.275)/(head_w*.095))**2-((yy+.052)/.038)**2)",
     "z-=fm*.00555*math.exp(-((x-side*head_w*.275)/(head_w*.093))**2-((yy+.052)/.037)**2)"),
    ("z-=fm*.0022*math.exp(-((x-side*head_w*.105)/(head_w*.070))**2-((yy+.065)/.028)**2)",
     "z-=fm*.00275*math.exp(-((x-side*head_w*.105)/(head_w*.067))**2-((yy+.065)/.027)**2)"),
):
    if old not in s:
        raise SystemExit('v13.20 facial-plane anchor missing: '+old[:42])
    s=s.replace(old,new,1)

# Add three very shallow local breaks per side: alar crease, mouth-corner hollow and jaw-angle taper.
anchor="     z-=fm*.00275*math.exp(-((x-side*head_w*.105)/(head_w*.067))**2-((yy+.065)/.027)**2)\n"
if anchor not in s:
    raise SystemExit('v13.20 local plane insertion anchor missing')
insert=(
"     # v13.20 local plane breaks: subtle enough to read in 3/4 lighting without becoming carved lines.\n"
"     z-=fm*.00120*math.exp(-((x-side*head_w*.072)/(head_w*.043))**2-((yy+.055)/.014)**2)\n"
"     z-=fm*.00095*math.exp(-((x-side*head_w*.118)/(head_w*.050))**2-((yy+.086)/.018)**2)\n"
"     z-=fm*.00155*math.exp(-((x-side*head_w*.305)/(head_w*.086))**2-((yy+.118)/.027)**2)\n"
)
s=s.replace(anchor,anchor+insert,1)

old="ROOT['character_revision']='v13.19';"
new="ROOT['character_revision']='v13.20';"
if old not in s:
    raise SystemExit('v13.20 revision anchor missing')
s=s.replace(old,new,1)
s=s.replace("HEAD_ASSET['reference_profile_silhouette']='v13.19'","HEAD_ASSET['reference_profile_silhouette']='v13.20'",1)
needle="HEAD_ASSET['continuous_profile_revision']='v13.17';"
if needle in s:
    s=s.replace(needle,needle+"HEAD_ASSET['facial_plane_revision']='v13.20';",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V150: orbital, zygomatic, alar, mouth-corner and jaw-angle facial plane refinement')
