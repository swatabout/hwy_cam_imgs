from bs4 import BeautifulSoup
from fnmatch import fnmatch, filter as fnfilter
import csv, re, lxml, datetime, io, os, time, requests
import sqlalchemy as sql, pandas as pd
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
#Download selenium chromedriver
#Set an environment variable for it

start = time.time()
options = webdriver.ChromeOptions() 
options.add_argument("start-maximized")
# options.add_argument("--headless")
options.add_argument("--disable-extensions")
# options.add_argument('disable-infobars')
driver = webdriver.Chrome(options=options, executable_path=os.environ['HELP'])
driver.get("https://cotrip.org/map.htm#/default?StillCameraId")
WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='tab-pane ng-scope active']")))
time.sleep(4)
page = driver.page_source
soup = BeautifulSoup(page, 'lxml')
lst = []
for i in soup.find_all('div', {'class' : 'app-cam'}):
    lst.append(i.get('id'))
image = []
description= []
comments = []
count=1
if count % 100 == 0:
    driver.quit()
    driver.get("https://cotrip.org/map.htm#/default?StillCameraId")
    WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='tab-pane ng-scope active']")))
    time.sleep(4)
    page = driver.page_source
    soup = BeautifulSoup(page, 'lxml')
    for j in lst:
        print(j)
        button = driver.find_element_by_xpath(("//div[(@id= '%s')]") % j)
        button.click()
        # time.sleep(1)
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        for i in soup.find_all('img'):
            if i.get('ng-src') == None:
                continue
            else:
                j=[i for i in soup.find_all('img') if i.get('ng-src') is not None and fnmatch(i.get('ng-src'), '*dimage*')]
                k=[i for i in soup.find_all('img') if i.get('ng-src') is not None and fnmatch(i.get('ng-src'), '*websvc.coloradosprings.gov/live*')]
        if j==[]:
            for t in range(0,len(k)):
                image.append(k[t]['src'])
                for d in soup.find_all('div', {'class' : 'info-window-wrap ng-scope'}):
                    description.append(d.find('span', {'ng-bind-html': 'camera.Name'}).contents[0])
            for t in range(0,len(j)):
                image.append(j[t]['src'])
                for d in soup.find_all('div', {'class' : 'info-window-wrap ng-scope'}):
                    description.append(d.find('span', {'ng-bind-html': 'camera.Name'}).contents[0])
        else:
            for t in range(0,len(j)):
                image.append(j[t]['src'])
                for d in soup.find_all('div', {'class' : 'info-window-wrap ng-scope'}):
                    description.append(d.find('span', {'ng-bind-html': 'camera.Name'}).contents[0])
        for h in soup.find_all('span', {'ng-if': 'slide.Description'}):
            comments.append(h.contents[0])
        print(count)
        if count == 772:
            break
        else:
            count+=1
        print(f'images : {len(image)}')
        print(f'description : {len(description)}')
        print(f'comments : {len(comments)}')
        driver.delete_all_cookies()
        print('Nom Nom')
else:
    for j in lst:
        print(j)
        button = driver.find_element_by_xpath(("//div[(@id= '%s')]") % j)
        button.click()
        # time.sleep(1)
        try:
            page = driver.page_source
            soup = BeautifulSoup(page, 'lxml')
        except MemoryError:
            driver.refresh()
            time.sleep(2)
            page = driver.page_source
            soup = BeautifulSoup(page, 'lxml')
            button = driver.find_element_by_xpath(("//div[(@id= '%s')]") % j)
            button.click()
        for i in soup.find_all('img'):
            if i.get('ng-src') == None:
                continue
            else:
                j=[i for i in soup.find_all('img') if i.get('ng-src') is not None and fnmatch(i.get('ng-src'), '*dimage*')]
                k=[i for i in soup.find_all('img') if i.get('ng-src') is not None and fnmatch(i.get('ng-src'), '*websvc.coloradosprings.gov/live*')]
        if j==[]:
            for t in range(0,len(k)):
                image.append(k[t]['src'])
                for d in soup.find_all('div', {'class' : 'info-window-wrap ng-scope'}):
                    description.append(d.find('span', {'ng-bind-html': 'camera.Name'}).contents[0])
            for t in range(0,len(j)):
                image.append(j[t]['src'])
                for d in soup.find_all('div', {'class' : 'info-window-wrap ng-scope'}):
                    description.append(d.find('span', {'ng-bind-html': 'camera.Name'}).contents[0])
        else:
            for t in range(0,len(j)):
                image.append(j[t]['src'])
                for d in soup.find_all('div', {'class' : 'info-window-wrap ng-scope'}):
                    description.append(d.find('span', {'ng-bind-html': 'camera.Name'}).contents[0])
        for h in soup.find_all('span', {'ng-if': 'slide.Description'}):
            comments.append(h.contents[0])
        print(count)
        if count == 772:
            break
        else:
            count+=1
        print(f'images : {len(image)}')
        print(f'description : {len(description)}')
        print(f'comments : {len(comments)}')
        driver.delete_all_cookies()
        print('Nom Nom')

driver.quit()
colorado = pd.DataFrame(
    {'image': image,
     'description': description,
     'comments': comments
    })
colorado['state'] = 'CO'
colorado['UUID'] = range(1000000, 1000000 + len(colorado)) 
colorado['UUID'] = colorado['State'] + colorado['UUID'].astype(str)
colorado.to_csv(r'/path/to/Colorado_Traffic_Cameras_1.csv', index = None, header=True)
end = time.time()
print(f'{(end - start)/60} minutes of my life goone')




