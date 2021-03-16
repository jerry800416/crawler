# coding=utf-8
import time,os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By as BY
from selenium.webdriver.support import ui as UI
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select
from crawler_lib import *
from crawler_ref import logpath,path


def getBlackList(url,downloadaddr):
    '''
    '''
    try:
        # init selenium
        driver = initSelenium(proxy=None,downloadaddr=downloadaddr,debugmode=False)
        # get url 
        driver.get(url)
        # click download btn
        UI.WebDriverWait(driver,15).until(lambda driver: driver.find_element_by_xpath("//input[@name='queryRVFile_bt']"))
        driver.find_element_by_xpath("//input[@name='queryRVFile_bt']").click()
        # sleep 3 sec for download 
        time.sleep(3)
        # quit driver
        driver.quit()
        # rename to blacklist
        try:
            os.rename(downloadaddr+'queryRVFile.xls',downloadaddr+'blacklist.xls')
        except FileExistsError:
            os.remove(downloadaddr+'blacklist.xls')
            os.rename(downloadaddr+'queryRVFile.xls',downloadaddr+'blacklist.xls')
    except Exception as e:
        try:
            driver.quit()
        except:
            pass
        go2log(logpath,'[getBlackListERR]'+ str(e))




if __name__ == '__main__':
    
    # get black list
    url = "https://web.pcc.gov.tw/vms/rvlmd/DisabilitiesQueryRV.do"
    getBlackList(url,path)
    