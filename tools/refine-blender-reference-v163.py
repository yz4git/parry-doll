from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
p=Path(__file__).with_name('make-blender-heroine.py')
face_path=root/'tools'/'heroine-face-rebuild-v140.json'
s=p.read_text(encoding='utf-8')
face=json.loads(face_path.read_text(encoding='utf-8'))

if '# REFERENCE_V163' in s and face.get('revision')=='v14.3':
    print('Blender heroine generator already carries REFERENCE_V163 / v14.3')
    raise SystemExit(0)
if '# REFERENCE_V162' not in s:
    raise SystemExit('REFERENCE_V162 generator required before v14.3')

marker="# REFERENCE_V162: v14.2 compacts the lower-face cage, preserves a softer adult jaw instead of a long V, and places a true side-facing ocular layer on the lateral head surface so profile audits read an eye rather than a dot."
if marker not in s:
    raise SystemExit('v14.3 marker anchor missing')
s=s.replace(marker,marker+"\n# REFERENCE_V163: v14.3 removes the detached lateral profile-eye plate after 3/4 audit exposed a duplicate-eye artifact; profile readability now comes from the original eye canthus wrapping farther around the orbital rim.",1)

face['revision']='v14.3'
face['reference_intent']='adult realistic-anime heroine; compact lower face and soft jaw retained from v14.2; exact profile eye must be a narrow continuation of the real eye at the lateral canthus, never a detached side-eye plate'
face_path.write_text(json.dumps(face,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

# Remove the v14.2 side-eye plate entirely. It was technically edge-on in front view but became a visible third eye in 3/4.
start=s.find(" # v14.2 exact-profile ocular layer. Constant-X YZ geometry is edge-on from the front but fully readable in true profile.")
if start < 0:
    raise SystemExit('v14.3 profile plate start missing')
end_line=" add_strand(HEAD,f'ProfileHeroLashV142_{side}',[(_px+side*.0011,eye_y+.0068,_pz+.0070),(_px+side*.0018,eye_y+.0105,_pz+.0145),(_px+side*.0027,eye_y+.0110,_pz+.0220)],.00031*eye_contrast,HAIR)"
end=s.find(end_line,start)
if end < 0:
    raise SystemExit('v14.3 profile plate end missing')
end=s.find('\n',end+len(end_line))
if end < 0:
    end=len(s)
s=s[:start]+s[end+1:]

# Wrap the existing side helper around the eye instead of inventing a second eye.
# It remains close enough to the front aperture to merge in 3/4, but moves outward enough to show in exact profile.
repls=(
 ("ex+side*eye_rx*.892,eye_y+.0001,.1027,eye_ry*1.420,.01080,SCLERA,52",
  "ex+side*eye_rx*1.185,eye_y+.0001,.1012,eye_ry*1.08,.01280,SCLERA,54"),
 ("ex+side*eye_rx*.900,eye_y+.0002,.10365,eye_ry*.900,.00665,IRIS_INNER,48",
  "ex+side*eye_rx*1.195,eye_y+.0002,.10215,eye_ry*.665,.00745,IRIS_INNER,46"),
 ("ex+side*eye_rx*.904,eye_y+.0001,.10405,eye_ry*.390,.00305,PUPIL,36",
  "ex+side*eye_rx*1.200,eye_y+.0001,.10255,eye_ry*.285,.00315,PUPIL,34"),
 ("ex+side*eye_rx*.915,eye_y+eye_ry*.96,.1020","ex+side*eye_rx*1.175,eye_y+eye_ry*.78,.1004"),
 ("ex+side*eye_rx*.918,eye_y+eye_ry*.39,.10775","ex+side*eye_rx*1.190,eye_y+eye_ry*.34,.10810"),
 ("ex+side*eye_rx*.918,eye_y-.0001,.10925","ex+side*eye_rx*1.195,eye_y-.0001,.11030"),
 ("ex+side*eye_rx*.915,eye_y-eye_ry*.92,.1021","ex+side*eye_rx*1.175,eye_y-eye_ry*.72,.1006"),
 ("ex+side*eye_rx*.918,eye_y-eye_ry*.40,.10705","ex+side*eye_rx*1.190,eye_y-eye_ry*.32,.10775"),
 ("ex+side*eye_rx*.918,eye_y-.0001,.10895","ex+side*eye_rx*1.195,eye_y-.0001,.10995"),
)
for old,new in repls:
    if old not in s:
        raise SystemExit('v14.3 canthus anchor missing: '+old[:54])
    s=s.replace(old,new,1)

# A single outer-canthus lash extension follows the wrapped eye. Unlike v14.2 this is not a filled sclera plate.
anchor=" add_strand(HEAD,f'ProfileLowerLidV140_{side}',[(ex+side*eye_rx*1.175,eye_y-eye_ry*.72,.1006),(ex+side*eye_rx*1.190,eye_y-eye_ry*.32,.10775),(ex+side*eye_rx*1.195,eye_y-.0001,.10995)],.00018*eye_contrast,EYE_WET)"
if anchor not in s:
    raise SystemExit('v14.3 lash insert anchor missing')
extra="\n add_strand(HEAD,f'WrappedCanthusLashV143_{side}',[(ex+side*eye_rx*1.08,eye_y+eye_tilt+.0032,.1043),(ex+side*eye_rx*1.18,eye_y+eye_tilt+.0057,.1086),(ex+side*eye_rx*1.27,eye_y+eye_tilt+.0044,.1130)],.00026*eye_contrast,HAIR)"
s=s.replace(anchor,anchor+extra,1)

old="ROOT['character_revision']='v14.2';"
new="ROOT['character_revision']='v14.3';"
if old not in s:
    raise SystemExit('v14.3 revision anchor missing')
s=s.replace(old,new,1)
needle="HEAD_ASSET['face_rebuild_revision']='v14.2';"
if needle in s:
    s=s.replace(needle,"HEAD_ASSET['face_rebuild_revision']='v14.3';",1)
needle="FACE_ASSET['profile_ocular_revision']='v14.2';"
if needle in s:
    s=s.replace(needle,"FACE_ASSET['profile_ocular_revision']='v14.3-wrapped-canthus';",1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V163: removed detached profile eye and wrapped real canthus around orbital rim')
