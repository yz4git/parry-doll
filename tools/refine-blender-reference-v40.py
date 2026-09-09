from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V40' in s:
    print('Blender heroine generator already carries REFERENCE_V40')
    raise SystemExit(0)
if '# REFERENCE_V39' not in s:
    raise SystemExit('REFERENCE_V39 generator required before v4.0')

s=s.replace(
    '# REFERENCE_V39: portrait de-doll pass with slimmer eyes, stronger nose/lips and finer asymmetric fringe.',
    '# REFERENCE_V39: portrait de-doll pass with slimmer eyes, stronger nose/lips and finer asymmetric fringe.\n# REFERENCE_V40: narrower shoulder flow and split couture skirt that exposes the long-leg silhouette.',
    1,
)

# Narrow only the visual deltoid/clavicle shell. The core bust/waist envelope remains measured-reference locked.
a=s.index('# Anatomical clavicle/deltoid bridge')
b=s.index('# Reference-like harness:',a)
shoulder=s[a:b]
shoulder=shoulder.replace("side*bust_w*.405,.238,.002","side*bust_w*.365,.238,.002",1)
shoulder=shoulder.replace("(bust_w*.125,.064,bust_d*.150)","(bust_w*.108,.061,bust_d*.142)",1)
shoulder=shoulder.replace("side*bust_w*.430,.225,bust_d*.18","side*bust_w*.392,.225,bust_d*.18",1)
shoulder=shoulder.replace("(bust_w*.285,.010,.008)","(bust_w*.250,.010,.008)",1)
s=s[:a]+shoulder+s[b:]

# Rebuild the skirt as a short split front with two swept-back couture tails.
# The v3.9 front audit showed too many long vertical strips crossing the legs.
a=s.index('# Layered pointed skirt measured from the reference silhouette.')
b=s.index('# === REFERENCE COUTURE MICRO DETAIL v2.6 ===',a)
skirt="""# Layered split skirt v4.0: short front petals keep the thigh line visible; long tails move behind/outside the legs.
add_panel(PELVIS,'FrontCenterV40_L',[(-.145,.124,.142),(-.010,.118,.152),(-.024,-.150,.160),(-.080,-.295,.142),(-.170,-.155,.108)],.016,WHITE)
add_panel(PELVIS,'FrontCenterV40_R',[(.010,.118,.152),(.145,.124,.142),(.170,-.155,.108),(.080,-.295,.142),(.024,-.150,.160)],.016,WHITE)
add_panel(PELVIS,'HipPetalV40_L',[(-.112,.120,.116),(-.226,.096,.092),(-.276,-.080,.070),(-.218,-.245,.090),(-.132,-.150,.122)],.015,BLACK)
add_panel(PELVIS,'HipPetalV40_R',[(.112,.120,.116),(.132,-.150,.122),(.218,-.245,.090),(.276,-.080,.070),(.226,.096,.092)],.015,BLACK)
# Bright outer split panels stop high on the thigh instead of becoming calf-length white stripes.
add_panel(PELVIS,'OuterPetalV40_L',[(-.180,.108,.104),(-.252,.072,.070),(-.300,-.135,.050),(-.250,-.335,.068),(-.174,-.190,.112)],.013,WHITE)
add_panel(PELVIS,'OuterPetalV40_R',[(.180,.108,.104),(.174,-.190,.112),(.250,-.335,.068),(.300,-.135,.050),(.252,.072,.070)],.013,WHITE)
# Black under-petals create a clean split silhouette and visually lengthen the legs.
add_panel(PELVIS,'SplitUnderV40_L',[(-.210,.095,.040),(-.278,.060,.010),(-.318,-.205,-.018),(-.276,-.455,.018),(-.218,-.250,.060)],.012,BLACK)
add_panel(PELVIS,'SplitUnderV40_R',[(.210,.095,.040),(.218,-.250,.060),(.276,-.455,.018),(.318,-.205,-.018),(.278,.060,.010)],.012,BLACK)
# Only two long couture tails remain, swept backward and outward so the front leg columns stay clear.
add_panel(PELVIS,'RearTailV40_L',[(-.250,.080,-.120),(-.158,.070,-.160),(-.205,-.420,-.205),(-.285,-.820,-.145),(-.350,-.470,-.090)],.014,BLACK)
add_panel(PELVIS,'RearTailV40_R',[(.158,.070,-.160),(.250,.080,-.120),(.350,-.470,-.090),(.285,-.820,-.145),(.205,-.420,-.205)],.014,BLACK)
add_panel(PELVIS,'RearTailInlayV40_L',[(-.270,.050,-.132),(-.190,.045,-.168),(-.226,-.405,-.188),(-.282,-.690,-.140),(-.326,-.445,-.104)],.009,WHITE)
add_panel(PELVIS,'RearTailInlayV40_R',[(.190,.045,-.168),(.270,.050,-.132),(.326,-.445,-.104),(.282,-.690,-.140),(.226,-.405,-.188)],.009,WHITE)

"""
s=s[:a]+skirt+s[b:]
p.write_text(s,encoding='utf-8')

# Match the slimmer shoulder shell in runtime retargeting without touching gameplay nodes.
runtime=ROOT/'visual-src'/'blender-heroine.js'
r=runtime.read_text(encoding='utf-8')
old='const REF_SHOULDER_HALF=.197;'
new='const REF_SHOULDER_HALF=.188;'
if old in r:
    r=r.replace(old,new,1)
elif new not in r:
    raise SystemExit('v4.0 runtime shoulder anchor missing')
runtime.write_text(r,encoding='utf-8')

print('Applied REFERENCE_V40: narrower shoulder flow and cleaner split couture skirt')
