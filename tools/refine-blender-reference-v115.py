from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V115' in s:
    print('Blender heroine generator already carries REFERENCE_V115')
    raise SystemExit(0)
if '# REFERENCE_V114' not in s:
    raise SystemExit('REFERENCE_V114 generator required before v11.5')
marker='# REFERENCE_V114: stronger public-basemesh-scale facial projection gives the clean shell a readable nose/lip/chin silhouette and retargets surface accents to it.'
if marker not in s:
    raise SystemExit('v11.5 REFERENCE_V114 marker anchor missing')
s=s.replace(marker,marker+'\n# REFERENCE_V115: the clean shell gains a tapered adult jaw, deeper orbital seating, stronger malar transition and a naturally wider mouth after five-view review.',1)

old_sections=""" sections=[
  (.164,.071,.078,.080,-.010),(.150,.101,.084,.086,-.008),(.132,.119,.089,.091,-.006),
  (.108,.128,.094,.095,-.003),(.082,.131,.098,.097,-.001),(.058,.129,.100,.098,.001),
  (.036,.125,.101,.099,.002),(.014,.128,.102,.099,.003),(-.008,.127,.102,.100,.003),
  (-.030,.123,.102,.101,.002),(-.052,.118,.101,.102,.001),(-.072,.110,.100,.103,.000),
  (-.089,.102,.098,.103,-.001),(-.103,.094,.096,.102,-.003),(-.115,.085,.094,.101,-.004),
  (-.126,.075,.091,.098,-.006),(-.135,.062,.087,.093,-.008),(-.141,.047,.081,.086,-.009),
  (-.145,.030,.072,.078,-.010)
 ]
"""
new_sections=""" sections=[
  (.164,.071,.078,.080,-.010),(.150,.101,.084,.086,-.008),(.132,.119,.089,.091,-.006),
  (.108,.128,.094,.095,-.003),(.082,.130,.098,.097,-.001),(.058,.128,.100,.098,.001),
  (.036,.124,.101,.099,.002),(.014,.126,.102,.099,.003),(-.008,.125,.102,.100,.003),
  (-.030,.120,.102,.101,.002),(-.052,.114,.101,.102,.001),(-.072,.105,.100,.103,.000),
  (-.089,.096,.098,.103,-.001),(-.103,.087,.096,.102,-.003),(-.115,.078,.094,.101,-.004),
  (-.126,.068,.091,.098,-.006),(-.135,.056,.087,.093,-.008),(-.141,.042,.081,.086,-.009),
  (-.145,.026,.072,.078,-.010)
 ]
"""
if old_sections not in s:
    raise SystemExit('v11.5 head section block missing')
s=s.replace(old_sections,new_sections,1)

old_orbit="""     z-=fm*.0017*math.exp(-((x-ex)/.0265)**2-((yy-.033)/.0190)**2)
     # Brow/zygomatic bridge and adult cheek break.
     z+=fm*.0022*math.exp(-((x-ex)/.031)**2-((yy-.061)/.022)**2)
     z+=fm*.0048*math.exp(-((x-side*.057)/.033)**2-((yy+.004)/.035)**2)
     z-=fm*.0021*math.exp(-((x-side*.068)/.029)**2-((yy+.053)/.034)**2)
"""
new_orbit="""     z-=fm*.0027*math.exp(-((x-ex)/.0265)**2-((yy-.033)/.0195)**2)
     # Brow/zygomatic bridge and adult cheek break.  The malar peak sits slightly below/outside
     # the eye, then falls into a shallow lower-cheek hollow instead of one flat side plane.
     z+=fm*.0025*math.exp(-((x-ex)/.031)**2-((yy-.061)/.022)**2)
     z+=fm*.0062*math.exp(-((x-side*.057)/.034)**2-((yy+.004)/.036)**2)
     z-=fm*.0027*math.exp(-((x-side*.069)/.030)**2-((yy+.054)/.035)**2)
"""
if old_orbit not in s:
    raise SystemExit('v11.5 orbit/cheek block missing')
s=s.replace(old_orbit,new_orbit,1)

