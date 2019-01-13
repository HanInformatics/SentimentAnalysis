#coding: utf-8
#writer: uk960214@gmail.com, jek.cl.nlp@gmail.com
#date:2018.12

import dataset

def initdb(dbname, tblname, pkey):
    try:
        db = dataset.connect('sqlite:///%s' %dbname)
        db.create_table(tblname, primary_id=pkey, primary_type=db.types.string(256))
    except Exception as e:
        print(e)

def list2db(dlist, dbname, tblname):
    try:
        db = dataset.connect('sqlite:///%s' %dbname)
        for data in dlist:
            db[tblname].upsert(data, ['url'])
    except Exception as e:
        print(e)

def tbl2txt(dbname, tblname, cols, ofn):
    db = dataset.connect('sqlite:///%s' %dbname)
    outfile = open(ofn, 'w', encoding='utf-8')
    records = db[tblname].all()
    for rec in records:
        item = []
        for col in cols:
            item.append(rec[col])
        outfile.write('%s\n' %('\t'.join(item)))
    outfile.close()

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
        if len(tab) > 2 :
            url = tab[2]
        else: url = ''
        record['url'] = url
        idx += 1
        db[tablename].upsert(record,['url'])

def tmp_f(infn):
    results = []
    with open(infn, 'r', encoding='utf-8') as infile:
        for l in infile:
            if l == '' : continue
            item = l.split('\t')
            if len(item) != 3: continue
            record = {'title':item[0], 'content':item[1], 'url':item[2]}
            results.append(record)
    return results




if __name__ == "__main__":
    try:
        #initdb('data/psydb.db', 'psynews', pkey='url')
        results=tmp_f('psynews.txt')
        list2db(results,'data/psydb.db', 'psynews')
        #txt2tbl('psynews.txt','data/psydb.db', 'psynews')
        tbl2txt('data/psydb.db', 'psynews', ['title', 'content'], 'psynews.body.txt')

    except Exception as e:
        print(e)
