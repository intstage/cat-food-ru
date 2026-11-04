"""Merge compositions, prices and countries into data.json with scores.

Usage: python3 -I src/build.py data data/data.json
"""
import json, os, sys, glob

S = sys.argv[1]
OUT = sys.argv[2]
det = {d['id']: d for d in json.load(open(f'{S}/petshop/details.json'))}
comp = {c['id']: c for c in json.load(open(f'{S}/compositions.json'))}
countries = {int(k): v for k, v in json.load(open(f'{S}/countries.json')).items()}

SHOPS = {
    'petshop': 'Petshop', 'ozon': 'Ozon', 'yamarket': 'Яндекс Маркет', '4lapy': 'Четыре Лапы',
    'wildberries': 'Wildberries', 'zoozavr': 'Зоозавр', 'beethoven': 'Бетховен', 'magizoo': 'Магизоо', 'zooopttorg': 'ЗооОптТорг',
}
# Typical values used when a label omits moisture, ash or fibre.
DEF = {'dry': {'moist': 10, 'ash': 7, 'fiber': 3}, 'wet': {'moist': 80, 'ash': 2.2, 'fiber': 0.5}}
DATE = '2026-11-04'


def lin(x, lo, hi, pts):
    t = (x - lo) / (hi - lo)
    return round(max(0.0, min(1.0, t)) * pts, 1)


def shop_offers():
    res = {}
    for d in det.values():
        offs = [{'weight_g': v['w'], 'price_rub': v['price'][0], 'in_stock': (v['avail'] or 0) > 0,
                 'url': f"https://www.petshop.ru/catalog/{d['slug']}/?oid={v['id']}"}
                for v in d['variants'] if v['w'] and v['price'] and v['price'][0]]
        res.setdefault(d['id'], {})['petshop'] = {'offers': offs, 'note': 'цена для Санкт-Петербурга'}
    for f in glob.glob(f'{S}/prices/*.json'):
        shop = os.path.basename(f)[:-5]
        if shop not in SHOPS:
            continue
        try:
            rows = json.load(open(f))
        except Exception as e:
            print('skip', f, e)
            continue
        for r in rows:
            offs = [o for o in (r.get('offers') or []) if o.get('weight_g') and o.get('price_rub')]
            if r.get('found') and offs:
                offs = [{**o, 'url': o.get('url') or r.get('url')} for o in offs]
                res.setdefault(r['id'], {})[shop] = {'offers': offs, 'note': (offs[0].get('price_note') or r.get('note'))}
    return res


def best_unit(offers):
    """Cheapest price per 100 g, preferring packs in stock. Returns (unit, offer, in_stock)."""
    def pick(pool):
        best = None
        for o in pool:
            u = o['price_rub'] / o['weight_g'] * 100
            if best is None or u < best[0]:
                best = (u, o)
        return best
    in_stock = [o for o in offers if o.get('in_stock') is not False]
    b = pick(in_stock)
    if b:
        return b + (True,)
    b = pick(offers)
    return b + (False,) if b else None


def score(c, ster, has, pdm, fdm, cdm):
    sc = {}
    sc['protein'] = lin(pdm, 28, 55, 30) if has else 0
    src = {'named_meat': 20, 'generic_meat': 9, 'plant': 0}.get(c['first_ingredient_type'], 0)
    if c['has_plant_protein_isolate']:
        src -= 6
    if c['has_sugar_or_artificial']:
        src -= 5
    sc['source'] = max(0, src)
    sc['carbs'] = lin(-cdm, -45, -5, 15) if has else 0
    tr = {'full': 6, 'partial': 4, 'generic': 1}.get(c['composition_disclosed'], 0)
    tr += {True: 4, None: 2, False: 0}[c['complete_feed']]
    sc['transparency'] = tr
    if has:
        lo, hi = (10, 16) if ster == 'steril' else (14, 24)
        pen = (fdm - hi) * 1.0 if fdm > hi else ((lo - fdm) * 1.5 if fdm < lo else 0)
        sc['fit'] = round(max(0, 10 - pen), 1)
    else:
        sc['fit'] = 0
    return sc


