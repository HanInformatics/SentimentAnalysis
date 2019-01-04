#coding: utf-8
#writer: 요욱
#date:2018.12

import dataset

def txt2tbl(fn, dbname, tablename):
    db = dataset.connect('sqlite:///%s' %dbname)
    infile = open(fn, 'r', encoding='utf-8')
    lines = infile.readlines()
    infile.close()
    idx = 0
    record = {}
    for l in lines:
        tab = l.split('\t')
        record['title'] = tab[0]
        record['content'] = tab[1]
        if len(tab) > 2 : record['url'] = tab[2]
        record['idx'] = idx
        idx += 1
        db[tablename].upsert(record,['idx'])
if __name__ == "__main__":
    try:
        txt2tbl('psynews.txt', 'newsdb', 'psynews')
    except Exception as e:
        print(e)
