# cd D:\WebSite\ITTS-EP-WEBAPI\scheduleFile;
cd E:\work\crawler\manufacturer_details\crawler.ps1
venv\\Scripts\\activate;

# crawler black list
python crawler_black_list.py;
# crawler judbook
python crawler_judbook.py;
# crawler invoic use
python crawler_invoice_use.py;
# get API
Invoke-RestMethod 'https://ep.itts.com.tw:886/Function/UpdateSupplierExternal' `
-Method 'GET' `
-Headers @{ "Content-Type" = "application/json"; }