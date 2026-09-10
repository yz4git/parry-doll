from pathlib import Path

p=Path(__file__).with_name('make-blender-heroine.py')
s=p.read_text(encoding='utf-8')

if '# REFERENCE_V102' in s:
    print('Blender heroine generator already carries REFERENCE_V102')
    raise SystemExit(0)
if '# REFERENCE_V101' not in s:
    raise SystemExit('REFERENCE_V101 generator required before v10.2')

marker='# REFERENCE_V101: side hair becomes a scalp-tight undercap plus several rounded swept locks, replacing the large profile-facing leaf plate.'
if marker not in s:
    raise SystemExit('v10.2 REFERENCE_V101 marker anchor missing')
s=s.replace(marker, marker+'\n# REFERENCE_V102: temporal lock tips sweep rearward around the ear instead of dropping into straight claw-like prongs.',1)

repls=[
("""  (side*head_w*.482,.028,-head_d*.027),
  (side*head_w*.466,-.006,-head_d*.043),
  (side*head_w*.438,-.032,-head_d*.055)
 ],[.003,.006,.009,.010,.009,.006,.0015],[.007,.012,.016,.019,.017,.011,.0035],HAIR,14,6)""",
"""  (side*head_w*.482,.028,-head_d*.027),
  (side*head_w*.468,.010,-head_d*.050),
  (side*head_w*.442,-.004,-head_d*.075)
 ],[.003,.006,.009,.010,.0085,.005,.0012],[.007,.012,.016,.019,.015,.009,.0028],HAIR,14,6)"""),
("""  (side*head_w*.489,.016,-head_d*.091),
  (side*head_w*.470,-.020,-head_d*.108),
  (side*head_w*.440,-.048,-head_d*.121)
 ],[.003,.006,.009,.011,.010,.006,.0015],[.008,.014,.019,.022,.020,.013,.004],HAIR,14,6)""",
"""  (side*head_w*.489,.016,-head_d*.091),
  (side*head_w*.474,.002,-head_d*.122),
  (side*head_w*.446,-.010,-head_d*.151)
 ],[.003,.006,.009,.011,.009,.0055,.0012],[.008,.014,.019,.022,.018,.011,.0032],HAIR,14,6)"""),
("""  (side*head_w*.482,.008,-head_d*.151),
  (side*head_w*.463,-.030,-head_d*.168),
  (side*head_w*.432,-.058,-head_d*.181)
 ],[.003,.006,.009,.011,.010,.006,.0015],[.008,.014,.020,.023,.020,.013,.004],HAIR,14,6)""",
"""  (side*head_w*.482,.008,-head_d*.151),
  (side*head_w*.466,-.004,-head_d*.184),
  (side*head_w*.438,-.016,-head_d*.211)
 ],[.003,.006,.009,.011,.009,.0055,.0012],[.008,.014,.020,.023,.018,.011,.0032],HAIR,14,6)"""),
("""  (side*head_w*.488,.036,-head_d*.101),
  (side*head_w*.468,-.012,-head_d*.124),
  (side*head_w*.438,-.046,-head_d*.142)
""",
"""  (side*head_w*.488,.036,-head_d*.101),
  (side*head_w*.472,.004,-head_d*.128),
  (side*head_w*.443,-.012,-head_d*.156)
""")
]
for old,new in repls:
    if old not in s:
        raise SystemExit('v10.2 temporal lock anchor missing')
    s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Applied REFERENCE_V102: temporal tips shortened and swept rearward around the ear')
