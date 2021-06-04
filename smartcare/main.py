# coding=utf-8
# 桃園市私立長青老人長期照顧中心(養護型)

import json,datetime,time,os,math,json,csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By as BY
from selenium.webdriver.support import ui as UI
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from ref import *



def initSelenium(proxy=None):
    '''
    init selenium and setting options
    '''
    #selenium options setting
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument("--disable-infobars")
    # add proxy
    if proxy != None:
        chrome_options.add_argument('--proxy-server=http://{}'.format(proxy))

    driver = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
    #set browser loading timeout
    driver.set_page_load_timeout(120)

    return driver



# write log
def go2log(log_path, e):
    '''
    write info to logpath\r\n
    log_path:log path\r\n
    e:information\r\n
    '''
    time = datetime.datetime.now()
    with open(log_path, 'a', newline='',encoding='utf-8') as f:
        f.write('{} :{}\r\n'.format(time.strftime("%Y-%m-%d %H:%M:%S"), str(e)))



def waitForPage(driver):
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id("dataLoading"))
    time.sleep(1)
    while 1:
        w = driver.find_element_by_xpath("//div[@id='dataLoading']")
        if w.get_attribute("style").split('display: ')[1] == 'none;':
            return True
        else :
            time.sleep(1)



def loginPage(driver,login_page):
    '''
    login page
    '''
    #  enter account
    driver.get("{}".format(login_page))
    time.sleep(1)
    #  if alert box open it!!
    try:
        driver.switch_to_alert().accept()
        time.sleep(1)
    except:
        pass
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id("Account"))
    driver.find_element_by_id("Account").send_keys(acc)
    time.sleep(2)
    # enter password
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id("Password"))
    driver.find_element_by_id("Password").send_keys(pwd)
    time.sleep(2)
    # login
    driver.find_element_by_xpath("//button[@type='submit']").click()
    print('[info] logging success')
    return driver



def getAllName(driver):
    '''
    '''
    driver.execute_script('window.open("{}")'.format(person_detail))
    driver.switch_to_window(driver.window_handles[1])
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id("imgMugShot"))
    # click all person
    btn = driver.find_element_by_xpath("//input[@id='CaseType4']")
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(1)
    # get all name
    name_list = []
    get_name_num = int((driver.find_element_by_xpath("//div[@id='PatientGrid']/div[last()]/span").text.split('共 ')[1].split('筆')[0]))
    this_name_page_num = int((driver.find_element_by_xpath("//div[@id='PatientGrid']/div[last()]/span").text.split('共 ')[0].split(' - ')[1]))
    for i in range((math.ceil((get_name_num / this_name_page_num)*1))):
        if get_name_num <= this_name_page_num :
            this_name_page_num = get_name_num
        for j in range(this_name_page_num) :
            j +=1
            name_list.append(driver.find_element_by_xpath("//div[@id='PatientGrid']/div[2]/table/tbody/tr[{}]/td[1]".format(j)).text)
        get_name_num -= this_name_page_num
        # click 下一頁
        driver.find_element_by_xpath("//div[@id='PatientGrid']/div[last()]/a[3]").send_keys('\n')
        time.sleep(1)    
    print('[info] get all name success ,get {} people'.format(len(name_list)))
    return driver,name_list



