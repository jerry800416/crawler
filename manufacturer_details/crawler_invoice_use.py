# coding=utf-8
import json,time,os
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By as BY
from selenium.webdriver.support import ui as UI
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains as AC
from crawler_lib import *
from crawler_ref import logpath,path


def sendCaptcha2Mail(driver,ten_minute_mail):
    '''
    use 10 Minute Mail to receive captcha
    '''
    # open Ministry of Finance and Taxation page
    driver.execute_script("window.open('https://www.etax.nat.gov.tw/cbes/web/CBES113W1_1')")
    # switch to Ministry of Finance and Taxation page
    driver.switch_to.window(driver.window_handles[1])
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_xpath("//input[@id='vatId']"))
    # set absolute time sleep to avoid Robot check
    time.sleep(2)
    # find send to email button and click
    driver.find_element_by_xpath("//a[@title='驗證碼']").click()
    time.sleep(2)
    # enter mail address
    driver.find_element_by_xpath("//input[@id='captchaReceiverMail']").send_keys(ten_minute_mail)
    time.sleep(2)
    # click send mail 
    driver.find_element_by_xpath("//button[@id='btn_submit']").click()
    return driver


def getCaptchaCode(driver):
    '''
    receive mail and get captcha
    '''
    # switch to 10 min mail page
    driver.switch_to.window(driver.window_handles[0])
    # wait 5 min to receive mail
    c = 0
    r = waitEmail(driver,c)
    while r != True:
        c += 1
        r = waitEmail(driver,c)
    # click page(200,100) to skip ads
    AC(driver).move_by_offset(200, 100).click().perform()
    # set absolute time sleep to avoid Robot check
    time.sleep(1)
    # get captcha
    code = driver.find_element_by_class_name('mailinhtml').text.split('：',1)[1]

    return driver,code


def waitEmail(driver,c):
    '''
    wait 10min mail get recaptcha mail and refresh page
    '''
    try:
        # refresh this page
        driver.get('https://10minutemail.net/?lang=zh-tw')
        # wait for 30 sec
        UI.WebDriverWait(driver,60).until(EC.text_to_be_present_in_element(('id','maillist'),'財政資訊中心'))
        time.sleep(1)
        # if get mail ,open it
        driver.find_element_by_xpath("//a[text()='財政資訊中心 <webmail@etax.nat.gov.tw>']").click()
        return True
    except:
        if c == 4 :
            return True
        return False


def getCompanyInvoice(driver,gui,code):
    '''
    get company data
    '''
    # switch to Ministry of Finance and Taxation page
    driver.switch_to.window(driver.window_handles[1])
    # enter gui
    driver.find_element_by_xpath("//input[@id='vatId']").send_keys(gui)
    # enter captcha
    driver.find_element_by_id('captcha').send_keys(code)
    # submit
    driver.find_element_by_xpath("//input[@type='submit']").click()
    time.sleep(5)
    # click 查詢近期是否使用統一發票 button
    driver.find_element_by_id("txCompany").click()
    time.sleep(5)
    # get ajax result
    driver.execute_script("window.open('https://www.etax.nat.gov.tw/cbes/web/CBES113W/getIsTxCompany?vatId={}')".format(gui))
    # switch to ajax result json page
    driver.switch_to.window(driver.window_handles[2])
    UI.WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_tag_name('pre'))
    # get result in html
    content = driver.find_element_by_tag_name('pre').text
    # string to json obj
    parsed_json = json.loads(content)

    return driver,parsed_json['queryResult']


def mkJSON(path,seq,result):
    '''
    control invice json file 
    '''
    # if result is True ,make space invoice json file in dir 
    if result == True:
        with open(path+seq+'\invoice.json','w',encoding="utf-8") as f:
            pass
    # if result is False ,remove invoice file in dir
    elif result == False:
        if 'invoice.json' in os.listdir(path+seq) :
            os.remove(path+seq+'\invoice.json')
    else :
        pass


def checkInvoice(gui):
    '''
    main control
    '''
    try:
        # init selenium
        driver = initSelenium(proxy=None,debugmode=True)
        # get 10 min mail address
        driver,ten_minute_mail = getMailAddr(driver)
        a
        # send captcha to mail address
        driver = sendCaptcha2Mail(driver,ten_minute_mail)
        # receive mail and get captcha
        driver,code = getCaptchaCode(driver)
        # enter captcha and search invoice
        driver,result = getCompanyInvoice(driver,gui,code)
        driver.quit()
    except Exception as e:
        result = None
        try:
            driver.quit()
        except:
            pass
        go2log(logpath,'[checkInvoiceERR]{}'.format(seq)+ str(e))

    return result



if __name__ == '__main__':
    

    companylist = getAllDir(path,os.listdir(path))
    # get detail from supplierlist.json
    companys = getDetail(path + 'supplierlist.json')

    for i in companys:
        # get sequence and gui code
        seq = str(i['Seq'])
        gui = i['TaxNumber']
        # mkdir sequence dir
        if seq not in companylist:
            os.mkdir(path + seq)
        result = checkInvoice(gui)
        # control make json file or not
        mkJSON(path,seq,result)