def item(i, d, c, offers):
    kind, ster = d['seg'].split('_')
    df = DEF[kind]
    est = []
    moist = c['moisture'] if c['moisture'] is not None else (est.append('влага') or df['moist'])
    ash = c['ash'] if c['ash'] is not None else (est.append('зола') or df['ash'])
    fib = c['fiber'] if c['fiber'] is not None else (est.append('клетчатка') or df['fiber'])
    p, f = c['protein'], c['fat']
    dm = 100 - moist
    has = p is not None and f is not None
    pdm = p / dm * 100 if has else None
    fdm = f / dm * 100 if has else None
    nfe = max(0.0, 100 - p - f - fib - ash - moist) if has else None
    cdm = nfe / dm * 100 if has else None
    kcal = c['kcal_per_100g'] or (round(3.5 * p + 8.5 * f + 3.5 * nfe) if has else None)
    shops = {}
    for sh, v in offers.get(i, {}).items():
        b = best_unit(v['offers'])
        if b:
            shops[sh] = {'unit100': round(b[0], 1), 'pack_g': b[1]['weight_g'], 'pack_price': b[1]['price_rub'],
                         'url': b[1].get('url'), 'note': v.get('note'), 'in_stock': b[2],
                         'offers': [{'g': o['weight_g'], 'rub': o['price_rub']} for o in v['offers']]}
    avail = {k: v for k, v in shops.items() if v['in_stock']} or shops
    best = min(avail.items(), key=lambda kv: kv[1]['unit100']) if avail else None
    co = countries.get(i, {})
    return {
        'id': i, 'name': c['name'], 'brand': d['brand'], 'title': d['title'], 'kind': kind, 'steril': ster == 'steril',
        'country': co.get('country'), 'country_verified': co.get('verified'), 'origin': 'RU' if co.get('country') == 'Россия' else 'IMP',
        'top5': c['ingredients_top5'], 'first': c['first_ingredient_type'], 'meat_share': c['meat_share_pct'],
        'grain_free': c['grain_free'], 'plant_isolate': c['has_plant_protein_isolate'], 'sugar': c['has_sugar_or_artificial'],
        'disclosed': c['composition_disclosed'], 'complete': c['complete_feed'], 'notes': c['notes'],
        'p': p, 'f': f, 'fib': c['fiber'], 'ash': c['ash'], 'moist': c['moisture'], 'ca': c['calcium'], 'ph': c['phosphorus'], 'mg': c['magnesium'],
        'pdm': round(pdm, 1) if has else None, 'fdm': round(fdm, 1) if has else None, 'cdm': round(cdm, 1) if has else None,
        'kcal': kcal, 'kcal_est': not c['kcal_per_100g'] and has, 'est': est, 'has_analysis': has,
        'scores': score(c, ster, has, pdm, fdm, cdm), 'shops': shops,
        'best_shop': best[0] if best else None, 'best100': best[1]['unit100'] if best else None,
        'ps_rating': d.get('rating'), 'ps_reviews': d.get('ratingCount'),
    }


def main():
    offers = shop_offers()
    items = [item(i, d, comp[i], offers) for i, d in det.items()]
    for kind in ('dry', 'wet'):
        grp = sorted([x for x in items if x['kind'] == kind and x['best100']], key=lambda x: x['best100'])
        n = len(grp)
        for r, x in enumerate(grp):
            x['scores']['price'] = round(15 * (1 - r / (n - 1)), 1) if n > 1 else 7.5
        for x in items:
            if x['kind'] == kind and not x['best100']:
                x['scores']['price'] = 0
    for x in items:
        s = x['scores']
        x['quality'] = round((s['protein'] + s['source'] + s['carbs'] + s['transparency'] + s['fit']) / 85 * 100)
        x['total'] = round(sum(s.values()))
        x['p300'] = round(x['best100'] * 3) if x['best100'] else None
        x['p1500'] = round(x['best100'] * 15) if x['best100'] else None
    json.dump({'items': items, 'shops': SHOPS, 'date': DATE}, open(OUT, 'w'), ensure_ascii=False)
    cov = {sh: sum(1 for x in items if sh in x['shops']) for sh in SHOPS}
    print('items', len(items), 'coverage', cov)
    for x in sorted(items, key=lambda x: -x['total'])[:8]:
        print(x['total'], x['quality'], x['name'], x['best100'])


if __name__ == '__main__':
    main()