def getBasicInfo(driver,name,how_many_day):
    '''
    '''
    how_many_day = (datetime.datetime.now() - datetime.timedelta(days=how_many_day)).strftime("%Y/%m/%d")
    result = {}

    if name+'.json' in os.listdir(data_path):
        return driver,False

    # switch to page2 
    if len(driver.window_handles) == 2:
        driver.switch_to_window(driver.window_handles[1])
        # click all person
        btn = driver.find_element_by_xpath("//input[@id='CaseType4']")
        driver.execute_script("arguments[0].click();", btn)

    # search data from name
    driver.find_element_by_xpath("//input[@k-options='patientSearchOption']").clear()
    time.sleep(1)
    driver.find_element_by_xpath("//input[@k-options='patientSearchOption']").send_keys(name)
    time.sleep(1)
    btn = driver.find_element_by_xpath("//a[@ng-click='kendoQuery()']")
    driver.execute_script("arguments[0].click();", btn)
    # time.sleep(3)
    while True:
        if driver.find_element_by_xpath("//input[@ng-model='layoutPatient.Name']").get_attribute("value") == name:
            break
        else :
            time.sleep(1)
    # name
    result["姓名"] = driver.find_element_by_xpath("//input[@ng-model='layoutPatient.Name']").get_attribute("value")
    print('[info] pagename:{},needname:{}'.format(result["姓名"],name))
    # age
    result["年齡"] = driver.find_element_by_xpath("//input[@ng-model='layoutPatient.Age']").get_attribute("value")
    # gender
    result["性別"] = driver.find_element_by_xpath("//input[@ng-model='layoutPatient.SexName']").get_attribute("value")
    # bed site
    bed_site = driver.find_element_by_xpath("//input[@ng-model='layoutPatient.BedSite']").get_attribute("value")
    result["床位"] = '' if bed_site == '' else bed_site.split('F,')[1].replace(',','')
    # cases date
    result["開案日期"] = driver.find_element_by_xpath("//input[@ng-model='layoutPatient.CaseDateF']").get_attribute("value")
    # status
    result["開案狀態"] = driver.find_element_by_xpath("//input[@id='Status']").get_attribute("value")
    # alleviate medical care
    result["緩和醫療"] = driver.find_element_by_xpath("//input[@ng-model='layoutPatient.AlleviateMedicalCare']").get_attribute("value")
    #  number
    result["編號"] = driver.find_element_by_xpath("//input[@ng-model='layoutPatient.Kcstmr']").get_attribute("value")
    # cid
    result["身分證字號"] = driver.find_element_by_xpath("//input[@ng-model='Patient.CId']").get_attribute("value")
    # birthday
    result["生日"] = driver.find_element_by_xpath("//input[@ng-model='Patient.Birthday']").get_attribute("value")
    # marriage
    result["婚姻"] = driver.find_element_by_xpath("//label[@for='Married']/following-sibling::span[1]").text.split('\n')[0]
    # language
    mandarin = True if driver.find_element_by_xpath("//input[@id='Mandarin']").is_selected() == True else False
    taiwanese = True if driver.find_element_by_xpath("//input[@id='Taiwanese']").is_selected() == True else False
    hakka = True if driver.find_element_by_xpath("//input[@id='Hakka']").is_selected() == True else False
    aboriginal = True if driver.find_element_by_xpath("//input[@id='Aboriginal']").is_selected() == True else False
    otherLanguage = False if driver.find_element_by_xpath("//input[@id='OtherLanguage']").is_selected() == False else driver.find_element_by_xpath("//input[@id='OtherLanguageRemark']").get_attribute("value")
    result["慣用語言"] = {'國語':mandarin , '台語':taiwanese , '客語':hakka , '原住民語':aboriginal , '其他':otherLanguage}
    # address
    address_detail_city = driver.find_element_by_xpath("//span[@aria-owns='AddressDetailCity_listbox']").text.split('\n')[0]
    address_detail_city = address_detail_city if address_detail_city != '--縣市' else ''
    address_detail_area = driver.find_element_by_xpath("//span[@aria-owns='AddressDetailArea_listbox']").text.split('\n')[0]
    address_detail_area = address_detail_area if address_detail_area != '--鄉鎮市區' else ''
    address_detail_address = driver.find_element_by_xpath("//input[@id='AddressDetailAddress']").get_attribute("value")
    address_detail_address = address_detail_address if address_detail_address != ' ' else ''
    result["戶籍地址"] = {'市縣':address_detail_city , '鄉鎮市區':address_detail_area , '詳細地址':address_detail_address }
    # mail address
    mailing_address_detail_city = driver.find_element_by_xpath("//span[@aria-owns='MailingAddressDetailCity_listbox']").text.split('\n')[0]
    mailing_address_detail_city = mailing_address_detail_city if mailing_address_detail_city != '--縣市' else ''
    mailing_address_detail_area = driver.find_element_by_xpath("//span[@aria-owns='MailingAddressDetailArea_listbox']").text.split('\n')[0]
    mailing_address_detail_area = mailing_address_detail_area if mailing_address_detail_area != '--鄉鎮市區' else ''
    mailing_address_detail_address = driver.find_element_by_xpath("//input[@id='MailingAddressDetailAddress']").get_attribute("value")
    mailing_address_detail_address = mailing_address_detail_address if mailing_address_detail_address != ' ' else ''
    result["通訊地址"] = {'市縣':mailing_address_detail_city , '鄉鎮市區':mailing_address_detail_area , '詳細地址':mailing_address_detail_address }
    # ContactPerson
    result["緊急聯絡人"],r = [],[]
    menu_table = driver.find_element_by_xpath("//div[@id='ContactPersonGrid']/div[3]/table/tbody")
    rows = len(menu_table.find_elements_by_tag_name('tr'))
    for j in range(rows):
        c_name = driver.find_element_by_xpath("//div[@id='ContactPersonGrid']/div[3]/table/tbody/tr[{}]/td[1]".format(j+1)).text
        c_relation = driver.find_element_by_xpath("//div[@id='ContactPersonGrid']/div[3]/table/tbody/tr[{}]/td[2]".format(j+1)).text
        c_title = driver.find_element_by_xpath("//div[@id='ContactPersonGrid']/div[3]/table/tbody/tr[{}]/td[3]".format(j+1)).text
        c_phone = driver.find_element_by_xpath("//div[@id='ContactPersonGrid']/div[3]/table/tbody/tr[{}]/td[4]".format(j+1)).text
        c_celphone = driver.find_element_by_xpath("//div[@id='ContactPersonGrid']/div[3]/table/tbody/tr[{}]/td[5]".format(j+1)).text
        result["緊急聯絡人"].append({'姓名':c_name,'關係':c_relation,'稱謂':c_title,'電話':c_phone,'手機':c_celphone})
    # Identitication type
    result["福利身分"] = Select(driver.find_element_by_xpath("//select[@id='IdentiticationType']")).first_selected_option.get_attribute("innerHTML")

    # switch to 護理紀錄
    print('[info] start get 護理紀錄')
    result['護理紀錄'] = []
    driver.execute_script('window.open("{}")'.format(nurse_record))
    driver.switch_to_window(driver.window_handles[2])
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id("imgMugShot"))
    # change start time 5 years ago
    driver.find_element_by_xpath("//input[@id='start']").clear()
    time.sleep(1)
    driver.find_element_by_xpath("//input[@id='start']").send_keys(how_many_day)
    time.sleep(2)
    get_num = int((driver.find_element_by_xpath("//div[@id='NursingRecordGrid']/div[last()]/span").text.split('共 ')[1].split('筆')[0]))
    this_page_num = int((driver.find_element_by_xpath("//div[@id='NursingRecordGrid']/div[last()]/span").text.split('共 ')[0].split(' - ')[1]))

    # nursing record grid
    for j in range((math.ceil((get_num / this_page_num)*1))):
        if get_num <= this_page_num :
            this_page_num = get_num
        for k in range(this_page_num) :
            k +=1
            dtime = driver.find_element_by_xpath("//div[@id='NursingRecordGrid']/div[2]/table/tbody/tr[{}]/td[1]".format(k)).text
            focus = driver.find_element_by_xpath("//div[@id='NursingRecordGrid']/div[2]/table/tbody/tr[{}]/td[2]".format(k)).text
            record = driver.find_element_by_xpath("//div[@id='NursingRecordGrid']/div[2]/table/tbody/tr[{}]/td[3]".format(k)).text
            shift = driver.find_element_by_xpath("//div[@id='NursingRecordGrid']/div[2]/table/tbody/tr[{}]/td[4]".format(k)).text
            person = driver.find_element_by_xpath("//div[@id='NursingRecordGrid']/div[2]/table/tbody/tr[{}]/td[5]".format(k)).text
            result['護理紀錄'].append({'日期時間':dtime,'焦點':focus,'護理記錄':record,'班別':shift,'護理人員':person})
        get_num -= this_page_num
        # click 下一頁
        driver.find_element_by_xpath("//div[@id='NursingRecordGrid']/div[last()]/a[3]").send_keys('\n')
        time.sleep(1)

    driver.close()
    print('[info] {} data crawler success!'.format(result["姓名"]))

    return driver,result



