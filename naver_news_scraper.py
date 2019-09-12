#2018.07.XX
# -*-coding:utf-8 -*-
# scraping news by query

from bs4 import BeautifulSoup
import json
import re
import os, sys
import requests
import time, random

def get_news(n_url):
    news_detail = []
    print(n_url)
    breq = requests.get(n_url)
    bsoup = BeautifulSoup(breq.content, 'html.parser')

    # parse html
    title = bsoup.select('h3#articleTitle')[0].text
    news_detail.append(title)

    # pdate
    pdate = bsoup.select('.t11')[0].get_text()[:11]
    news_detail.append(pdate)

    # news text
    _text = bsoup.select('#articleBodyContents')[0].get_text().replace('\n', " ")

    if '동영상 뉴스' in _text:
        pass
    else:
        btext = _text.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")
        news_detail.append(btext.strip())


    #pcompany
    pcompany = bsoup.select('#footer address')[0].get_text()
    news_detail.append(pcompany)

    return news_detail


def do_scrape(query, s_date, e_date):
    page = 1
    s_from = s_date.replace(".", "")
    e_to = e_date.replace(".", "")
    filename = query + s_date + '-' + e_date +'.txt'
    ofile = open(filename, 'w', encoding='utf-8')
    while page < 10**8:
        try:
            url = "https://search.naver.com/search.naver?where=news&query=" + query + "&sort=0&ds=" + s_date + "&de=" + e_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(page)

            header={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            }
            req = requests.get(url, headers=header)
            sys.stdout.write(url +'\n')
            cont = req.content
            soup = BeautifulSoup(cont, 'html.parser')
            #print(soup)
            for urls in soup.select("._sp_each_url"):
                if urls["href"].startswith("https://news.naver.com"):
                    if len(urls['href'].split('sid1=')) < 2 : continue
                    sid = urls['href'].split('sid1=')[1].split('&')[0]
                    if sid in ['106', '104', '107']: #Entertainment, Sports, and life&culture, respectively
                        continue
                    news_data = get_news(urls['href'])
                    #print(news_data)
                    if len(news_data) < 3 : continue
                    #pdate, title, btext, pcompany
                    ofile.write("{}\t{}\t{}\t{}\n".format(news_data[1], urls['href'], news_data[0], news_data[2]))
                    #ofile.write("{}\t{}\t{}\n".format(news_data[1], news_data[0], news_data[2]))
                    ofile.flush()
                    time.sleep(random.randint(0,3))
                else:
                    print(urls['href'])
            page += 10
            '''
            os.system('mv cur_end%s > pre_end%s' %(query, query))
            os.system('tail -n 3 %s > cur_end%s' %(filename,query))
            os.system('diff pre_end%s cur_end%s | wc -l > rst' %(query, query))
            with open('rst', 'r') as f:
                r=f.read().strip()
                if r =='0':
                    'No more scraped'
                    exit()
            '''
        except Exception as e:
            print(e)
    ofile.close()


query = "조현병"  # url 인코딩 에러는 parse.quote(query)
s_date = "2018.12.01"
e_date = "2018.12.31"

if __name__ == "__main__":
    try:
        if len(sys.argv) > 2 :
            do_scrape(sys.argv[1], sys.argv[2], sys.argv[3])
        else:
            do_scrape(query, s_date, e_date)
    except Exception as e:
        print(e)

