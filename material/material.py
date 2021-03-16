# coding=utf-8
from pyquery import PyQuery as pq
import json,time,datetime


def initPQ(url):
    '''
    init pyquery and get url 
    '''
    # pyquery
    doc = pq(url=url,encoding='big5')
    return doc


def getInfo(doc):
    '''
    get information data in https://fubon-ebrokerdj.fbs.com.tw/z/ze/zeq/zeq.djhtm
    凱基原物料報價網
    '''
    table = doc('table[class=t01]')
    industry = table('td[class=t3t]').text().split(' ')
    dictinfo = []
    for i in range(len(industry)):
        column = table('td[class=t3t]').eq(i).next().children()
        j = 0
        while 1:
            if len(column.eq(j)) != 0:
                name = column.eq(j).text().replace('【','').replace('】','')
                A = column.eq(j).attr('href').split('zeqa_')[1].split('.')[0]
                dictinfo.append({'IndustryCode':chi2Num(industry[i]),'Industry':industry[i],'CategoryCode':chi2Num(name),'Category':name,'A':A})
                j += 1
            else : 
                break
    return dictinfo



def chi2Num(chi):
    '''
    根據中文字產生唯一code(可選)
    '''
    n = ''
    for i in chi:
        n += str(ord(i))
    if len(n) < 6:
        n = '00000' + n
    return n






if __name__ == "__main__":

    # new_result = []
    url = "https://fubon-ebrokerdj.fbs.com.tw/z/ze/zeq/zeq.djhtm"
    doc = initPQ(url)
    # get all data
    results = getInfo(doc)

    for i in range(len(results)):

        url = "https://fubon-ebrokerdj.fbs.com.tw/Z/CZHG.djbcd?A=" + results[i]['A']
        doc = initPQ(url).text().split(' ')
        
        # date_n = doc[0].split(',')
        # value_n = doc[1].split(',')
        # get record date
        results[i]['RecordDate'] = doc[0].split(',')[-1]
         # get value
        results[i]['Price'] = doc[1].split(',')[-1]
        
        url = 'https://fubon-ebrokerdj.fbs.com.tw/z/ze/zeq/zeqa_' + results[i]['A'] + '.djhtm'
        doc = initPQ(url).text().split("'Unit': ")[1].split(',')[0]
        # get currency and unit
        currency = doc.split('/')[0].split('"')[1]
        try:
            unit = doc.split('/')[1].split(' Y')[0]
        except:
            unit = currency.split(' Y')[0]
            currency = 'null'

        currency = currency.split(' ')
        results[i]['Currency'] = currency[0]
        try:
            results[i]['ChargeUnit'] = currency[1]
        except:
            results[i]['ChargeUnit'] = 'null'
        results[i]['Unit'] = unit

        '''
        if you want get all data ,not only today data ,open it
        '''
        # if len(date_n) == len(value_n):
        #     for j in range(len(date_n)):
        #         new_r = {}
        #         new_r = results[i]
        #         new_r['RecordDate'] = date_n[j]
        #         new_r['Price'] = value_n[j]
        #         new_result.append(new_r)
        #         # print(new_r)

        #         file = './{}.json'.format('allallall')
        #         with open(file,'a',encoding="utf-8") as file:
        #             json.dump(new_result, file,ensure_ascii=False)
        # else :
        #     print(results[i]['Category'], '  ERROR')

        # delete useless info
        del results[i]['A']

    file = 'D:\\WebSite\\ITTS-EP-FRONTSITE\\wwwroot\\TrendRecord\\Price\\{}.json'.format(datetime.date.today().strftime("%Y%m%d"))
    # file = './{}.json'.format(datetime.date.today().strftime("%Y%m%d"))
    with open(file,'w',encoding="utf-8") as file:
        json.dump(results, file,ensure_ascii=False)