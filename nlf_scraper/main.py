from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import time
from bs4 import BeautifulSoup
import random
import json
import uuid
from dbConnector import DBConnector
import re


CURRENT_WEEK = 15
CURRENT_YEAR = '2021'
PATH = './chromedriver.exe'
ID = str(uuid.uuid4()).split('-')[0]
SECONDS = 10
RESULT = 0
url = "https://www.nfl.com/games/vikings-at-cardinals-2015-reg-14"
YEARS = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']
WEEK = 0
DB = 'nfl'
pattern = re.compile(r"'|\"")


def set_user_agent(options:Options) -> None:
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')

def start(driver:webdriver.Chrome, **kwargs) -> None:
    global RESULT
    global url
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get(url)
    while True:
        if  RESULT == 1:
            print('success')
            RESULT = 0
            break
        try:
            driver.refresh()
            time.sleep(SECONDS)
            RESULT = begin_scrape(driver, s_year = kwargs['s_year'], g_id = kwargs['g_id'], my_db = kwargs['my_db'])
        except Exception as e: 
            print('---ERROR----\n',e)

def begin_scrape(driver:webdriver.Chrome, **kwargs) -> int:
    global DB
    global pattern
    driver_cards = [i for i in driver.find_elements(By.CLASS_NAME,'css-cursor-18t94o4.css-view-1dbjc4n.r-cursor-1loqt21.r-touchAction-1otgn73.r-transitionProperty-1i6wzkk.r-userSelect-lrvibr')[1:]
    if not ('Download Game Book' in i.text or 'GEAR UP FOR' in i.text or 'Subscribe' in i.text)]
    driver.execute_script("window.scrollTo(0,300)")
    for i in driver_cards:
        i.click()
    driver_card_drive_desc = [i for i in driver.find_elements(By.CLASS_NAME,'css-view-1dbjc4n.r-backgroundColor-15dxrt1.r-paddingHorizontal-1pn2ns4') if 'Scoring Play:' not in i.text]
    # for i in driver_card_drive_desc:
    #     print('vvv',i.text)
    size1 = len(driver_cards)
    size2 = len(driver_card_drive_desc)
    if size1==size2 and size1 !=0:
        print('both list lengths are equal')
        zipped = zip(driver_cards, driver_card_drive_desc)
        for x,y in zipped:
            print('Drive\n',x.text+'\nDrive Description\n',y.text+'\n','-'*15)
            x_text = pattern.sub(r"",x.text)
            y_text = pattern.sub(r"",y.text)
            kwargs['my_db'].execute(kwargs['my_db'].insertIntoTable(f"pbp_{kwargs['s_year']}",season_id=kwargs['g_id'],year=kwargs['s_year'],drive=x_text,description=y_text),DB)
        return 1
    else:
        print('lists not same size')
        return 0

def table(my_db:DBConnector,db_name) -> None:
    global YEARS
    ans = input("\nschedule or pbp?\n")
    match ans.lower():
        case 'schedule':
            for i in YEARS:
                name = f"schedule_{i}"
                my_db.execute(my_db.createTablestring(name,["week SMALLINT NOT NULL", "day VARCHAR(20) NOT NULL",
                 "date VARCHAR(50) NOT NULL", "time VARCHAR(50) NOT NULL", "teamOne VARCHAR(100) NOT NULL, at BOOL NOT NULL", "teamTwo VARCHAR(100) NOT NULL"]),db_name)
        case 'pbp':
            for i in YEARS:
                name = f"pbp_{i}"
                my_db.execute(my_db.createTablestring(name,["season_id INT NOT NULL", "year VARCHAR(10) NOT NULL", "drive TEXT NOT NULL", "description TEXT NOT NULL"]), db_name)
        case _: print("not valid try again\n")
            
def insert(year,my_db:DBConnector,db_name):
    with open(f'./seasons_schedule/{year}.csv') as file:
                for line in file.readlines()[1:]:
                    line = line.split(',')
                    at=False
                    if line[5] == '@':
                        at=True
                    my_db.execute(my_db.insertIntoTable(f"schedule_{year}", week=int(line[0]), day=line[1], date=line[2], time=line[3], teamOne=line[4], at=at, teamTwo=line[6]),db_name) 

def insert_to_schedule(my_db:DBConnector,db_name) -> None:
    global YEARS
    ans = input("Give start Year or press enter to start from 2012 use --once to only do that season\n")
    year = ans.split(' ')[0] if ans != '' else None
    match year:
        case '2012' | '2013' | '2014' | '2015' | '2016' | '2017' | '2018' | '2019' | '2020' | '2021':
            if '--once' in ans:
                insert(year,my_db, db_name)
            else:
                for i in YEARS[YEARS.index(year):]:
                    insert(i,my_db,db_name)
        case _:
            for i in YEARS:
                insert(i,my_db, db_name)
    
    # if 'start' in kwargs:
    #     for i in YEARS[start:]:
    #         with open(f'./seasons_schedule/{i}.csv') as file:
    #             for line in file.readlines()[1:]:
    #                 line = line.split(',')
    #                 at=False
    #                 if line[5] == '@':
    #                     at=True
    #                 my_db.execute(my_db.insertIntoTable(f"schedule_{i}", week=int(line[0]), day=line[1], date=line[2], time=line[3], teamOne=line[4], at=at, teamTwo=line[6]),db_name)
    # else:
    #     for i in YEARS:
    #         with open(f'./seasons_schedule/{i}.csv') as file:
    #             for line in file.readlines()[1:]:
    #                 line = line.split(',')
    #                 at=False
    #                 if line[5] == '@':
    #                     at=True
    #                 my_db.execute(my_db.insertIntoTable(f"schedule_{i}", week=int(line[0]), day=line[1], date=line[2], time=line[3], teamOne=line[4], at=at, teamTwo=line[6]),db_name)

