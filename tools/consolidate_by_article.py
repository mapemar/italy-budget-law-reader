"""Rule (24/11/2026): one article, one measure. Consolidates measures of the same article into a single record.
Usage: python3 -I tools/consolidate_by_article.py data/lb-2027.json [--apply]
The record keeps the id of the first component; components are listed in lineage.merged_from and their text is kept in
description_en and lineage.note. refs = all paragraphs of the article; fiscal_rows = union."""
import json,sys,collections,re
path=sys.argv[1]; apply='--apply' in sys.argv
d=json.load(open(path,encoding='utf-8'))
A={a['number']:a for a in d['articles']}
par=collections.defaultdict(list)
for p in d['paragraphs']: par[p['article']].append(p['id'])
def art_of(m):
    s={r.split('-')[0] for r in m['refs']}
    assert len(s)==1,(m['id'],s); return next(iter(s))
groups=collections.OrderedDict()
for m in d['measures']: groups.setdefault(art_of(m),[]).append(m)
new=[];mapping={}
for a,ms in groups.items():
    n=int(a[1:]); first=ms[0]
    allp=[p['id'] for p in A[n]['paragraphs']] if isinstance(A[n]['paragraphs'][0],dict) else list(A[n]['paragraphs'])
    rows=[f for m in ms for f in m['fiscal_rows']]
    if len(ms)==1:
        r=dict(first); r['refs']=allp; new.append(r); mapping[first['id']]=first['id']; continue
    comps=' '.join(f"({i}) [{m['id']}] {m['title_en']}. {m['description_en']}" for i,m in enumerate(ms,1))
    notes=' '.join(f"[{m['id']}] {m['lineage']['note']}" for m in ms)
    merged=sorted({x for m in ms for x in ([m['id']] if m is not first else [])+m['lineage'].get('merged_from',[])})
    r=dict(first)
    r.update(title_en=f"Article {n}: {A[n]['heading_en']}",description_en=f"Article-level record with {len(ms)} components. {comps}",
             refs=allp,fiscal_rows=rows,seed='merge',
             lineage={'merged_from':merged,'split_from':None,'note':f"Article-level rule (24/11/2026): one article, one measure. Combines {', '.join(m['id'] for m in ms)} (earlier seeded separately; evidence per component follows). {notes}"})
    new.append(r)
    for m in ms: mapping[m['id']]=first['id']
print(len(d['measures']),'->',len(new),'records'); print({k:v for k,v in mapping.items() if k!=v})
if apply:
    ids={m['id'] for m in new}
    for f in d['fiscal_rows']:
        if f.get('measure'): f['measure']=mapping[f['measure']]
    d['measures']=new
    mp='; '.join(f"{k}->{v}" for k,v in mapping.items() if k!=v)
    d['uncertainties'].append({"id":f"U{max(int(u['id'][1:]) for u in d['uncertainties'])+1:03d}","stage":"b2","text":"Article-level rule (24/11/2026): one article, one measure. Measure ids merged into the first component of each article: "+mp+". Earlier uncertainties and the files in work/batches/ refer to the previous ids; lineage.merged_from gives the mapping. Classification (thematic area, ministry, CSR) will be assigned once per article, using primary and secondary fields for mixed articles.","raised":"24/11/2026","resolved":"24/11/2026","resolution":"Mapping recorded here and in lineage."})
    open(path,'w',encoding='utf-8').write(json.dumps(d,ensure_ascii=False,indent=1)+'\n'); print('APPLIED')