# Retarget eye contour curves to the seated v11.3 eye plane; the old v10.0 Z values sat too far forward.
s=s.replace("add_strand(HEAD,f'UpperLashV100_{side}',[(inner,eye_y-eye_tilt+.0006,.10395),(ex,eye_y+.0101,.10450),(outer,eye_y+eye_tilt+.0006,.10400)],.00054,HAIR)","add_strand(HEAD,f'UpperLashV115_{side}',[(inner,eye_y-eye_tilt+.0006,.10255),(ex,eye_y+.0101,.10305),(outer,eye_y+eye_tilt+.0006,.10260)],.00048,HAIR)",1)
s=s.replace("add_strand(HEAD,f'UpperLidFoldV100_{side}',[(inner+side*.0035,eye_y-eye_tilt+.0025,.10350),(ex,eye_y+.0124,.10392),(outer-side*.0035,eye_y+eye_tilt+.0025,.10350)],.00014,FACE_DARK)","add_strand(HEAD,f'UpperLidFoldV115_{side}',[(inner+side*.0035,eye_y-eye_tilt+.0025,.10215),(ex,eye_y+.0124,.10255),(outer-side*.0035,eye_y+eye_tilt+.0025,.10215)],.00011,FACE_DARK)",1)
s=s.replace("add_strand(HEAD,f'LowerLidV100_{side}',[(inner+side*.0035,eye_y-eye_tilt-.0001,.10342),(ex,eye_y-.0072,.10368),(outer-side*.0035,eye_y+eye_tilt-.0001,.10342)],.000052,FACE_DARK)","add_strand(HEAD,f'LowerLidV115_{side}',[(inner+side*.0035,eye_y-eye_tilt-.0001,.10205),(ex,eye_y-.0072,.10227),(outer-side*.0035,eye_y+eye_tilt-.0001,.10205)],.000045,FACE_DARK)",1)

old_lips="""add_panel(HEAD,'UpperLipV114_L',[(-.0230,-.0848,.1195),(-.0112,-.0802,.1206),(0,-.0832,.1221),(0,-.0867,.1224),(-.0098,-.0860,.1213),(-.0215,-.0880,.1200)],.00028,LIP)
add_panel(HEAD,'UpperLipV114_R',[(0,-.0832,.1221),(.0112,-.0802,.1206),(.0230,-.0848,.1195),(.0215,-.0880,.1200),(.0098,-.0860,.1213),(0,-.0867,.1224)],.00028,LIP)
add_panel(HEAD,'LowerLipV114',[(-.0215,-.0883,.1201),(0,-.0877,.1222),(.0215,-.0883,.1201),(.0180,-.0944,.1198),(0,-.0970,.1208),(-.0180,-.0944,.1198)],.00032,LIP)
add_strand(HEAD,'MouthSeamV114',[(-.0218,-.0868,.1200),(-.0102,-.0863,.1212),(0,-.0871,.1225),(.0102,-.0863,.1212),(.0218,-.0868,.1200)],.000040,FACE_DARK)
"""
new_lips="""add_panel(HEAD,'UpperLipV115_L',[(-.0265,-.0849,.1189),(-.0130,-.0801,.1205),(0,-.0831,.1222),(0,-.0868,.1225),(-.0110,-.0860,.1213),(-.0250,-.0882,.1195)],.00027,LIP)
add_panel(HEAD,'UpperLipV115_R',[(0,-.0831,.1222),(.0130,-.0801,.1205),(.0265,-.0849,.1189),(.0250,-.0882,.1195),(.0110,-.0860,.1213),(0,-.0868,.1225)],.00027,LIP)
add_panel(HEAD,'LowerLipV115',[(-.0250,-.0884,.1196),(0,-.0878,.1222),(.0250,-.0884,.1196),(.0210,-.0945,.1194),(0,-.0971,.1208),(-.0210,-.0945,.1194)],.00031,LIP)
add_strand(HEAD,'MouthSeamV115',[(-.0255,-.0869,.1196),(-.0118,-.0863,.1211),(0,-.0872,.1226),(.0118,-.0863,.1211),(.0255,-.0869,.1196)],.000038,FACE_DARK)
"""
if old_lips not in s:
    raise SystemExit('v11.5 lip block missing')
s=s.replace(old_lips,new_lips,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V115: tapered adult jaw, stronger cheek/orbit structure, seated lid contours and wider natural mouth')