def print_season(season_year:str, my_db:DBConnector, db_name:str) -> None:
    result = my_db.execute(my_db.selectAllFrom(f"schedule_{season_year}"),db_name)
    print(result)

def set_url(year:str, id:str, my_db:DBConnector, db_name:str):
    global url
    if isinstance(id, str) and not id.isnumeric():
        print('not a numeric value for id')
        return
    result = my_db.execute(my_db.selectAllFrom(f"schedule_{year}",f"id={id}"),db_name)[0]
    teamOne = result[5]
    teamTwo = result[7]
    if year>'2019':
        if "Washington" in teamOne:
            teamOne = teamOne.split(' ')
            teamOne = f"{teamOne[1]}-{teamOne[2]}"
            teamTwo = teamTwo.split(' ')[-1]
        elif "Washington" in teamTwo:
            teamTwo = teamTwo.split(' ')
            teamTwo = f"{teamTwo[1]}-{teamTwo[2]}"
            teamOne = teamOne.split(' ')[-1]
        else:
            teamOne = teamOne.split(' ')[-1]
            teamTwo = teamTwo.split(' ')[-1]
    else:
        teamOne = teamOne.split(' ')[-1]
        teamTwo = teamTwo.split(' ')[-1]
    if result[6]:
        url = f"https://www.nfl.com/games/{teamOne.lower()}-at-{teamTwo.lower()}-{year}-reg-{result[1]}"
    else:
        url = f"https://www.nfl.com/games/{teamTwo.lower()}-at-{teamOne.lower()}-{year}-reg-{result[1]}"


def select_url(my_db:DBConnector, db_name:str) -> None:
    global YEARS
    print(YEARS,'\n')
    year = input("which year ")
    if year not in YEARS:
        print('invalid year try again')
        return
    print_season(year, my_db, db_name)
    
    id = input("what game id would you like to set ")
    if id >= 280:
        print("not valid id for game")
        return
    set_url(year,id, my_db, db_name)
    
def games_upto_now(driver: webdriver.Chrome, my_db:DBConnector, db_name:str, **kwargs) -> None:
    global YEARS
    global CURRENT_WEEK
    global CURRENT_YEAR
    if 'start' in kwargs:
        for i in YEARS[YEARS.index(kwargs['start']):]:
            result = my_db.execute(my_db.selectAllFrom(f"schedule_{i}"),db_name)
            for x in result:
                print(x[0], ' ', x[1])
                if i < CURRENT_YEAR:
                    print(f"Season {i} week {x[1]}")
                    set_url(i,x[0], my_db, db_name)
                    start(driver, s_year = i, g_id = x[0], my_db = my_db)
                elif i == CURRENT_YEAR and x[1] < CURRENT_WEEK:
                    print(f"Season {i} week {x[1]}")
                    set_url(i,x[0], my_db, db_name)
                    start(driver, s_year = i, g_id = x[0], my_db = my_db) 
    else:
        for i in YEARS:
            result = my_db.execute(my_db.selectAllFrom(f"schedule_{i}"),db_name)
            for x in result:
                print(x[0], ' ', x[1])
                if i < CURRENT_YEAR:
                    print(f"Season {i} week {x[1]}")
                    set_url(i,x[0], my_db, db_name)
                    start(driver, s_year = i, g_id = x[0], my_db = my_db)
                elif i == CURRENT_YEAR and x[1] < CURRENT_WEEK:
                    print(f"Season {i} week {x[1]}")
                    set_url(i,x[0], my_db, db_name)
                    start(driver, s_year = i, g_id = x[0], my_db = my_db)


def main() -> None:
    global url
    global YEARS
    global DB
    my_db = DBConnector(path='../fastApi/.env')
    options = Options()
    set_user_agent(options)
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    while True:
        ans = input("""
What would you like to do?
Quit -> q
create DB -> db
start scraper -> sc
create tables for seasons -> tb
insert data to season schedule -> insc
set look for game to set - > sg
Test the function -> test
temp fix -> fix ***BETA\n""")
        match ans.lower():
            case 'q': break
            case 'db': my_db.execute(my_db.createDBstr(DB))
            case 'tb': table(my_db,DB)
            case 'sc':
                driver = webdriver.Chrome(options=options,executable_path=PATH)
                start(driver)
            case 'insc': insert_to_schedule(my_db,DB)
            case 'sg': select_url(my_db,DB)
            case 'test': 
                ans = input('what year to start? default 2012\n')
                driver = webdriver.Chrome(options=options,executable_path=PATH)
                if ans == '':
                    games_upto_now(driver,my_db,DB)
                elif ans.isnumeric():
                    games_upto_now(driver,my_db,DB,start=ans)
                else:
                    print('not valid try again\n')
                driver.close()
            case 'fix': 
                year = input('enter year\n')
                if year.isnumeric() and year in YEARS:
                    id = input('enter game id to\n')
                    if id.isnumeric():
                        set_url(year,id,my_db,DB)
                        driver = webdriver.Chrome(options=options,executable_path=PATH)
                        start(driver,my_db=my_db,s_year=year,g_id=id)
                else:
                    print('invalid year')
                driver.close()
            case _ : print('Sorry not valid answer')
        print('\ndone')
if __name__ == '__main__':
    main()
