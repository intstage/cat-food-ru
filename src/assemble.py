import json,sys,csv
S,OUTDIR=sys.argv[1],sys.argv[2]  # S: папка data, OUTDIR: корень сайта
d=json.load(open(f'{S}/data.json'))
t=open('src/template.html',encoding='utf-8').read().replace('/*DATA*/null',json.dumps(d,ensure_ascii=False))
open(f'{OUTDIR}/index.html','w',encoding='utf-8').write(t)
shops=list(d['shops'])
with open(f'{S}/korma-dlya-koshek.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f,delimiter=';')
    w.writerow(['id','Корм','Бренд','Тип','Стерил.','Страна','Страна проверена','Белок %','Жир %','Клетчатка %','Зола %','Влага %','Белок СВ %','Жир СВ %','Углеводы СВ %','Ккал/100г','1-й ингредиент','Без злаков','Качество','Итог','Мин ₽/100г','Магазин','₽ за 300 г','₽ за 1,5 кг']+[f'{d["shops"][s]} ₽/100г' for s in shops]+['Первые ингредиенты','Заметки'])
    for x in sorted(d['items'],key=lambda x:-x['total']):
        w.writerow([x['id'],x['name'],x['brand'],x['kind'],'да' if x['steril'] else 'нет',x['country'],x['country_verified'],x['p'],x['f'],x['fib'],x['ash'],x['moist'],x['pdm'],x['fdm'],x['cdm'],x['kcal'],x['first'],x['grain_free'],x['quality'],x['total'],x['best100'],d['shops'].get(x['best_shop'] or '',''),x['p300'],x['p1500']]+[(x['shops'].get(s) or {}).get('unit100') for s in shops]+[' | '.join(x['top5'] or []),x['notes']])
print('ok', len(t))
