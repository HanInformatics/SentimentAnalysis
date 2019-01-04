# -*-coding:utf-8 -*-
# writer: uk960214@gmail.com, jek.cl.nlp@gmail.com
# date: 2018.12
# about: scrape 정신의학신문

from bs4 import BeautifulSoup
import requests
import re
import urllib

def scrape_urls(pages=10):
    full_urls=[]
    page = 1
    while page <= pages:
        try:
            print(page)
            url = 'http://www.psychiatricnews.net/news/articleList.html?page='+str(page)+'&total=359&sc_section_code=&sc_sub_section_code=&sc_serial_code=&sc_area=A&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=%BF%EC%BF%EF%C1%F5&sc_word2=&sc_andor=&sc_order_by=E&view_type=sm'
            html = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(html, 'html.parser')
            atable = soup.find('table', id = 'article-list')
            atitle = soup.find_all('td', class_ ='list-titles')
            artlist = []
            for t in atitle:
                tags = t('a')
                for tag in tags:
                    all_l = tag.get('href', None)
                    artlist.append(all_l)
            for l in artlist:
                urlstart = 'http://www.psychiatricnews.net/news/'
                l = urlstart + l
                full_urls.append(l)
            page += 1
        except Exception as e:
            print(e)
    return full_urls

def scrape_news(url, ofile, metafile):
    try:
        source = requests.get(url)
        source.encoding = 'euc-kr'
        html = source.text
        soup = BeautifulSoup(html, 'html.parser')
        atitle = soup.find('div', class_='headline border-box')
        acontent = soup.find('div', id = 'articleBody')
        t = atitle.text.strip()
        c = acontent.text.strip()
        if c == '' or t == '': return
        cc = c.replace('\r', '')
        #cc = c.replace('^m', '')
        cc = cc.replace('\n', '')
        tnc = [t,cc]
        ofile.write('%s\t%s\n' %(t, cc))
        metafile.write("%s\t%s\n" %(t, url))
        print('done', url)
    except Exception as e:
        print(e)

def scrape_pages(full_urls, filename):
    print('# of page urls:', len(full_urls))
    ofile = open(filename, 'w')
    metafile = open(filename +'.meta', 'w')
    n_doc = 0
    for u in full_urls:
        print('# doc', n_doc)
        scrape_news(u, ofile, metafile)
        n_doc += 1
    ofile.close()
    metafile.close()

if __name__ == "__main__":
    try:
        full_urls=scrape_urls(100)
        scrape_pages(full_urls, 'psynews.txt')
    except Exception as e:
        print(e)
