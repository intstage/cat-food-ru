import os,sys,re,json
sys.path.insert(0,os.path.dirname(__file__))
import unify
P=os.environ.get('DATA_DIR','data')
skus=json.load(open(P+'/skus.json'))
LAPY={
1018:r'royal canin sterilised 37',
121825:r'pro plan.*sterilised adult renal plus.*с кроликом',
87137:r'grandorf holistic adult sterilised сухой корм для стерилизованных кошек, с индейкой',
75740:r'monge sterilised сухой корм для стерилизованных кошек с пониженным содержанием калорий, с курицей',
74040:r'perfect fit сухой корм для стерилизованных кошек, с курицей, (1,2 кг|5 кг)',
79071:r'farmina nd prime сухой корм для стерилизованных кошек, с курицей и гранатом',
47273:r'whiskas сухой корм для стерилизованных кошек старше 1 года, с курицей',
116385:r'брит kea sterilised сухой корм для профилактики мкб',
1004:r'royal canin indoor 27',
13741:r'pro plan.* delicate digestion сухой корм для взрослых кошек.*индейки',
87112:r'grandorf holistic adult indoor.*четыре вида мяса',
92788:r'felix сухой корм для взрослых кошек мясное объедение, с говядиной',
79063:r'farmina nd prime сухой корм для кошек, с курицей и гранатом',
100584:r'pro plan.*sterilised maintenance влажный корм \(пауч\) для взрослых стерилизованных кошек, с говядиной в соусе',
108800:r'royal canin sterilised влажный корм \(пауч\) для стерилизованных кошек, в соусе',
129460:r'perfect fit влажный корм для стерилизованных кошек, паштет с индейкой',
102252:r'брит премиум влажный корм \(пауч\) для взрослых стерилизованных кошек, с цыпленком в соусе',
121822:r'pro plan.*maintenance влажный корм \(пауч\) для взрослых кошек, с уткой в соусе',
94403:r'whiskas влажный корм \(пауч\) для кошек, рагу с индейкой и кроликом',
81014:r'гурмэ.*желе де-люкс, с курицей в желе',
108796:r'royal canin instinctive влажный корм \(пауч\) для кошек в возрасте от 1 года до 7 лет, мелкие кусочки в соусе',
130438:r"nature.s table влажный корм \(пауч\) для кошек, говядина в соусе",
130520:r'crave влажный корм \(пауч\) полнорационный.*с говядиной',
}
ZOO={
1018:r'royal canin sterilised 37 (?!.*(котят|влажн))',
121825:r'pro plan renal plus с кроликом',
87137:r'grandorf для стерилизованных индейка',
75740:r'monge курица стерилизованных',
112659:r'savita для стерилизованных сухой беззерновой с форелью',
97304:r'florida.*(лосось-черника|sterilised с лососем и черникой)',
127215:r'karmy sterilized для стерилизованных индейка',
79071:r'farmina nd курица с гранатом стерилизованных',
1004:r'royal canin indoor 27',
13741:r'корм сухой для кошек pro plan delicate digestion с индейкой$',
104233:r'savita для взрослых сухой беззерновой с лососем и белой рыбой',
87112:r'grandorf (4 вида мяса|четыре мяса)$',
100584:r'pro plan maintenance с говядиной в соусе для стерилизованных',
108800:r'royal canin sterilised соус стерилизованных пауч',
111024:r'florida для стерилизованных и кастрированных котов кусочки говядина желе',
129855:r'savita с уткой и овощами в соусе',
129218:r'karmy sterilized.*лосось в желе',
121822:r'pro plan maintenance с уткой в соусе$',
103658:r'florida с чувствительным пищеварением кусочки индейка морковь в соусе',
81014:r'гурмэ желе де-люкс с курицей в желе',
108796:r'royal canin instinctive соус пауч',
78136:r'monge cat grill итальянский кролик пауч',
}
sid_ex={13741:r'предпочтениями|с индейкой и рисом'}
def build(shop,spec,items):
    out=[]
    for s in skus:
        rx=spec.get(s['id'])
        matched=[g for g in items if rx and re.search(rx,g['title'],re.I)] if rx else []
        if not matched:
            out.append({'id':s['id'],'shop':shop,'found':False,'matched_title':None,'url':None,'offers':[],'checked_at':'2026-11-04','note':'not sold / no exact match'}); continue
        by={}
        for g in matched:
            for o in g['offers']:
                if o['weight_g'] is None: continue
                if shop=='4lapy' and sid_ex.get(s['id']) and re.search(sid_ex[s['id']],o['name'],re.I): continue
                k=o['weight_g']
                if k not in by or (o['in_stock'] and not by[k]['in_stock']) or (o['in_stock']==by[k]['in_stock'] and o['price_rub']<by[k]['price_rub']): by[k]=o
        offers=[{'weight_g':w,'price_rub':o['price_rub'],'old_price_rub':o['old_price_rub'] if (o['old_price_rub'] or 0)>o['price_rub'] else None,'in_stock':o['in_stock']} for w,o in sorted(by.items())]
        if shop=='zoozavr':
            for of,(w,o) in zip(offers,sorted(by.items())): of['url']=o.get('url')
        m0=matched[0]
        out.append({'id':s['id'],'shop':shop,'found':True,'matched_title':' || '.join(g['title'] for g in matched) if len(matched)>1 else m0['title'],'url':m0['url'] if shop=='4lapy' else sorted(by.items())[0][1].get('url'),'offers':offers,'checked_at':'2026-11-04'})
    return out
for shop,spec,items in [('4lapy',LAPY,unify.load_lapy()),('zoozavr',ZOO,unify.load_zoo())]:
    res=build(shop,spec,items)
    json.dump(res,open(f'{P}/prices/{shop}.json','w'),ensure_ascii=False,indent=1)
    print(shop,sum(r['found'] for r in res),'/',len(res))
    for r in res:
        if r['found']: print(r['id'],r['matched_title'][:100],[(o['weight_g'],o['price_rub']) for o in r['offers']])
