
"""
@author: youn_j
"""

# modules
import requests
import wget
from bs4 import BeautifulSoup as bs
import os
from tqdm import tqdm
import time
from datetime import date
from dateutil.relativedelta import relativedelta

import argparse
parser = argparse.ArgumentParser(description='')
parser.add_argument('-wl', '--wave', default= None , type=int)
args = parser.parse_args() 

if args.wave == None:
    raise MissingWaveError("Please enter the wavelength that you want to download")


# args.wave = 131 #int
wvln_path = dict({ 93:'suvi-l1b-fe094',  94:'suvi-l1b-fe094', 131:'suvi-l1b-fe131', 171:'suvi-l1b-fe171', \
                  195:'suvi-l1b-fe195', 284:'suvi-l1b-fe284', 304:'suvi-l1b-he304', 305:'suvi-l1b-he304' })
link_parent = "https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/goes18/l1b/{}/".format(wvln_path[args.wave])
out_path = '/userhome/youn_j/Dataset/SUVI/GOES18/{}/'.format(args.wave)
os.makedirs(out_path, exist_ok=True)

download_list = []
start_date = date(2023, 1, 1)
end_date = date(2024, 12, 31)
print("START")
while start_date <= end_date:
    _day_folder = str(start_date.strftime("%Y/%m/%d"))
    _day_file = str(start_date.strftime("%Y%j"))
    print(_day_file)
    link = link_parent+_day_folder+'/'
    j = 1
    for i in range(5):
        try:
            page = requests.get(link, timeout=10) 
        except:
            print('retry',j,'/ 3')
            if j == 4:
                print(day_file)
                raise SystemError
            j += 1
            time.sleep(10)
            continue
            
            
    html = bs(page.text, "html.parser")
    print(page.status_code) #200: successful connection , 404: Fail    
    
    if page.status_code == 404:
        start_date = start_date + relativedelta(days=1)
        continue
    _list = html.find_all('a')
    for i in range(len(_list)):
        file = _list[i]
        _name, extension = os.path.splitext(file["href"])
        try:
            img_end = int(_name[39:52])
            img_start = int(_name[23:36])
            if (f's{_day_file}00' in _name) and (img_end - img_start >=1) :
                print(str(file['href']))
                download_list.append(link + str(file['href']))
                break
        except:
            continue
            

    start_date = start_date + relativedelta(days=1)

# download
print("{0} files will be downloaded...".format(len(download_list)))
for _fits in tqdm(download_list):
    try:
        wget.download(_fits, out=out_path)
    except:
        print(_fits, "is not available") 