# catch bed information(only catch ones)
def getBedRecord(driver):
    '''
    catch bed information(only catch ones)
    '''
    results = []
    # open bed record
    driver.execute_script('window.open("{}")'.format(bed_record))
    driver.switch_to_window(driver.window_handles[-1])
    time.sleep(3)
    # all bed num
    get_num = int((driver.find_element_by_xpath("//div[@id='BedRecordGrid']/div[last()]/span").text.split('共 ')[1].split('筆')[0]))
    # get this page num from table
    this_page_num = int((driver.find_element_by_xpath("//div[@id='BedRecordGrid']/div[last()]/span").text.split('共 ')[0].split(' - ')[1]))
    for j in range((math.ceil((get_num / this_page_num)*1))):
        if get_num <= this_page_num :
            this_page_num = get_num
        for k in range(this_page_num) :
            k +=1
            # get area
            area = driver.find_element_by_xpath("//div[@id='BedRecordGrid']/div[2]/table/tbody/tr[{}]/td[1]".format(k)).text
            # get bed site
            bed_site = driver.find_element_by_xpath("//div[@id='BedRecordGrid']/div[2]/table/tbody/tr[{}]/td[2]".format(k)).text + driver.find_element_by_xpath("//div[@id='BedRecordGrid']/div[2]/table/tbody/tr[{}]/td[3]".format(k)).text
            # get status
            status = driver.find_element_by_xpath("//div[@id='BedRecordGrid']/div[2]/table/tbody/tr[{}]/td[5]".format(k)).text
            results.append({'區域':area,'房號':bed_site,'狀態':status})
        get_num -= this_page_num
        # click 下一頁
        driver.find_element_by_xpath("//div[@id='BedRecordGrid']/div[last()]/a[3]").send_keys('\n')
        time.sleep(1)
    driver.close()

    # switch to one 
    driver.switch_to_window(driver.window_handles[0])

    return driver,results



