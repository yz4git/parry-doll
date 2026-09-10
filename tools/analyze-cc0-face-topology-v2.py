#!/usr/bin/env python3
"""Extract a LOCAL facial topology patch from pinned CC0 MakeHuman/MPFB hm08.

v1 proved provenance/fetching, but some morph categories (notably chin bone targets)
contain broad compensating edits. v2 therefore constrains facial morph vertices by
the actual hm08 head target bounds and by the +Z front half of the head before
expanding only two adjacency rings.
"""
from __future__ import annotations
import argparse, gzip, json
from collections import Counter, defaultdict
from pathlib import Path

BODY_VERTEX_LIMIT=13380
CORE_REGIONS=("cheek","chin","eyebrows","eyes","forehead","mouth","nose")
SOURCE_COMMIT="03264788d967bcd33844be70e35db05b231aa017"
SOURCE_REPO="https://github.com/nirholas/three.ws"


def load_obj(path):
    verts=[];faces=[]
    with open(path,"r",encoding="utf-8",errors="replace") as f:
        for line in f:
            if line.startswith("v "):
                p=line.split();verts.append(tuple(map(float,p[1:4])))
            elif line.startswith("f "):
                ids=[]
                for tok in line.split()[1:]:
                    v=tok.split('/',1)[0]
                    if v:
                        n=int(v);ids.append(len(verts)+n if n<0 else n-1)
                if len(ids)>=3:faces.append(tuple(ids))
    return verts,faces


def target_ids(root):
    out=set();count=0
    paths=list(root.rglob("*.target"))+list(root.rglob("*.target.gz")) if root.exists() else []
    for p in sorted(paths):
        count+=1;op=gzip.open if p.suffix==".gz" else open
        with op(p,"rt",encoding="utf-8",errors="replace") as f:
            for line in f:
                s=line.strip()
                if not s or s.startswith('#'):continue
                try:i=int(s.split()[0])
                except (ValueError,IndexError):continue
                if 0<=i<BODY_VERTEX_LIMIT:out.add(i)
    return out,count


def bbox(verts,ids):
    pts=[verts[i] for i in ids]
    return {"min":[min(p[k] for p in pts) for k in range(3)],"max":[max(p[k] for p in pts) for k in range(3)]}


def adjacency(faces):
    adj=defaultdict(set);body=[]
    for f in faces:
        if any(i<0 or i>=BODY_VERTEX_LIMIT for i in f):continue
        body.append(f)
        for a,b in zip(f,f[1:]+f[:1]):
            adj[a].add(b);adj[b].add(a)
    return adj,body


def expand(seed,adj,allowed,rings=2):
    out=set(seed);front=set(seed)
    for _ in range(rings):
        nxt=set()
        for v in front:nxt.update(adj.get(v,()))
        nxt &= allowed;nxt -= out
        out |= nxt;front=nxt
    return out


def components(nodes,adj):
    unseen=set(nodes);res=[]
    while unseen:
        s=unseen.pop();c={s};stack=[s]
        while stack:
            v=stack.pop()
            for n in adj.get(v,()):
                if n in unseen:unseen.remove(n);c.add(n);stack.append(n)
        res.append(c)
    return sorted(res,key=len,reverse=True)


