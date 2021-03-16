from selenium import webdriver
import csv,openpyxl,time
import pandas as pd
from main import *

succ_table_list = []

if __name__ == '__main__':
    
    # reload list
    modellist = []
    with open('nodata.txt','r') as f:
        for line in f.readlines():
            modellist.append(line.strip())


    # finished list
    df = pd.read_excel(r'E:\\work\\crawler\\sap_table\\new_output.xlsx',sheet_name ='new_output',engine='openpyxl')
    finished_list = list(set(df["表格名稱"].T.to_numpy()))


    # pandas
    df = pd.read_excel(r'E:\\work\\crawler\\sap_table\\source\\SAP_DBSchema(範本)-V1.xlsx',sheet_name ='爬文資料表',engine='openpyxl')
    modellist_old = list(df["抓資料表格名稱"].T.to_numpy())
    df2 = df["模組"].T.to_numpy()
    newdict = {}
    for i in range(len(df2)):
        newdict[modellist_old[i]] = str(df2[i])
    

    # 初始化 selenium
    driver = initSelenium(proxy=None)
    handles = driver.window_handles


    # 寫入欄位名稱
    '''
    with open('output.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['模組','表格名稱','表格中文說明','中文名稱','欄位名稱','英文名稱','主鍵','資料型態','長度' ,'外部索引','Description','Main Category','Sub Category','Table type','備註'])
    '''

    while len(modellist) != 0 :
        table = modellist.pop(0)
        if (table not in finished_list) and (table not in ['nan',None]) :
            try :
                n_check_table_list,handles = getTableInfo(driver,handles,table,newdict)
                for i in n_check_table_list:
                    try:
                        newdict[i] = str(newdict[table])
                    except:
                        newdict[i] = 'reload'
                modellist = n_check_table_list + modellist
                finished_list.append(table)

            except Exception as e:
                print(e)
                with open('nodata2.txt','a') as f:
                    f.write(str(table) + '\r')

    driver.quit()