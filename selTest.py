from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
import time
from bs4 import BeautifulSoup
import random
import json
import uuid
from threading import Thread
import re

HEIGHT = 0    
HOSTLIST = []
SUGGESTED = []
scrapedData = {}
PATH = "C:\Program Files (x86)\chromedriver.exe"

ID = str(uuid.uuid4()).split('-')[0]

def setUserAgent():
    ua = UserAgent()
    userAgent = ua.random
    #print(userAgent)
    options.add_argument(f'user-agent={userAgent}')

options = Options()
setUserAgent()
options.add_argument('--disable-blink-features=AutomationControlled')
#options.add_argument("user-data-dir=selenium")
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options,executable_path=PATH)

def scrape(names, host=True):
    for name in names:
        if name in scrapedData:
            pass
        else:
            setUserAgent()
            time.sleep(random.randrange(1,4))
            try:
                ADDED = False
                search = driver.find_element_by_name('q')
                search.clear()
                search.send_keys(f'{name}')
                time.sleep(random.randrange(1,4))
                search.send_keys(Keys.ENTER)

                time.sleep(random.randrange(2,6))

                results=driver.find_element_by_css_selector("a.tiktok-1bltwtr-StyledAvatarUserLink.e12ixqxa2")
                #results=driver.find_element_by_css_selector("div.tiktok-133zmie-DivLink.e12ixqxa0").text shows name and follower count maybe good for conditional
                results.click()

                time.sleep(random.randrange(2,6))
                results = driver.find_elements_by_css_selector("div.number")
                followers = results[1].text.split('\n')[0]
                print(followers)
                '''if 'M' in followers:
                    if str(name) not in HOSTLIST or str(name) not in SUGGESTED:
                        scrapedData[f'{name}'] = {"followers":f"{followers}","email":""}
                        ADDED = False'''
                if 'K' in followers:
                    amount = followers[:-1]
                    if float(amount)>=100 and float(amount) <= 599:
                        scrapedData[f'{name}']= {"followers":f"{followers}","email":""}
                        ADDED = True
                if ADDED:
                    description = driver.find_element_by_css_selector("h2.share-desc.mt10").text
                    email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+",description)
                    if email and len(email.group())>1 and email.group()[0]!='@':
                        scrapedData[f'{name}']['email'] = email.group()
                        print(email.group(),' added')
            except Exception as e:
                print(e)
                driver.refresh()
            if host and ADDED:
                    try:
                        time.sleep(random.randrange(2,6))

                        results = driver.find_elements_by_css_selector("span.jsx-2659493321.user-item-inner")
                        if results:
                            for user in results:
                                username = user.text.split('\n')[0]
                                if username != '' and username not in SUGGESTED:
                                    print(username)
                                    SUGGESTED.append(username)
                        else:
                            results = driver.find_elements_by_css_selector("div.jsx-2333069902.user-container")
                            for user in results:
                                if user.text != '' and user.text not in SUGGESTED:
                                    print(user.text)
                                    SUGGESTED.append(user.text)
                    except :
                        pass        
            if random.randrange(0,3)==0:
                try:
                    driver.find_element_by_css_selector("div.jsx-969240130.video-card-mask").click()
                    time.sleep(random.randrange(2,10))
                    driver.back()
                except :
                    pass         
            time.sleep(random.randrange(1,4))


driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.get("http://tiktok.com/")

time.sleep(12)

driver.refresh()
time.sleep(5)

for i in range(100):
    HEIGHT = HEIGHT + 1500
    driver.execute_script(f"window.scrollTo(0,{HEIGHT})")
    time.sleep(random.randrange(1,4))

#feed = driver.find_element_by_css_selector('.jsx-668066632')
#for tiktok in feed:
#    username = tiktok.find_element_by_xpath('.//span[@class="lazzyload-wrapper"]/div/div/div[1]/a[1]/h3').text
page = driver.page_source
soup = BeautifulSoup(page,features='html.parser')
for tiktok in soup.find_all('span',{"class":"lazyload-wrapper"}):
    try:
        username = tiktok.find('h3', {"class":"author-uniqueId jsx-4013687392"})
        if username.text != '':
            HOSTLIST.append(username.text)
            print(username.text)
    except :
        pass

time.sleep(random.randrange(1,6))

scrape(HOSTLIST)
scrape(SUGGESTED, host=False)
print(scrapedData)

with open(f'tikTok_users_{ID}.json','w') as outfile:
    json.dump(scrapedData,outfile)

driver.quit()