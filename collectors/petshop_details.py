import json,sys,subprocess,time,re,html
SEL={'dry_steril':[1018,121825,87137,125931,75740,137202,112659,74040,76441,118590,97304,3732,79071,47273,127215,116385],
'dry_normal':[1004,13741,124284,125938,104233,87112,40107,137196,134145,114662,9186,92788,79063,9837,1074,96525],
'wet_steril':[100584,108800,111024,127153,129855,15545,81049,86634,78141,96486,129460,108218,129218,102252],
'wet_normal':[121822,103658,94403,129862,81014,108796,71428,87405,109663,130438,78136,130520,82275,46003]}
def txt(s): return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s or ''))).strip()
out=[]
for seg,ids in SEL.items():
    for i in ids:
        r=subprocess.run(['curl','-s','-m','40','-A','Mozilla/5.0',f'https://www.petshop.ru/api/v4/site/catalog/products/{i}/?cityId=22'],capture_output=True,text=True).stdout
        try: p=json.loads(r)['product']
        except Exception as e: print('ERR',i,e); continue
        out.append({'seg':seg,'id':i,'brand':p['brand']['name'],'title':p['title'],'slug':p['slug'],
          'rating':p.get('rating'),'ratingCount':p.get('ratingCount'),
          'ingredients':txt(p.get('ingredients')),'description':txt(p.get('description'))[:3000],
          'variants':[{'id':v['id'],'t':v['variantTitle'],'price':v['price'],'w':(v.get('packing') or {}).get('weight'),'avail':v.get('availableCount'),'comp':v.get('composition')} for v in p['variants']]})
        print(seg,i,p['brand']['name'],len(out[-1]['ingredients']),flush=True); time.sleep(0.3)
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
