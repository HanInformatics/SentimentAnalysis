#!/bin/sh

SOURCE=urls.txt
TERMS=terms.txt
awk -F "\t" '{print $1}' $SOURCE > $TERMS
echo "$TERMS is from $SOURCE"
#terms=`cat $TERMS`
echo $terms
SDATE="2018.12.01"
EDATE="2018.12.31"
#for each in $terms
while read each
do
    echo "The current term is \"$each\""
    echo "python3 naver_news_scraper.py \"$each\" $SDATE $EDATE &"
    python3 naver_news_scraper.py $each $SDATE $EDATE &
done < $TERMS







