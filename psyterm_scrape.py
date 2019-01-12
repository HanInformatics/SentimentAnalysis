# -*-coding:utf-8 -*-
# writer: jek.cl.nlp@gmail.com
# date: 2018.12
# about: scrape 국가건강정보포털 의학정보:정신건강의학과 용어 from urls.txt

from bs4 import BeautifulSoup
import requests
import pdb
import json

def scrape_a_page(url, term=''):
    term_content =[]
    #pdb.set_trace()
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    #if term != '', term == headword
    try:
        headword=soup.find('h2', class_='headword').get_text(strip=True)
    except Exception as e:
        print(e)

    try:
        engword=soup.find('span', class_='u_word_dic').get_text(strip=True)
    except Exception as e:
        engword =''
        print(e)

    try:
        summarytext=soup.find('dl', class_='summary_area').get_text(strip=True)
        if summarytext[0:2] == '요약':
            summarytext = summarytext[2:] #remove the very first '요약'
    except Exception as e:
        summarytext=''
        print(e)

    try:
        sub_texts = []
        sub_list = soup.find_all('h3', class_='stress')
        for sub in sub_list:
            subtitle = sub.get_text()
            sub_ptxt=[]
            while True:
                nsub=sub.find_next('p')
                nhsub=sub.find_next('h3').find_next('p')
                if nsub != nhsub:
                    sub_ptxt.append(nsub.get_text())
                else:
                    break
                sub = nsub
            sub_texts.append((subtitle, sub_ptxt))

        return((headword, engword, summarytext, sub_texts))
    except Exception as e:
        print(e)
        return

def scrape_term_url(fn):
    infile = open(fn, 'r', encoding='utf-8')
    lines = infile.readlines()
    infile.close()

    import os
    if not os.path.exists('data'):
        os.mkdir('data')

    t_u = []
    for l in lines:
        tu = l.strip().split('\t')
        if len(tu) < 2 : continue
        a_term_content=scrape_a_page(tu[1], tu[0])

        ofile = open('data/'+ a_term_content[0], 'w', encoding='utf-8')
        ofile.write('headword:%s\n' %a_term_content[0])
        ofile.write('engword:%s\n' %a_term_content[1])
        ofile.write('summary:%s\n' %a_term_content[2])

        for sub in a_term_content[3]: #sub_texts
            ofile.write('subtitle-%s:' %sub[0])
            ofile.write('%s\n' %(' '.join(sub[1]))) #sub_ptxt
        ofile.close()

if __name__ == "__main__":
    try:
        scrape_term_url('urls.txt')
    except Exception as e:
        print(e)

