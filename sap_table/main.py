from selenium import webdriver
import csv,openpyxl,time
import pandas as pd


succ_table_list = []

'''
    tb_name 表格名稱
    chi_tb_description 表格中文說明
    chi_name 中文名稱
    col_name 欄位名稱
    name 英文名稱
    primary_key 主鍵
    data_type 資料型態
    length 長度 
    check_table 外部索引
    description Description
    main_category Main Category
    sub_category Sub Category
    table_type Table type
    chi_remark 備註
'''


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


def googleTranslate(driver,handles,text):
    '''
    '''
    if len(handles) < 2 :
        driver.execute_script('window.open("https://translate.google.com.tw/?hl=zh-TW&sl=en&tl=zh-TW&op=translate")')
    handles = driver.window_handles
    driver.switch_to_window(handles[1])
    if text not in ['',' ']:
        driver.find_element_by_xpath("//textarea[@role='combobox']").clear()
        driver.find_element_by_xpath("//textarea[@role='combobox']").send_keys(text)
        time.sleep(1)
        try:
            result = driver.find_element_by_xpath("//textarea[@lang='zh-TW']").get_attribute('data-initial-value')
        except :
            result = text
    else :
        result = ''
    driver.switch_to_window(handles[0])
    return result,driver,handles


def getTableInfo(driver,handles,modulename,modulelist):
    '''
    '''
    try:
        module = modulelist[modulename]
    except:
        module = 'reload'
    driver.switch_to_window(handles[0])
    driver.get("https://www.tcodesearch.com/sap-tables/detail?id={}".format(modulename))
    tb_name = modulename
    description = driver.find_element_by_xpath("//td[text()='Description:']/following-sibling::td[1]").text
    chi_tb_description,driver,handles = googleTranslate(driver,handles,description)
    main_category = driver.find_element_by_xpath("//td[text()='Main Category:']/following-sibling::td[1]").text
    sub_category = driver.find_element_by_xpath("//td[text()='Sub Category:']/following-sibling::td[1]").text
    table_type = driver.find_element_by_xpath("//td[text()='Table type:']/following-sibling::td[1]").text
    chi_remark,driver,handles = googleTranslate(driver,handles,driver.find_element_by_xpath("//p[@class='description']").text)

    num_rows = len(driver.find_elements_by_xpath("//table[@class='table table-striped border-radius shadow--sm']/tbody/tr"))
    
    n_check_table_list,ws = [],[]

    for i in range(num_rows):
        col_name = driver.find_element_by_xpath("//table[@class='table table-striped border-radius shadow--sm']/tbody/tr[{}]/td[2]".format(i+1)).text
        name = driver.find_element_by_xpath("//table[@class='table table-striped border-radius shadow--sm']/tbody/tr[{}]/td[3]".format(i+1)).text
        chi_name,driver,handles = googleTranslate(driver,handles,name)
        primary_key = driver.find_element_by_xpath("//table[@class='table table-striped border-radius shadow--sm']/tbody/tr[{}]/td[4]".format(i+1)).text
        data_type = driver.find_element_by_xpath("//table[@class='table table-striped border-radius shadow--sm']/tbody/tr[{}]/td[5]".format(i+1)).text
        length = driver.find_element_by_xpath("//table[@class='table table-striped border-radius shadow--sm']/tbody/tr[{}]/td[6]".format(i+1)).text
        check_table = driver.find_element_by_xpath("//table[@class='table table-striped border-radius shadow--sm']/tbody/tr[{}]/td[7]".format(i+1)).text
        global succ_table_list
        if (check_table not in ['','*']) and (check_table not in n_check_table_list) and (check_table not in succ_table_list):
            n_check_table_list.append(check_table)

        # print([tb_name,chi_tb_description,chi_name,col_name,name,primary_key,data_type,length,check_table,description,main_category,sub_category,table_type,chi_remark])
        ws.append([module,tb_name,chi_tb_description,chi_name,col_name,name,primary_key,data_type,length,check_table,description,main_category,sub_category,table_type,chi_remark])
        
    succ_table_list.append(modulename)
    
    with open('new_output.csv', 'a', newline='',encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(ws)


    return n_check_table_list,handles




if __name__ == '__main__':

    # pandas
    df = pd.read_excel(r'E:\\work\\crawler\\sap_table\\source\\SAP_DBSchema(範本)-V1.xlsx',sheet_name ='爬文資料表',engine='openpyxl')
    modellist = list(df["抓資料表格名稱"].T.to_numpy())
    df2 = df["模組"].T.to_numpy()
    newdict = {}
    for i in range(len(df2)):
        newdict[modellist[i]] = str(df2[i])

    # 初始化 selenium
    driver = initSelenium(proxy=None)
    handles = driver.window_handles

    # 寫入欄位名稱
    with open('output.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['模組','表格名稱','表格中文說明','中文名稱','欄位名稱','英文名稱','主鍵','資料型態','長度' ,'外部索引','Description','Main Category','Sub Category','Table type','備註'])
    
    finished_list = []

    while len(modellist) != 0 :
        table = modellist.pop(0)
        if (table not in finished_list) and (table not in ['nan',None]) :
            try :
                n_check_table_list,handles = getTableInfo(driver,handles,table,newdict)
                for i in n_check_table_list:
                    newdict[i] = str(newdict[table])

                modellist = n_check_table_list + modellist
                finished_list.append(table)
                # print(n_check_table_list)
                # wb.save('test.xlsx')
            except :
                with open('nodata.txt','a') as f:
                    f.write(str(table) + '\r')

            
    driver.quit()