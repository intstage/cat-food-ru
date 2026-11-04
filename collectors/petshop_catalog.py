import json,sys,subprocess,time
def get(url):
    return json.loads(subprocess.run(['curl','-s','-m','40','-A','Mozilla/5.0',url],capture_output=True,text=True).stdout)
res={}
for kind,cid in [('dry',930),('wet',931)]:
    items=[];page=1
    while True:
        d=get(f'https://www.petshop.ru/api/v4/site/catalog/products/?cityId=22&categoryId={cid}&page={page}&p=')
        prods=d.get('products') or []
        if not prods: break
        items+=prods
        if page==1: print(kind,'total',d.get('totalCount'),flush=True)
        if len(items)>=d.get('totalCount',0) or page>60: break
        page+=1; time.sleep(0.4)
    for p in items:
        p.pop('thumbnails',None);p.pop('thumbnailAlts',None)
        for v in p.get('variants',[]): v.pop('thumbnails',None);v.pop('thumbnailAlts',None)
    res[kind]=items; print(kind,len(items))
json.dump(res,open(sys.argv[1],'w'),ensure_ascii=False)