def getPhysiologicalMeasurements(driver,name,how_many_day=60):
    '''
    '''
    half_year = (datetime.datetime.now() - datetime.timedelta(days=how_many_day)).strftime("%Y/%m/%d")
    results = []

    if name +'.json' in os.listdir(physiological_result):
        return driver,False
    else :
        # turn to physiological measurements record page
        driver.execute_script('window.open("{}")'.format(physiological_measurements_record))
        driver.switch_to_window(driver.window_handles[2])
        time.sleep(3)
    
    # click all person
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id("CaseType4"))
    btn = driver.find_element_by_xpath("//input[@id='CaseType4']")
    driver.execute_script("arguments[0].click();", btn)
    r = waitForPage(driver)
    # search data from name
    driver.find_element_by_xpath("//input[@k-options='patientSearchOption']").clear()
    driver.find_element_by_xpath("//input[@k-options='patientSearchOption']").send_keys(name)
    btn = driver.find_element_by_xpath("//a[@ng-click='kendoQuery()']")
    driver.execute_script("arguments[0].click();", btn)
    r = waitForPage(driver)
    # change start time half years ago
    driver.find_element_by_xpath("//input[@id='start']").clear()
    driver.find_element_by_xpath("//input[@id='start']").send_keys(half_year)
    r = waitForPage(driver)
    # get number of data
    try:
        get_num = int((driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[last()]/span").text.split('共 ')[1].split('筆')[0]))
        this_page_num = int((driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[last()]/span").text.split('共 ')[0].split(' - ')[1]))
        
    except :
        driver.close()
        driver.switch_to_window(driver.window_handles[1])
        return driver,results

    # get data
    for j in range((math.ceil((get_num / this_page_num)*1))):
        if get_num <= this_page_num :
            this_page_num = get_num
        for k in range(this_page_num) :
            result = {}
            k +=1
            result['日期時間'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[1]".format(k)).text
            result['體溫'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[2]".format(k)).text
            result['脈搏'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[3]".format(k)).text
            result['呼吸'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[4]".format(k)).text
            result['收縮壓'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[5]".format(k)).text
            result['舒張壓'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[6]".format(k)).text
            result['血氧'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[7]".format(k)).text
            result['飯前血糖'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[8]".format(k)).text
            result['飯後血糖'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[9]".format(k)).text
            result['疼痛'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[10]".format(k)).text
            result['備註'] = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[11]".format(k)).text
            # 記錄人員
            btn = driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[2]/table/tbody/tr[{}]/td[12]/a[1]".format(k))
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(3)
            result["記錄人員"] = Select(driver.find_element_by_xpath("//select[@id='WorkUser']")).first_selected_option.get_attribute("innerHTML")
            btn = driver.find_element_by_xpath("//button[@id='ReturnShow']")
            driver.execute_script("arguments[0].click();", btn)
            r = waitForPage(driver)
            results.append(result)

        get_num -= this_page_num
        # click 下一頁
        driver.find_element_by_xpath("//div[@id='MeasurementGrid']/div[last()]/a[3]").send_keys('\n')
        r = waitForPage(driver)

    driver.close()
    driver.switch_to_window(driver.window_handles[1])

    return driver,results



def getDrugRecord(driver,name,how_many_day='2021/05/28'):
    '''
    '''
    results = []
    if name +'.json' in os.listdir(drug_result):
        return driver,False
    else :
        # turn to physiological measurements record page
        driver.execute_script('window.open("{}")'.format(drug_record))
        driver.switch_to_window(driver.window_handles[-1])
        time.sleep(3)
    # click all person
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id("CaseType4"))
    btn = driver.find_element_by_xpath("//input[@id='CaseType4']")
    driver.execute_script("arguments[0].click();", btn)
    r = waitForPage(driver)
    # search data from name
    driver.find_element_by_xpath("//input[@k-options='patientSearchOption']").clear()
    driver.find_element_by_xpath("//input[@k-options='patientSearchOption']").send_keys(name)
    btn = driver.find_element_by_xpath("//a[@ng-click='kendoQuery()']")
    time.sleep(1)
    driver.execute_script("arguments[0].click();", btn)
    r = waitForPage(driver)
    # get num
    get_num = int((driver.find_element_by_xpath("//div[@id='MainGrid']/div[last()]/span").text.split('共 ')[1].split('筆')[0]))
    this_page_num = int((driver.find_element_by_xpath("//div[@id='MainGrid']/div[last()]/span").text.split('共 ')[0].split(' - ')[1]))

    # get data
    for j in range((math.ceil((get_num / this_page_num)*1))):
        if get_num <= this_page_num :
            this_page_num = get_num
        for k in range(this_page_num) :
            result = {}
            k +=1
            # get data
            institute = driver.find_element_by_xpath("//div[@id='MainGrid']/div[2]/table/tbody/tr[contains(@class, 'k-master-row')][{}]/td[4]".format(k)).text
            division = driver.find_element_by_xpath("//div[@id='MainGrid']/div[2]/table/tbody/tr[contains(@class, 'k-master-row')][{}]/td[5]".format(k)).text
            dtype = driver.find_element_by_xpath("//div[@id='MainGrid']/div[2]/table/tbody/tr[contains(@class, 'k-master-row')][{}]/td[3]".format(k)).text
            # click edit btn
            btn = driver.find_element_by_xpath("//div[@id='MainGrid']/div[2]/table/tbody/tr[contains(@class, 'k-master-row')][{}]/td[11]/a[1]".format(k))
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(3)
            begindate = driver.find_element_by_xpath("//input[@id='BeginDate']").get_attribute("value")
            enddate = driver.find_element_by_xpath("//input[@id='EndDate']").get_attribute("value")

            if datetime.datetime.strptime(enddate, "%Y/%m/%d") < datetime.datetime.strptime(how_many_day, "%Y/%m/%d"):
                continue

            if dtype != '自備':
                cnt = len(driver.find_elements_by_xpath("//table[@id='Drugs']/tbody/tr"))
            else :
                cnt = len(driver.find_elements_by_xpath("//div[@id='DrugGrid']/table/tbody/tr"))
            for i in range(cnt):
                result = {}
                if dtype != '自備':
                    if i == 0 :
                        continue
                    result['名稱'] = driver.find_element_by_xpath("//table[@id='Drugs']/tbody/tr[{}]/td[1]".format(i+1)).text
                    result['用量'] = driver.find_element_by_xpath("//table[@id='Drugs']/tbody/tr[{}]/td[2]".format(i+1)).text
                    result['單位'] = driver.find_element_by_xpath("//table[@id='Drugs']/tbody/tr[{}]/td[3]".format(i+1)).text
                    r = driver.find_element_by_xpath("//table[@id='Drugs']/tbody/tr[{}]/td[5]".format(i+1)).text.split(' - ')
                    result['服法'] = driver.find_element_by_xpath("//table[@id='Drugs']/tbody/tr[{}]/td[7]".format(i+1)).text
                    result['途徑'] = driver.find_element_by_xpath("//table[@id='Drugs']/tbody/tr[{}]/td[8]".format(i+1)).text
                else :
                    result['名稱'] = driver.find_element_by_xpath("//div[@id='DrugGrid']/table/tbody/tr[{}]/td[4]".format(i+1)).text
                    result['用量'] = driver.find_element_by_xpath("//div[@id='DrugGrid']/table/tbody/tr[{}]/td[5]".format(i+1)).text
                    result['單位'] = driver.find_element_by_xpath("//div[@id='DrugGrid']/table/tbody/tr[{}]/td[6]".format(i+1)).text
                    r = driver.find_element_by_xpath("//div[@id='DrugGrid']/table/tbody/tr[{}]/td[8]".format(i+1)).text.split(' - ')
                    result['服法'] = driver.find_element_by_xpath("//div[@id='DrugGrid']/table/tbody/tr[{}]/td[10]".format(i+1)).text
                    result['途徑'] = driver.find_element_by_xpath("//div[@id='DrugGrid']/table/tbody/tr[{}]/td[11]".format(i+1)).text

                result['頻率'] = r[0]
                result['類型'] = dtype
                result['院所'] = institute
                result['科別'] = division
                result['服藥開始日'] = begindate
                result['服藥結束日'] = enddate
                try:
                    r1 = r[1].split(',') 
                except :
                    r1 = []
                for l in range(4):
                    try:
                        result['時間{}'.format(l)] = r1[l]
                    except:
                        result['時間{}'.format(l)] = ""
                results.append(result)
            
            # click cancel btn
            btn = driver.find_element_by_xpath("//button[@id='cancel']")
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)

    driver.close()
    driver.switch_to_window(driver.window_handles[-1])
    return driver,{'藥事資料':results}



def getRestraintRecord(driver,name):
    '''
    '''
    results = []
    if name +'.json' in os.listdir(restraint_result):
        return driver,False
    else :
        # turn to physiological measurements record page
        driver.execute_script('window.open("{}")'.format(restraint_record))
        driver.switch_to_window(driver.window_handles[-1])
        time.sleep(3)
    # click all person
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id("CaseType4"))
    btn = driver.find_element_by_xpath("//input[@id='CaseType4']")
    driver.execute_script("arguments[0].click();", btn)
    r = waitForPage(driver)
    # search data from name
    driver.find_element_by_xpath("//input[@k-options='patientSearchOption']").clear()
    driver.find_element_by_xpath("//input[@k-options='patientSearchOption']").send_keys(name)
    btn = driver.find_element_by_xpath("//a[@ng-click='kendoQuery()']")
    time.sleep(1)
    driver.execute_script("arguments[0].click();", btn)
    r = waitForPage(driver)
    # get num
    try:
        get_num = int((driver.find_element_by_xpath("//div[@id='MainGrid']/div[last()]/span").text.split('共 ')[1].split('筆')[0]))
        this_page_num = int((driver.find_element_by_xpath("//div[@id='MainGrid']/div[last()]/span").text.split('共 ')[0].split(' - ')[1]))
    except :
        driver.close()
        driver.switch_to_window(driver.window_handles[-1])
        return driver,results

    # get data
    for j in range((math.ceil((get_num / this_page_num)*1))):
        if get_num <= this_page_num :
            this_page_num = get_num
        for k in range(this_page_num) :
            result = {}
            k +=1
            # MainGrid
            result['約束時間'] = driver.find_element_by_xpath("//div[@id='MainGrid']/div[2]/table/tbody/tr[contains(@class, 'k-master-row')][{}]/td[3]".format(k)).text
            result['約束主因'] = driver.find_element_by_xpath("//div[@id='MainGrid']/div[2]/table/tbody/tr[contains(@class, 'k-master-row')][{}]/td[4]".format(k)).text
            result['約束部位'] = driver.find_element_by_xpath("//div[@id='MainGrid']/div[2]/table/tbody/tr[contains(@class, 'k-master-row')][{}]/td[5]".format(k)).text
            result['約束方式'] = driver.find_element_by_xpath("//div[@id='MainGrid']/div[2]/table/tbody/tr[contains(@class, 'k-master-row')][{}]/td[6]".format(k)).text
            # click edit btn
            btn = driver.find_element_by_xpath("//div[@id='MainGrid']/div[2]/table/tbody/tr[contains(@class, 'k-master-row')][{}]/td[11]/a[1]".format(k))
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(3)
            result['護理人員'] = Select(driver.find_element_by_xpath("//select[@id='WorkUser']")).first_selected_option.get_attribute("innerHTML")
            result['移除約束'] = driver.find_element_by_xpath("//input[@id='IsRemove']").is_selected()
            Duration = {}
            Duration['<=1小時'] = driver.find_element_by_xpath("//input[@id='Duration_1']").is_selected()
            Duration['1-4小時'] = driver.find_element_by_xpath("//input[@id='Duration_1to4']").is_selected()
            Duration['4-8小時'] = driver.find_element_by_xpath("//input[@id='Duration_4to8']").is_selected()
            Duration['8-16小時'] = driver.find_element_by_xpath("//input[@id='Duration_8to16']").is_selected()
            Duration['16-24小時'] = driver.find_element_by_xpath("//input[@id='Duration_16to24']").is_selected()
            Duration['>=24小時'] = driver.find_element_by_xpath("//input[@id='Duration_moreThan24']").is_selected()
            try:
                result['總持續時間'] = [i for i in Duration if Duration[i]==True][0]
            except IndexError:
                result['總持續時間'] = ''
            result['觀察間隔'] = driver.find_element_by_xpath("//input[@ng-model='RestraintRecord.CareInterval']").get_attribute("value")
            result['放鬆間隔'] = driver.find_element_by_xpath("//input[@ng-model='RestraintRecord.RelaxInterval']").get_attribute("value")
            result['每次放鬆'] = driver.find_element_by_xpath("//input[@ng-model='RestraintRecord.RelaxMinutes']").get_attribute("value")
            result['防範措施'] = {
                    '增加陪伴':driver.find_element_by_xpath("//input[@id='Precautions_Companionship']").is_selected(),
                    '使用枕頭或靠床旁椅的保護措施':driver.find_element_by_xpath("//input[@id='Precautions_Pillow']").is_selected(),
                    '將床放低靠牆或依需要更換矮床':driver.find_element_by_xpath("//input[@id='Precautions_BedDown']").is_selected(),
                    '協助下床坐輪椅':driver.find_element_by_xpath("//input[@id='Precautions_Wheelchair']").is_selected(),
                    '主動滿足需求':driver.find_element_by_xpath("//input[@id='Precautions_MeetTheDemand']").is_selected(),
                    '有意義的活動以分散住民注意力如至娛樂室看電視':driver.find_element_by_xpath("//input[@id='Precautions_Activity']").is_selected(),
                    '其他':driver.find_element_by_xpath("//input[@id='OtherPrecautionsRemark']").get_attribute("value")
            }
            result['護理措施'] = {
                    '使用約束前已試過其他防範措施':driver.find_element_by_xpath("//input[@id='NursingMeasures_TakenBefore']").is_selected(),
                    '評估約束理由必要性及可能造成合併症':driver.find_element_by_xpath("//input[@id='NursingMeasures_Evaluation']").is_selected(),
                    '與工作人員協商':driver.find_element_by_xpath("//input[@id='NursingMeasures_Consult']").is_selected(),
                    '向住民解釋':driver.find_element_by_xpath("//input[@id='NursingMeasures_Explain']").is_selected(),
                    '與住民家屬討論經同意約束':driver.find_element_by_xpath("//input[@id='NursingMeasures_Discussions']").is_selected(),
                    '其他':driver.find_element_by_xpath("//input[@id='OtherNursingMeasuresRemark']").get_attribute("value")
            }  
            result['家屬備忘'] = driver.find_element_by_xpath("//textarea[@id='FamilyRemark']").get_attribute("value")
            result['其他備註'] = driver.find_element_by_xpath("//textarea[@id='Remark']").get_attribute("value")
            result['後續評估'] = driver.find_element_by_xpath("//textarea[@id='Evaluation']").get_attribute("value")

            results.append(result)
            # click cancel btn
            btn = driver.find_element_by_xpath("//button[@id='cancel']")
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)

    driver.close()
    driver.switch_to_window(driver.window_handles[-1])
    return driver,results



def HospitalizedIndicatorsReport(input_file,output_path,get_code_path):
    '''
    需先下載好資料csv檔案，下載位置
    指標/報表管理 > 指標表單 > 非計畫性轉至急性醫院住院
    選定區間之後查詢完成並下載csv檔案
    '''
    with open(input_file, newline='',encoding='utf-8') as csvfile:
        rows = csv.reader(csvfile)
        c = 0
        for row in rows:
            if c == 0 :
                c += 1
                continue
            result = {}
            result['姓名'] = row[1]
            with open(get_code_path+'/{}.json'.format(result['姓名']), 'r',encoding='utf-8') as f1:
                data = json.load(f1)
            result['編號'] = data['編號']
            result['性別'] = row[3]
            result['生日'] = row[5]
            result['開案日'] = row[7]
            result['床位'] = row[9]
            result['填表人員'] = row[11]
            result['入住七十二小時內'] = False if row[13]=='0' else True 
            for i in [row[15],row[16],row[17],row[18]]:
                if i[0] == '1':
                    result['發生班別'] = i[1:]
            result['住院天數'] = row[20]
            result['住院日期'] = row[22]
            result['出院日期'] = row[24]
            result['住院醫院'] = row[26]
            result['科別'] = row[28]
            result['主治醫師'] = row[30]
            result['陪同住院者'] = row[32]
            result['陪同者關係'] = row[34]
            result['陪同者電話'] = row[36]
            for i in [row[38],row[39]]:
                if i[0] == '1':
                    result['出院帶藥'] = i[1:]
            for i in [row[41],row[42],row[43],row[44],row[45]]:
                if i[0] == '1':
                    result['住院原因'] = i[1:]
            for i in [row[46],row[47],row[48],row[49],row[50],row[51]]:
                if i[0] == '1':
                    result['導因分析'] = i[1:]+row[52]
            for i in [row[55],row[56],row[57],row[58],row[59],row[60]]:
                if i[0] == '1':
                    result['處理結果'] = i[1:]
            for i in [row[62],row[63]]:
                if i[0] == '1':
                    result['類別分析'] = i[1:]
            result['疾病診斷'] = row[65]
            result['原因分析'] = row[67]
            result['改善措施'] = row[69]
            result['後續追蹤'] = row[71]
            result['其他備註'] = row[73]
            # output_path
            result = json.dumps(result, ensure_ascii=False)
            with open('{}/{}.json'.format(output_path,str(c)), 'w',encoding='utf-8') as f2:
                f2.write(result)
            c += 1






if __name__ == '__main__':


    print('[info] start crawler')

    # init selenium
    driver = initSelenium(proxy=None)


    # (必選) 登入頁面
    driver = loginPage(driver,login_page)


    # (可選) 抓取床位資訊
    '''
    driver,results = getBedRecord(driver)
    results = json.dumps(results, ensure_ascii=False)
    with open('{}/bedInfo.json'.format(data_path), 'w',encoding='utf-8') as f:
        f.write(results)
    '''


    # (必選) 抓取所有人名
    driver,name_list = getAllName(driver)


    #  (可選) 抓取基本資料
    '''
    for name in name_list:
        driver,results = getBasicInfo(driver,name,how_many_day=1825)
        if results != False :
            results = json.dumps(results, ensure_ascii=False)
            with open('{}/{}.json'.format(data_path,name), 'w',encoding='utf-8') as f:
                f.write(results)
        else :
            continue
    '''


    # (可選) 抓取生命徵象資料
    '''
    for name in name_list:
        driver,results = getPhysiologicalMeasurements(driver,name,how_many_day=60)
        if results != False :
            results = json.dumps(results, ensure_ascii=False)
            with open('{}/{}.json'.format(physiological_result,name), 'w',encoding='utf-8') as f:
                f.write(results)
        else :
            continue
    '''


    # (可選) 抓取藥事資料
    '''
    for name in name_list:
        driver,results = getDrugRecord(driver,name,how_many_day='2021/05/28')
        if results != False :
            results = json.dumps(results, ensure_ascii=False)
            with open('{}/{}.json'.format(drug_result,name), 'w',encoding='utf-8') as f:
                f.write(results)
        else :
            continue
    '''

    # (可選) 抓取約束記錄
    for name in name_list:
        driver,results = getRestraintRecord(driver,name)
        if results != False :
            results = json.dumps(results, ensure_ascii=False)
            with open('{}/{}.json'.format(restraint_result,name), 'w',encoding='utf-8') as f:
                f.write(results)
        else :
            continue


    driver.quit()

    # (可選) 抓取非計畫性轉至急性醫院住院紀錄單(評鑑)
    '''
    HospitalizedIndicatorsReport('HospitalizedIndicatorsRecord.csv','hospitalized','results')
    '''