def profile_samples(verts,ids,bins=28):
    b=bbox(verts,ids);mn,mx=b['min'],b['max'];sx=max(mx[0]-mn[0],1e-8);sy=max(mx[1]-mn[1],1e-8);sz=max(mx[2]-mn[2],1e-8)
    cx=(mn[0]+mx[0])*.5;band=sx*.075;out=[]
    for bi in range(bins):
        y0=mn[1]+sy*bi/bins;y1=mn[1]+sy*(bi+1)/bins
        cand=[verts[i] for i in ids if y0<=verts[i][1]<=y1 and abs(verts[i][0]-cx)<=band]
        if not cand:continue
        p=max(cand,key=lambda q:q[2])
        out.append({"y":round((p[1]-mn[1])/sy,6),"front_z":round((p[2]-mn[2])/sz,6),"x":round((p[0]-cx)/sx,6)})
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-root',required=True,type=Path);args=ap.parse_args()
    root=args.source_root
    readme=(root/'README.md').read_text(encoding='utf-8',errors='replace');lic=(root/'LICENSE.md').read_text(encoding='utf-8',errors='replace')
    if 'CC0' not in readme or 'CC0' not in lic:raise SystemExit('CC0 provenance check failed')
    verts,faces=load_obj(root/'3dobjs'/'base.obj');adj,body_faces=adjacency(faces)
    head,head_files=target_ids(root/'targets'/'head')
    if not head:raise SystemExit('head targets missing')
    hb=bbox(verts,head);hmin,hmax=hb['min'],hb['max'];hdepth=hmax[2]-hmin[2];hwidth=max(abs(hmin[0]),abs(hmax[0]));hheight=hmax[1]-hmin[1]
    # Generic hm08 faces +Z. Keep the front ~72% of head depth; permit a small relaxed skirt for closure rings.
    front_cut=hmin[2]+hdepth*.28
    core_allowed={i for i,(x,y,z) in enumerate(verts[:BODY_VERTEX_LIMIT]) if abs(x)<=hwidth*1.02 and hmin[1]<=y<=hmax[1] and z>=front_cut}
    ring_allowed={i for i,(x,y,z) in enumerate(verts[:BODY_VERTEX_LIMIT]) if abs(x)<=hwidth*1.06 and hmin[1]-hheight*.035<=y<=hmax[1] and z>=front_cut-hdepth*.06}
    region_raw={};region_local={};region_files={}
    for r in CORE_REGIONS:
        ids,n=target_ids(root/'targets'/r);region_raw[r]=ids;region_local[r]=ids & core_allowed;region_files[r]=n
    seed=set().union(*(region_local[r] for r in CORE_REGIONS))
    if len(seed)<250:raise SystemExit(f'face seed too small: {len(seed)}')
    expanded=expand(seed,adj,ring_allowed,2)
    patch_faces=[f for f in body_faces if all(i in expanded for i in f)]
    used={i for f in patch_faces for i in f}
    # Retain only the largest connected surface component. Small islands from eye/teeth helpers are not the skin topology target.
    padj=defaultdict(set)
    for f in patch_faces:
        for a,b in zip(f,f[1:]+f[:1]):padj[a].add(b);padj[b].add(a)
    comps=components(used,padj)
    if not comps:raise SystemExit('no patch components')
    skin=set(comps[0]);patch_faces=[f for f in patch_faces if all(i in skin for i in f)];used={i for f in patch_faces for i in f}
    pb=bbox(verts,used);mn,mx=pb['min'],pb['max'];center=[(mn[k]+mx[k])*.5 for k in range(3)];span=[max(mx[k]-mn[k],1e-8) for k in range(3)]
    ordered=sorted(used);remap={o:i for i,o in enumerate(ordered)}
    nverts=[[round((verts[o][0]-center[0])/span[0],6),round((verts[o][1]-center[1])/span[1],6),round((verts[o][2]-center[2])/span[2],6)] for o in ordered]
    nfaces=[[remap[i] for i in f] for f in patch_faces]
    edge_count=Counter()
    for f in patch_faces:
        for a,b in zip(f,f[1:]+f[:1]):edge_count[tuple(sorted((a,b)))]+=1
    boundary=[e for e,n in edge_count.items() if n==1];quad=sum(len(f)==4 for f in patch_faces);tri=sum(len(f)==3 for f in patch_faces);ng=sum(len(f)>4 for f in patch_faces)
    stats={
      "source":{"repo":SOURCE_REPO,"commit":SOURCE_COMMIT,"license":"CC0-1.0","base_mesh":"MakeHuman/MPFB hm08","coordinate_system":"Y-up, +Z face-forward"},
      "head_roi":{"head_target_files":head_files,"head_vertices":len(head),"bbox":hb,"front_cut_z":front_cut,"core_allowed_vertices":len(core_allowed),"ring_allowed_vertices":len(ring_allowed)},
      "regions":{r:{"target_files":region_files[r],"raw_vertices":len(region_raw[r]),"local_vertices":len(region_local[r])} for r in CORE_REGIONS},
      "patch":{"seed_vertices":len(seed),"expanded_vertices":len(expanded),"retained_vertices":len(used),"faces":len(patch_faces),"quads":quad,"triangles":tri,"ngons":ng,"quad_ratio":round(quad/max(len(patch_faces),1),6),"boundary_edges":len(boundary),"components_before_largest":[len(c) for c in comps[:12]],"bbox":pb,"profile_samples_normalized":profile_samples(verts,used)}
    }
    template={"version":2,"license":"CC0-1.0","source_repo":SOURCE_REPO,"source_commit":SOURCE_COMMIT,"description":"Local hm08 face-skin topology: facial morph union intersected with head +Z ROI, two adjacency rings, largest connected surface only. Coordinates independently normalized about patch center.","normalization":{"source_center":center,"source_span":span},"vertices":nverts,"faces":nfaces}
    Path('tools/cc0-face-topology-stats.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf-8')
    Path('tools/cc0-face-topology-template-v1.json').write_text(json.dumps(template,separators=(',',':'))+'\n',encoding='utf-8')
    report=f"""# CC0 Face Topology Analysis\n\nSource: MakeHuman/MPFB hm08 data vendored by `nirholas/three.ws`, pinned at `{SOURCE_COMMIT}` and declared CC0-1.0.\n\n## v2 local-face extraction\n\n- hm08 vertices: **{len(verts):,}**; body range: 0–{BODY_VERTEX_LIMIT-1:,}.\n- Head morph envelope: **{len(head):,} vertices**, bbox `{hb}`.\n- +Z facial ROI seed: **{len(seed):,} vertices** from cheek/chin/brows/eyes/forehead/mouth/nose after geometric clipping.\n- After two adjacency rings: **{len(expanded):,} vertices**.\n- Largest connected face skin patch: **{len(used):,} vertices / {len(patch_faces):,} faces**.\n- Quads: **{quad:,} ({quad/max(len(patch_faces),1):.1%})**; triangles: {tri:,}; n-gons: {ng:,}.\n- Open patch boundary edges: **{len(boundary):,}**. A nonzero boundary is expected and is the seam used to blend into PARRY DOLL's cranium.\n\n## PARRY DOLL use\n\nThe generic CC0 geometry is **not the heroine's identity target**. The extracted patch supplies edge flow and local vertex density only. v7.5+ remains the side-profile constraint, while the generated PARRY DOLL face sheet controls eye scale, V-jaw, cheek width, nose and lip shape. The next hybrid head should fit this topology to those targets and bridge its boundary into a simpler rear cranium.\n\nMachine data: `tools/cc0-face-topology-stats.json` and `tools/cc0-face-topology-template-v1.json`.\n"""
    Path('docs/CC0_FACE_TOPOLOGY_ANALYSIS.md').write_text(report,encoding='utf-8')
    print(report);print('template vertices',len(nverts),'faces',len(nfaces))

if __name__=='__main__':main()
