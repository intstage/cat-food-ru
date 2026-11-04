import json,re
import os; P=os.path.join(os.environ.get('DATA_DIR','data'),'prices')
def wparse(t):
    t=t.lower().replace(',','.')
    m=re.search(r'(\d+(?:\.\d+)?)\s*\*\s*(\d+)\s*(?:шт)',t)  # multipack
    m2=re.findall(r'(\d+(?:\.\d+)?)\s*(кг|гр\.?|г|kg)\b',t)
    if not m2: return None
    v,u=m2[-1] if len(m2)==1 else m2[0]
    v=float(v); return int(round(v*1000)) if u in('кг','kg') else int(round(v))
def load_lapy():
    d=json.load(open(P+'/4lapy_candidates.json')); seen={}
    for b,items in d.items():
        for i in items: seen[i['url']]=i
    out=[]
    for i in seen.values():
        offs=[]
        for o in i['offers']:
            if o['price'] is None: continue
            if re.search(r'в подарок|\+\s*\d',o['name'],re.I): continue
            w=o['w']; 
            if isinstance(w,str): w=wparse(w)
            if w is None: w=wparse(o['name'])
            offs.append({'weight_g':w,'price_rub':o['price'],'old_price_rub':o['old'] or None,'in_stock':o['avail'],'name':o['name']})
        out.append({'title':i['name'],'url':'https://4lapy.ru'+i['url'],'offers':offs})
    return out
def load_zoo():
    d=json.load(open(P+'/zoozavr_candidates.json')); seen={}
    for b,items in d.items():
        for i in items: seen[i['id']]=i
    groups={}
    for i in seen.values():
        t=i['title']; w=wparse(t)
        key=re.sub(r'\s*\d+(?:[.,]\d+)?\s*(?:кг|гр?\.?)\b','',t,flags=re.I)
        key=re.sub(r'\s+',' ',key).strip()
        old=i['old']['price'] if isinstance(i['old'],dict) else i['old']
        g=groups.setdefault(key,{'title':key,'url':i['url'],'offers':[]})
        g['offers'].append({'weight_g':w,'price_rub':i['price'],'old_price_rub':old,'in_stock':i['avail']=='AVAILABLE','name':t,'url':i['url']})
    return list(groups.values())
