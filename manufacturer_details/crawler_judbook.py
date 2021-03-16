# coding=utf-8
import json,datetime,time,os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By as BY
from selenium.webdriver.support import ui as UI
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from crawler_lib import *
from crawler_ref import logpath,path


def getfilelist(downloadaddr):
    '''
    '''
    result = []
    filelist = os.listdir(downloadaddr)
    for i in filelist:
        i = i.split('.')
        if i[1] == 'pdf':
            result.append(i[0])
    return result




if __name__ == '__main__':


    companylist = getAllDir(path,os.listdir(path))
    # get detail from supplierlist.json
    companys = getDetail(path + 'supplierlist.json')
    
    for i in companys :

        seq = str(i['Seq'])
        name = i['Name']
        # mkdir sequence dir
        if seq not in companylist:
            os.mkdir(path + seq)

        url = "https://law.judicial.gov.tw/FJUD/Default.aspx"
        downloadaddr = path +'{}\\'.format(seq)
        filelist = getfilelist(downloadaddr)

        try:
            # init selenium
            driver = initSelenium(proxy=None,downloadaddr=downloadaddr,debugmode=False)
            # get url 
            driver.get(url)
            a
            UI.WebDriverWait(driver,15).until(lambda driver: driver.find_element_by_id('txtKW'))
            # key in company name
            driver.find_element_by_id('txtKW').send_keys(name)
            # submit
            driver.find_element_by_id('btnSimpleQry').click()
            # get hidden qid
            UI.WebDriverWait(driver,15).until(lambda driver: driver.find_element_by_id('hidQID'))
            qid = driver.find_element_by_id('hidQID').get_attribute('value')
            # get count of judbook
            url = 'https://law.judicial.gov.tw/controls/GetResultCount.ashx?ty=JUDBOOK&q={}'.format(qid)
            driver.get(url)
            # get result in html and turn to json obj
            count = int(json.loads(driver.find_element_by_tag_name('body').text)['Total'])

            for j in range(count):
                # get judbook
                url = 'https://law.judicial.gov.tw/FJUD/data.aspx?ro={}&q={}'.format(j,qid)
                driver.get(url)
                # get title,date,reason
                UI.WebDriverWait(driver,15).until(lambda driver: driver.find_element_by_class_name('col-td'))
                title = driver.find_elements(BY.CLASS_NAME,'col-td')[0].text.replace(' ','')
                date = driver.find_elements(BY.CLASS_NAME,'col-td')[1].text.replace(' ','').replace('年','/').replace('月','/').replace('日','/').replace('民國','')[:-1]
                reason = driver.find_elements(BY.CLASS_NAME,'col-td')[2].text.replace(' ','')

                if title not in filelist:

                    # hlExportPDF
                    UI.WebDriverWait(driver,15).until(lambda driver: driver.find_element_by_id('hlExportPDF'))
                    driver.find_element_by_id('hlExportPDF').click()
                    # sleep 1 sec wait download complete
                    time.sleep(1)
                    # get most new file
                    s = os.listdir(downloadaddr)
                    s.sort(key=lambda k: os.path.getmtime(downloadaddr+k) if not os.path.isdir(downloadaddr+k) else 0)
                    # rename file
                    os.rename(downloadaddr+s[-1],downloadaddr+title+'.pdf')

                    # read file
                    if os.path.exists(downloadaddr+'judiciallist.json'):
                        with open(downloadaddr+'judiciallist.json','r',encoding='utf-8') as f:
                            data = json.load(f)
                    else :
                        data = []
                    
                    data.append({"Title": title,"Date": date,"Reason": reason,"FileName": title+".pdf"})

                    with open(downloadaddr+'judiciallist.json','w',encoding='utf-8') as f:
                        data = json.dump(data,f,ensure_ascii=False)

                    # use url get
                    # url = driver.find_element_by_id('hlExportPDF').get_attribute('href')
                    # url = url.split('fname=')[0]+'fname='+urllib.quote(filename)
                    # driver.get(url)

                    go2log(logpath,'[getjudbookOK]'+name+'-'+title+' download complete!')
                    print(name,'-',title,' download complete!')
                time.sleep(2)

            driver.quit()
            time.sleep(1)

        except Exception as e:
            try:
                driver.quit()
                time.sleep(1)
            except:
                pass
            go2log(logpath,'[getjudbookERR]{}'.format(seq)+ str(e))



    