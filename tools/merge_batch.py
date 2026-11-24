"""Validate (and with --apply merge) a measure-seeding batch proposal into data/lb-2027.json.
Usage: python3 -I tools/merge_batch.py data/lb-2027.json work/batches/batchNN_proposal.json [--apply]
"""
import json,sys,re
law,prop=sys.argv[1],sys.argv[2]; apply='--apply' in sys.argv
d=json.load(open(law,encoding='utf-8')); p=json.load(open(prop,encoding='utf-8'))
ref=json.load(open(law.replace('lb-2027.json','reference.json'),encoding='utf-8'))
seeds={e['id'] for e in ref['enums']['seed']}
errs=[]; E=errs.append
pids={x['id'] for x in d['paragraphs']}
rows={r['id']:r for r in d['fiscal_rows']}
mids={m['id'] for m in d['measures']}
A={a['number']:a for a in d['articles']}
covered_arts={r.split('-')[0] for m in d['measures'] for r in m['refs']}
prop_arts=set()
nxt=max(int(i[1:]) for i in mids)+1
req=['law_id','id','title_en','description_en','refs','fiscal_rows','seed','lineage','thematic','ministry','relevance','low_priority','csr','profile']
seen=set(); assigned={}
for k,m in enumerate(p['measures']):
    i=m.get('id')
    if i!=f"M{nxt+k:03d}": E(f"{i}: expected M{nxt+k:03d}")
    if i in mids or i in seen: E(f"{i}: duplicate id")
    seen.add(i)
    for f in req:
        if f not in m: 
            if f in('ministry',) : m[f]=None
            else: E(f"{i}: missing {f}")
    if m.get('law_id')!='lb-2027': E(f"{i}: law_id")
    if m.get('seed') not in seeds: E(f"{i}: bad seed {m.get('seed')}")
    if not m.get('title_en') or not m.get('description_en'): E(f"{i}: empty title/description")
    for r in m.get('refs',[]):
        if r not in pids: E(f"{i}: unknown ref {r}")
    if not m.get('refs'): E(f"{i}: no refs")
    arts={r.split('-')[0] for r in m.get('refs',[])}
    if len(arts)!=1: E(f"{i}: article-level rule: refs must belong to one article, got {sorted(arts)}")
    else:
        a=next(iter(arts)); n=int(a[1:])
        allp=[x['id'] if isinstance(x,dict) else x for x in A[n]['paragraphs']]
        if set(m['refs'])!=set(allp): E(f"{i}: article-level rule: refs must be all paragraphs of {a}; missing {sorted(set(allp)-set(m['refs']))}")
        if a in covered_arts or a in prop_arts: E(f"{i}: article {a} already has a measure (one article, one measure)")
        prop_arts.add(a)
    for f in m.get('fiscal_rows',[]):
        if f not in rows: E(f"{i}: unknown row {f}")
        elif rows[f]['match_status']=='matched': E(f"{i}: row {f} already matched to {rows[f]['measure']}")
        if f in assigned: E(f"{f}: assigned twice ({assigned[f]}, {i})")
        assigned[f]=i
    for f in('thematic','ministry','relevance','low_priority','csr','profile'):
        if m.get(f) is not None: E(f"{i}: {f} must be null at seeding")
    if not all(x in m.get('lineage',{}) for x in('merged_from','split_from','note')): E(f"{i}: lineage keys")
ra=p.get('row_assignments',{})
if ra!=assigned: E(f"row_assignments differ from measures[].fiscal_rows: {sorted(set(ra.items())^set(assigned.items()))[:6]}")
unrec=p.get('unreconciled_rows',[])
uids={u['id'] for u in d['uncertainties']}
for u in p.get('uncertainties',[]):
    if u['id'] in uids: E(f"{u['id']}: duplicate uncertainty id")
    if not all(k in u for k in('id','stage','text','raised','resolved','resolution')): E(f"{u['id']}: format")
print(f"measures {len(p['measures'])}, rows assigned {len(assigned)}, uncertainties {len(p.get('uncertainties',[]))}, unreconciled {len(unrec)}")
if errs:
    print('ERRORS'); [print(' -',e) for e in errs]; sys.exit(1)
print('VALID')
if apply:
    for m in p['measures']:
        d['measures'].append(m)
        for f in m['fiscal_rows']:
            rows[f]['measure']=m['id']; rows[f]['match_status']='matched'
    d['uncertainties'].extend(p.get('uncertainties',[]))
    open(law,'w',encoding='utf-8').write(json.dumps(d,ensure_ascii=False,indent=1)+'\n')
    print('APPLIED')
