import urllib.request,urllib.parse,json,re,time,os,hashlib
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/130 Safari/537.36'
RAW=os.environ.get('RAW_DIR','data/raw/4lapy')
def fetch(query,page=1):
    key=hashlib.md5(f'{query}|{page}'.encode()).hexdigest()[:10]
    fn=f'{RAW}/q_{key}.json'
    if os.path.exists(fn): return json.load(open(fn))
    url='https://4lapy.ru/search/?'+urllib.parse.urlencode({'query':query,'page':page})
    r=urllib.request.Request(url,headers={'User-Agent':UA})
    h=None
    for attempt in range(4):
        try:
            h=urllib.request.urlopen(r,timeout=40).read().decode('utf-8'); break
        except urllib.error.HTTPError as e:
            if e.code==404: return {'query':query,'page':page,'total':0,'items':[]}
            time.sleep(2)
        except Exception:
            time.sleep(2)
    if h is None: raise RuntimeError('fetch failed '+url)
    m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',h,re.S)
    d=json.loads(m.group(1))
    fb=d['props']['pageProps']['fallback']
    res=None
    for k,v in fb.items():
        if k.startswith('/catalog/search'): res=v
    out={'query':query,'page':page,'total':res['meta']['total'] if res else 0,'items':(res or {}).get('items',[])}
    json.dump(out,open(fn,'w'),ensure_ascii=False)
    time.sleep(0.6)
    return out
def compact(it):
    offs=[]
    for o in it.get('offers',[]):
        w=None
        for a in o.get('snippetAttributes',[]):
            if a['code']=='weight_netto':
                for v in a['values']:
                    w=v.get('weightInGrams') or v.get('value')
        pr=o.get('price') or {}
        offs.append({'name':o['name'],'w':w,'price':pr.get('priceValue'),'old':pr.get('oldPriceValue'),'avail':o.get('available')})
    return {'name':it['name'],'url':it['url'],'brand':it.get('brandCode'),'offers':offs}
