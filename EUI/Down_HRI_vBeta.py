import requests
import wget
from bs4 import BeautifulSoup as bs
import os
from tqdm import tqdm
import time
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd

file_path = "/userhome/youn_j/Code_DEMHRI/download/SolarOrbiter_state_250320.xlsx"
df = pd.read_excel(file_path) 
xls = pd.ExcelFile(file_path)
df_table1 = pd.read_excel(file_path, sheet_name='table1')


data_name_list = df_table1['dataname'].tolist()
start_list = df_table1['start'].tolist()
end_list = df_table1['end'].tolist()
filter_list = df_table1['filter'].tolist() if 'filter' in df_table1.columns else []
gaincomb_list = df_table1['gaincomb'].tolist()
duration_list = df_table1['duration (s)'].tolist()
cadence_list = df_table1['cadence (s)'].tolist()



data_lists = {
    "data_name": data_name_list,
    "start": start_list,
    "end": end_list,
    "filter": filter_list,
    "gaincomb": gaincomb_list,
    "duration": duration_list,
    "cadence": cadence_list
}

link_parent = "https://www.sidc.be/EUI/data/L1/"
out_path = "/userhome/youn_j/Dataset/HRI/174/"
os.makedirs(out_path, exist_ok=True)

link = None
download_list = []

start_date = date(2020, 5, 20)
end_date = date(2024, 7, 8)
list_len = len(data_lists['data_name'])

print(list_len)

for i in range(list_len-1,0,-1): #10, 9, 8, ...
    if start_date <= end_date:
        print(i)
        
        if data_lists['data_name'][i] == 'hrieuv174': # discard hrieuvopen
            
            while start_date != data_lists['start'][i].date(): #if st_date == data_list >> pass
                start_date = start_date + relativedelta(days=1)
            
            # download data selection
            _day = str(start_date.strftime("%Y/%m/%d"))
            if link != link_parent + _day: # if next i step is different date w/ before one's
                link = link_parent + _day
                j = 1
                for _ in range(5): #wait for crowl
                    try:
                        page = requests.get(link, timeout=10)
                        html = bs(page.text, "html.parser")
                    except:
                        print('retry',j,'/ 3')
                        if j == 4:
                            print(_day)
                            raise SystemError
                        j += 1
                        time.sleep(10)
                        continue
                        
            print(link)
            _list = html.find_all('a') #get html list
            
            if data_lists['duration'][i] >= 720:
                dur_div_720 = int(data_lists['duration'][i]//720)
            else:
                dur_div_720 = 1

            print(dur_div_720)
            for t in range(dur_div_720): #purposed data
                Next_data = data_lists['start'][i] + t * relativedelta(seconds=720)
                Next_data = Next_data.strftime("%Y%m%dT%H%M")
                
                for k in range(len(_list)): #html list
                    file = _list[k]
                    _name, extension = os.path.splitext(file["href"])
                    if extension != '.fits':
                        continue

                    if 'solo_L1_eui-hrieuv174-image_'+Next_data in _name :
                        print('solo_L1_eui-hrieuv174-image_'+Next_data)
                        download_list.append(link + "/" +  str(file['href']))
                        break

                    else: 
                        pass
#                         print("UNEXPECTED!!:  "+ 'solo_L1_eui-hrieuv174-image_' + Next_data)
#                         print("compare with:  "+ str(file['href']))
                
        else:
            print("HRIEUVopen")
            continue
    else:
        break
        
        
# download MAIN
print("{0} files will be downloaded...".format(len(download_list)))
for _fits in tqdm(download_list):
    try:
        wget.download(_fits, out=out_path)
    except:
        print(_fits, "is not available")