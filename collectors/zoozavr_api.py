import urllib.request,urllib.parse,json,time,sys
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/130 Safari/537.36'
B='https://api.zoozavr.ru/v2/products/new'
def get(search=None,extra='',limit=36,offset=0,sort=None,meta=True):
    q=[('filter','site:zoozavr;withregion:RU-MOW'+extra),('limit',limit),('offset',offset)]
    if search: q.append(('search',search))
    if sort: q.append(('sort',sort))
    if meta: q.append(('meta','*'))
    url=B+'?'+urllib.parse.urlencode(q,safe=':;[]')
    r=urllib.request.Request(url,headers={'User-Agent':UA,'Origin':'https://zoozavr.ru','Referer':'https://zoozavr.ru/'})
    return json.load(urllib.request.urlopen(r,timeout=40))
if __name__=='__main__':
    for s in sys.argv[1:]:
        d=get(s,limit=8,sort=None)
        print(s,d['meta'].get('length'),[x['title'][:55] for x in d['items']]);time.sleep(0.6)
