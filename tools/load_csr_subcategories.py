"""Load approved CSR 2026 titles and subcategories (id, label, scope) from the proposal markdown into reference.json."""
import json,re,sys
md,ref=sys.argv[1],sys.argv[2]
t=open(md,encoding='utf-8').read()
titles=dict(re.findall(r'^## CSR2026-(\d) – (.+)$',t,re.M))
subs={}
for m in re.finditer(r'^\*\*CSR2026-(\d+)\.(\d+) (.+?)\*\*\n((?:- .*\n?)+)',t,re.M):
    n,k,label,body=m.groups()
    sc=re.search(r'^- Scope: (.+)$',body,re.M).group(1).strip()
    subs.setdefault(int(n),[]).append({"id":f"CSR2026-{n}.{k}","label":label.strip(),"scope":sc})
orig=open(ref,encoding='utf-8').read()
d=json.loads(orig); f=d['csr_framework']
for r in f['recommendations']:
    n=r['number']; r['title']=titles[str(n)].strip(); r['subcategories']=subs[n]
f['status']='loaded'
f['source']['note']=f['source']['note'].replace("Titles and subcategories are not part of the source and are left empty until proposed and approved.","Titles and subcategories are not part of the source: they are an analytical structure proposed by the policy analyst (work/csr_subcategories_proposal.md) and approved by the user on 23/11/2026; each is anchored to words of the operative text.")
k=orig.index('"csr_framework":'); i=orig.index('{',k); depth=0
for j in range(i,len(orig)):
    if orig[j]=='{':depth+=1
    elif orig[j]=='}':
        depth-=1
        if depth==0:break
out=orig[:i]+json.dumps(f,ensure_ascii=False,indent=1).replace('\n','\n ')+orig[j+1:]
json.loads(out); open(ref,'w',encoding='utf-8').write(out)
print({n:len(v) for n,v in subs.items()},sum(len(v) for v in subs.values()))
