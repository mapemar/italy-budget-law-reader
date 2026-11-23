import json,re,subprocess,sys
pdf,ref=sys.argv[1],sys.argv[2]
t=subprocess.run(['pdftotext','-f','29','-l','31','-layout','-nopgbrk',pdf,'-'],capture_output=True,text=True,check=True).stdout
t=t.replace('\u0002','-').replace('­','')
lines=[l.strip() for l in t.splitlines()]
lines=[l for l in lines if l and not re.match(r'^11124/26\s+\d+$',l) and not l.startswith('ECOFIN 1A/LIFE')]
body=' '.join(lines)
body=re.sub(r'(\w)- (\w)',lambda m:m.group(0),body)
body=re.sub(r'\s+',' ',body)
s=body.index('HEREBY RECOMMENDS')
e=body.index('Done at Brussels')
op=body[s:e]
head=op[:op.index('1. Ensure')].strip()
parts=re.split(r'(?<=[\.\s])(?=[2-6]\. [A-Z])',op[op.index('1. Ensure'):])
recs=[]
for i,p in enumerate(parts,1):
    p=p.strip(); assert p.startswith(f'{i}. '),p[:30]
    recs.append(p[3:].strip())
assert len(recs)==6
print(head)
for r in recs: print(len(r),r[:70],'...',r[-50:])
d=json.load(open(ref,encoding='utf-8'))
f=d['csr_framework']
f['recommendations']=[{"id":f"CSR2026-{i}","number":i,"title":None,"text":r,"subcategories":[]} for i,r in enumerate(recs,1)]
f['status']='loaded (recommendations); subcategories pending approval'
f['source'].update({"provided_by":"User, in the Project (file 'CSR 2026.pdf')","date":"03/07/2026","note":"Council of the EU document 11124/26 (ECOFIN 914), 'Council Recommendation on the economic, social, employment, structural and budgetary policies of Italy', based on COM(2026) 212 final. Operative text (recommendations 1-6) loaded programmatically from the PDF, pp. 29-31, verbatim apart from line-break and hyphenation normalisation. Titles and subcategories are not part of the source and are left empty until proposed and approved."})
json.dump(d,open(ref,'w',encoding='utf-8'),ensure_ascii=False,indent=1);open(ref,'a').write('\n')
