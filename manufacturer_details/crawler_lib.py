# coding=utf-8
import datetime,time,os,json
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By as BY
from selenium.webdriver.support import ui as UI
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select




def getAllDir(path,companylist):
    '''
    return all data is dir
    '''
    result = []
    for i in companylist:
        if os.path.isdir(path +  i) and i not in ['result','venv','__pycache__']:
            result.append(i)
    return result


def getDetail(path):
    '''
    get some detail from json file
    '''
    with open(path,'r',encoding="utf-8") as f:
        data = json.load(f)
    return data


def initSelenium(downloadaddr=None,proxy=None,debugmode=True):
    '''
    init selenium and setting options
    '''
    #selenium options setting
    chrome_options = webdriver.ChromeOptions()
    if debugmode == False:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument('--log-level=3')
    # setting download addr and no sandbox
    # chrome_options.add_argument("---printing");
    if downloadaddr != None:
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': downloadaddr,"download.prompt_for_download": False,"download.directory_upgrade": True,"plugins.always_open_pdf_externally": True,"plugins.plugins_disabled": ["Chrome PDF Viewer"]}
        chrome_options.add_experimental_option('prefs', prefs)

    # "download.prompt_for_download": False,"download.directory_upgrade": True,"plugins.always_open_pdf_externally": True, "plugins.plugins_disabled": ["Chrome PDF Viewer"]

    # add proxy
    if proxy != None:
        chrome_options.add_argument('--proxy-server=http://{}'.format(proxy))

    driver = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
    #set browser loading timeout
    driver.set_page_load_timeout(120)

    return driver


def getMailAddr(driver):
    '''
    get free 10 Minute Mail address
    '''
    driver.get('https://10minutemail.net/')
    UI.WebDriverWait(driver,15).until(lambda driver: driver.find_element_by_id("fe_text"))
    # use 10minutes email get captcha
    ten_minute_mail = driver.find_element_by_id("fe_text").get_attribute('value')

    return driver,ten_minute_mail


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