from bs4 import BeautifulSoup
from multiprocessing import Pool
from multiprocessing import Process
import requests, csv, re, lxml, io, os, time, base64
import sqlalchemy as sql, pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

#Download selenium chromedriver
#Set an environment variable for it

def tx_scrape():
    start = time.time()
    df =pd.DataFrame()
    cameras = pd.DataFrame()

    # get content
    options = webdriver.ChromeOptions() 
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    # options.add_argument('disable-infobars')
    driver = webdriver.Chrome(options=options, executable_path=os.environ['HELP'])
    driver.get("http://its.txdot.gov/ITS_WEB/FrontEnd/default.html?r=AMA&p=Amarillo&t=cctv")
    # WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='divImg']")))
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='regionControl']")))
    page = driver.page_source
    soup = BeautifulSoup(page, 'lxml')
    driver.quit()
    temp = pd.DataFrame()


    #Create List that will allow us to iterate to the next url
    for i in soup.find_all('option'):
        temp = temp.append({ 'value': i.get('value'), 'city': i.contents}, ignore_index=True)
    temp['city'] = temp['city'].map(lambda x: str(x)[:-2])
    temp['city'] = temp['city'].map(lambda x: str(x)[2:])    
    city = temp['city'].values.tolist()
    value = temp['value'].values.tolist()
    city[-1:] = ['Yoakum Area']
    print(city)


    #Grab each subset of images in the url, and then close that url
    for i in range(len(city)):
        ci = city[i]
        va = value [i]
        url = f"http://its.txdot.gov/ITS_WEB/FrontEnd/default.html?r={va}&p={ci}&t=cctv"
        options = webdriver.ChromeOptions() 
        options.add_argument("start-maximized")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        # options.add_argument('disable-infobars')
        driver = webdriver.Chrome(options=options, executable_path=os.environ['HELP'])
        driver.get(url)
        if str(driver.current_url) == 'http://conditions.drivetexas.org/current/':
            print(f'{ci} is broken. Skipping {ci}.')
            driver.quit()
            continue
        else:
            try:
                WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@id, "roadwayList")]')))
                print('First Try')
            except TimeoutError as e:
                WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@id, "roadwayList")]')))
                print(e)
                continue
            page = driver.page_source
            soup=BeautifulSoup(page, 'lxml')
            newdf = pd.DataFrame()
            for s in soup.find_all('div', {'class': 'SelectedRoadway'}):
                newdf = newdf.append({'hwlist': s.get('id')}, ignore_index = True)
            for r in soup.find_all('div', {'class': 'Roadway'}):
                newdf = newdf.append({'hwlist': r.get('id')}, ignore_index = True)
            hwlist = newdf['hwlist'].values.tolist()
            try:
                for hw in hwlist:
                    print ('next')
                    print(hw)
                    button = driver.find_element_by_xpath(("//div[(@id= '%s')]") % hw)
                    # hw = driver.find_element_by_css_selector(".button[value='IH35']").click()
                    button.click()
                    # hw = driver.find_element_by_css_selector('div') #div:nth-child(5) > div:nth-child(1) > div > div > div:nth-child(1) > div:nth-child(0)')
                    time.sleep(3)
                    page = driver.page_source
                    # print(page)
                    soup = BeautifulSoup(page, 'lxml')
                    print('Checking Loading Pages for ' + ci)
                    x = True
                    count = 0
                    while x is True:
                        if count == 0:
                            for v in soup.find_all('img', {'class' : 'divImg'}):
                                e = soup.find_all('img', {'class' : 'divImg'})
                                print('in for loop (img, {class : divImg})')
                                b = 'http://its.txdot.gov/ITS_WEB/FrontEnd/snapshots/LoadingSnapshot.png'
                                c = 'http://its.txdot.gov/ITS_WEB/FrontEnd/images/snapshotMessage.gif'
                                try:
                                    if b == e[0].get('src'):
                                        driver.refresh()
                                        try:
                                            WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@id, "roadwayList")]')))
                                            print('Refresh complete')
                                        except TimeoutError as e:
                                            WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@id, "roadwayList")]')))
                                            print(e)
                                        time.sleep(7)
                                        page = driver.page_source
                                        soup =BeautifulSoup(page, 'lxml')
                                        print('new soup')
                                    else:
                                        x = False
                                        count+=2
                                        print('success')
                                        break
                                except Exception as e:
                                    print(e)
                                    continue
                    
                        else:
                            x = False
                            print('last iteration')
                            break


                    #parsing 
                    img = pd.DataFrame()
                    des = pd.DataFrame()

                    for v in soup.find_all('img', {'class' : 'divImg'}):
                        img = img.append({'Image_URL': v.get('src')}, ignore_index=True)
                    for j in soup.find_all('div', {'class': 'CameraSnapshotElement'}):
                        des = des.append({'Description': j.get('data-id'), 'City': ci}, ignore_index=True)
                    #dataframe concat
                    df = pd.concat([img, des], axis = 1)
                    cameras = cameras.append(df, ignore_index=True)
            except KeyError as e:
                print(e)
                continue 


            driver.quit()
        
    cameras['UUID'] = range(1, 1 + len(cameras))   
    end = time.time()
    amount = (end - start) / 60
    print(amount)
    # print(f'It took {amount} minutes.)

    cameras['base']= 1000000
    cameras['State']= 'TX'
    cameras['UUID_num'] = cameras['UUID'] + cameras['base'] 
    cameras['UUID'] = cameras['State'] + cameras['UUID_num'].astype(str)

    columns=['base', 'UUID_num']


    cameras.drop(columns, axis = 1, inplace = True)
    print('Cameras df is created')
    tx = cameras.values.tolist()
    
    # return cameras
    return tx

if __name__ == '__main__':

    start = time.time()
    tx = tx_scrape()
    p = Pool(os.cpu_count()-1)
    r = p.map_async(get_imgs, tx)
    r.wait()
    p.close()
    p.join()
    # p.close()
    end = time.time()
    print(f'{(end-start)/60} minutes to complete process.')
