"""Compare genuine skinned VRoid beta CC0 assets, not procedural mannequins.
Source VRM retained with all original spring bones and expressions. Recolor textures in binary
GLTF rather than tinting nodes so source materials and MToon data stay consistent.
"""
import json,struct,sys,io,hashlib
from pathlib import Path
from PIL import Image,ImageOps
src,dst=map(Path,sys.argv[1:3])
raw=src.read_bytes()
magic,ver,total=struct.unpack_from('<4sII',raw);assert magic==b'glTF' and ver==2 and total==len(raw)
chunks={};p=12
while p<len(raw):
    n,t=struct.unpack_from('<I4s',raw,p);chunks[t]=raw[p+8:p+8+n];p+=8+n
g=json.loads(chunks[b'JSON']);b=bytearray(chunks[b'BIN\0'])
vrm=g.get('extensions',{}).get('VRM',{});meta=vrm.get('meta',{})
print('VRM meta:',json.dumps(meta,ensure_ascii=False))
assert str(meta.get('licenseName','')).upper()=='CC0', 'source embedded license is not CC0'
report={'source':src.name,'sha256':hashlib.sha256(raw).hexdigest(),'license':meta.get('licenseName'),'materials':[],'bones':len(vrm.get('humanoid',{}).get('humanBones',[])),'expressions':len(vrm.get('blendShapeMaster',{}).get('blendShapeGroups',[]))}
def align():
    while len(b)%4:b.append(0)
def new_image(ii,kind):
    im=g['images'][ii];bv=g['bufferViews'][im['bufferView']];a=bv.get('byteOffset',0)
    old=Image.open(io.BytesIO(b[a:a+bv['byteLength']])).convert('RGBA');alpha=old.getchannel('A')
    lum=ImageOps.grayscale(old)
    # Saturated black-brown root and controlled chestnut glints; retain original painted highlights.
    if kind=='hair':colors=((17,10,9),(112,73,56))
    elif kind=='brow':colors=((19,10,9),(75,46,37))
    else:colors=((20,10,7),(166,105,60))
    img=ImageOps.colorize(lum,*colors).convert('RGBA');img.putalpha(alpha)
    out=io.BytesIO();img.save(out,format='PNG',optimize=True);data=out.getvalue()
    align();offset=len(b);b.extend(data)
    g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data)})
    g['images'].append({'bufferView':len(g['bufferViews'])-1,'mimeType':'image/png','name':'N4_'+kind+'_'+str(ii)})
    return len(g['images'])-1
cache={}
def recolor_tex(ti,kind):
    if not isinstance(ti,int) or ti<0 or ti>=len(g['textures']):return ti
    tx=g['textures'][ti]
    if 'source' not in tx:return ti
    key=(tx['source'],kind)
    if key not in cache:cache[key]=new_image(*key)
    if (ti,kind) not in texcache:
        cp=dict(tx);cp['source']=cache[key];g['textures'].append(cp);texcache[(ti,kind)]=len(g['textures'])-1
    return texcache[(ti,kind)]
texcache={}
for i,m in enumerate(g['materials']):
    name=m.get('name','').lower()
    kind='brow' if any(x in name for x in ('eyebrow','眉')) else 'iris' if any(x in name for x in ('eyeiris','iris','瞳')) else 'hair' if any(x in name for x in ('hair','髪')) else None
    rec={'name':m.get('name',''),'change':kind}
    if kind:
        p=m.setdefault('pbrMetallicRoughness',{});t=p.get('baseColorTexture')
        if t:t['index']=recolor_tex(t['index'],kind);p['baseColorFactor']=[1,1,1,1]
        if i<len(vrm.get('materialProperties',[])):
            mt=vrm['materialProperties'][i];tx=mt.get('textureProperties',{});v=mt.get('vectorProperties',{})
            for k in ('_MainTex','_ShadeTexture'):
                if k in tx:tx[k]=recolor_tex(tx[k],kind)
            if '_Color' in v:v['_Color']=[1,1,1,1]
            if '_ShadeColor' in v:v['_ShadeColor']=[.63,.49,.47,1]
    report['materials'].append(rec)
meta['title']='N4 VRoid candidate '+src.stem
meta['author']='pixiv Inc.; N4 color adaptation'
align();g['buffers'][0]['byteLength']=len(b)
j=json.dumps(g,ensure_ascii=False,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
res=struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(b))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(b),b'BIN\0')+b
dst.write_bytes(res);dst.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
