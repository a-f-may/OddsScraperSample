from cmath import tan
from math import inf
from sqlite3 import Timestamp
import time

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import numpy as np
import sys
import os

from googleapiclient.discovery import build

from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from googleapiclient.http import MediaFileUpload

s_init = pd.read_csv("resources/scripts/s_init.csv")
t_init = pd.read_csv("resources/scripts/t_init.csv")


#Get param from rails
args = sys.argv





def all_trifecta_pattern_odds(id):
    
    time.sleep(5)
    interval = 30
    options= Options()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    options.add_argument("--headless")

    browser = webdriver.Chrome(ChromeDriverManager().install(),options=options) 
    browser.implicitly_wait(interval) 


    browser.set_page_load_timeout(10)
    race_id = id
                
    url = 'https://race.netkeiba.com/odds/index.html?type=b1&race_id='\
    + str(race_id) + '&rf=shutuba_submenu'  

    browser.get(url)


    odds_win, odds_fukusyo = {}, {}, 
    odds_trifecta = {}

    table_tag_list = browser.find_elements_by_css_selector("table.RaceOdds_HorseList_Table")
    cnt = 0
    for table_tag in table_tag_list:
        html = table_tag.get_attribute('outerHTML')
        if cnt == 0:
            win_table = pd.read_html(html)[0]
        elif cnt == 1:
            fukusyo_table = pd.read_html(html)[0]
        cnt += 1
                
    horse_num = len(win_table)
                

    win_df = pd.DataFrame(data={'horse_num': win_table['馬番'],
                                            'odds': win_table['オッズ'],
                                            'race_ID': [race_id] * horse_num})
    fukusyo_df = pd.DataFrame(data={'horse_num': fukusyo_table['馬番'],
                                                'odds': fukusyo_table['オッズ'],
                                                'race_ID': [race_id] * horse_num})
                            

    odds_win[race_id] = win_df
    odds_fukusyo[race_id] = fukusyo_df

    text = browser.find_element_by_partial_link_text('3連単')
    browser.execute_script('arguments[0].scrollIntoView(true);', text)
    text.click()
    time.sleep(3)


    # 基準とする競走馬を選択する
    horse_list = [str(x) + ' ' + str(y)\
                for x, y in zip(win_table['馬番'], win_table['馬名'])]
                
    # 初期値
    pattern_list, odds_list = [], []
    cnt = 0
                
    for horse in horse_list:
                    
    # プルダウンを選択
        dropdown = browser.find_element_by_id('list_select_horse')
        Select(dropdown).select_by_visible_text(horse)
        time.sleep(3)

                    # オッズテーブルを作成
        table_tag_list = browser.find_elements_by_css_selector("table.Odds_Table")
        for table_tag in table_tag_list:
            html = table_tag.get_attribute('outerHTML')
            odds_table = pd.read_html(html)[0]
                        # 賭け方のパターン
            pattern_list += [str(win_table['馬番'].iloc[cnt, ]) + '-'\
                                        + str(odds_table.columns[0]) + '-'\
                                        + str(x)\
                                        for x in odds_table.iloc[:, 0]]
                        # オッズ
            odds_list += list(odds_table.iloc[:, 1])
                        
        cnt += 1
                    
                # オッズテーブル                      
    sanrentan_df = pd.DataFrame(data={'pattern': pattern_list,
                                                'odds': odds_list,
                                                'race_ID': [race_id] * len(odds_list)})
                                                
                
    # 辞書型変数に格納
    odds_trifecta[race_id] = sanrentan_df
    sanrentan_df["日.R"] = race_id[-4:-2] + "日目" + race_id[-2:] + "R"
    browser.quit()

    return sanrentan_df


def win_odds(id):
    "heroku上で動かすための設定"
    time.sleep(5)
    interval = 30
    options= Options()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    options.add_argument("--headless")
    # Google Chromeを起動 ---------------------- (※1)
    browser = webdriver.Chrome(ChromeDriverManager().install(),options=options) 
    browser.implicitly_wait(interval) 

    race_id = id
                # ページを開く
    url = 'https://race.netkeiba.com/odds/index.html?type=b1&race_id='\
    + str(race_id) + '&rf=shutuba_submenu'            
    browser.set_page_load_timeout(10)
    RETRIES = 3

    
    browser.get(url)



    odds_win, odds_fukusyo = {}, {}
    odds_trifecta = {}

    table_tag_list = browser.find_elements_by_css_selector("table.RaceOdds_HorseList_Table")
    cnt = 0
    for table_tag in table_tag_list:
        html = table_tag.get_attribute('outerHTML')
        if cnt == 0:
            win_table = pd.read_html(html)[0]
        elif cnt == 1:
            fukusyo_table = pd.read_html(html)[0]
        cnt += 1
                
    horse_num = len(win_table)
                
                
    win_df = pd.DataFrame(data={'horse_num': win_table['馬番'],
                                            'odds': win_table['オッズ'],
                                            'race_ID': [race_id] * horse_num})   
    win_df.index = np.arange(1,len(win_df)+1)
    all_trifecta_pattern_odds = win_df.T.iloc[1:2]
    all_trifecta_pattern_odds["id"] = id
    browser.quit()


    return  all_trifecta_pattern_odds


def make_race_id(y,field,time,day,round):
    field_hash = {
    "札幌":"01",
    "函館":"02",
    "福島":"03",
    "新潟":"04",
    "東京":"05",
    "中山":"06",
    "中京":"07",
    "京都":"08",
    "阪神":"09",
    "小倉":"10"
    }
    #print(field_hash[field])
    return str(y)+field_hash[field]+str(time).zfill(2)+str(day).zfill(2)+str(round).zfill(2)    

# %%

    

# %%


# %%

def odds_won_the_races(id,  all_trifecta_pattern_odds):

    race_id = id
    
    url = "https://race.netkeiba.com/race/result.html?race_id="+str(race_id)+"&rf=race_list"
    #display(url)


    win_df = pd.read_html(url)[1].iloc[0:1]
    trifecta_df = pd.read_html(url)[2].iloc[3:4]

    win_df["odd"] = win_df[2].str.replace("円","").str.replace(",","").astype(int) / 100
    trifecta_df["odd"] = trifecta_df[2].str.replace("円","").str.replace(",","").astype(int) / 100

    


    
    all_trifecta_pattern_odds =  all_trifecta_pattern_odds.append({
    'trifecta_pattern': trifecta_df[1].iloc[0],
    'trifecta_odds': trifecta_df["odd"].iloc[0],
    'win_pattern': win_df[1].iloc[0],
    'win_odds': win_df["odd"].iloc[0],
    'race_ID':race_id,
    },ignore_index=True)

    #display    all_trifecta_pattern_odds)

    return  all_trifecta_pattern_odds




# %%
RETRYLIM = 1000
def win_oneday(y=2022,field="新潟",round=3,day=1):
    id = make_race_id(y,field,round,day,1)
    
    i = 0
    
    while True: 
        
        try:
            all_trifecta_pattern_odds = win_odds(id)
                

        except TimeoutException:
        #全部NaN、で１行のDFを返す
            if i < RETRYLIM:
                i = i + 1
                time.sleep(10)
            else:
                all_trifecta_pattern_odds = t_init
                break
        
        else:
            break
           

  
    
    for j in range(2,13):
        
        id = make_race_id(y,field,round,day,j)
        print(id)
        i = 0
        while True:
            try:
                win_df = win_odds(id)

            except TimeoutException:
                
                if i < RETRYLIM:
                    i = i + 1
                    time.sleep(10)
                else:
                    win_df = t_init
                    break

            else:
                break
                

        all_trifecta_pattern_odds = pd.concat([all_trifecta_pattern_odds,win_df])
    
        all_trifecta_pattern_odds.to_csv("../csv/tes.csv")

    
    return  all_trifecta_pattern_odds


def trifecta_oneday(y,field,round,day):
    id = make_race_id(y,field,round,day,1)
    i = 0
    while True: 
        try:
            all_trifecta_pattern_odds = (id)
                

        except TimeoutException:
        #全部NaN、で１行のDFを返す
            if i < RETRYLIM:
                i = i + 1
                time.sleep(10)
            else:
                all_trifecta_pattern_odds = s_init
                break
        else: 
            break

    for j in range(2,13):
        id = make_race_id(y,field,round,day,j)

        i = 0
        while True: 
            try:
                sanrentan_df = (id)
                    

            except TimeoutException:
            #全部NaN、で１行のDFを返す
                if i < RETRYLIM:
                    i = i + 1
                    time.sleep(10)
                else:
                    sanrentan_df = t_init
                    break
            else: 
                break

        all_trifecta_pattern_odds = pd.concat([all_trifecta_pattern_odds,sanrentan_df])

    
    return  all_trifecta_pattern_odds


def trifecta_onetime(y,field="札幌",round=2,day=1):

    all_trifecta_pattern_odds = trifecta_oneday(y,field,round,1)

    for i in range(2,day+1):


        sanrentan_df = trifecta_oneday(y,field,round,i)


        all_trifecta_pattern_odds = pd.concat([all_trifecta_pattern_odds,sanrentan_df])






    df2 =   all_trifecta_pattern_odds["pattern"].str.split("-",expand=True)
    all_trifecta_pattern_odds = pd.concat([all_trifecta_pattern_odds,df2],axis=1)
    all_trifecta_pattern_odds =  all_trifecta_pattern_odds.rename(columns={0:"１着",1:"２着",2:"3着"})
    return  all_trifecta_pattern_odds

def win_onetime(y=2022,field="札幌",round=2,day=8):
    all_trifecta_pattern_odds = win_oneday(y,field,round,1)
    for i in range(2,day+1):
        win_df = win_oneday(y,field,round,i)
        all_trifecta_pattern_odds = pd.concat([all_trifecta_pattern_odds,win_df])





        all_trifecta_pattern_odds.to_csv("../csv/tes.csv")
    return  all_trifecta_pattern_odds


        
#回ごとの全オッズのCSV作成
year = int(args[1])
field = args[2]
times = int(args[3])
day = int(args[4])
MAKEWHAT = int(args[5])

"""
f=open("tmp/test.txt","w")#これをドライブにアップできるか
for i in range(5):
    f.write(args[i]+"_")
f.close
"""


def upload_to_drive(upload_file_path):

    SCOPES = ['https://www.googleapis.com/auth/drive']


    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'resources/scripts/service_account.json', SCOPES
    )
    http_auth = credentials.authorize(Http())

    drive_service = build('drive', 'v3', http=http_auth)

    upload_file_name = os.path.basename(upload_file_path)
    mine_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    folder_id = '1jtFyhZuFJ0wMl4US4819Mfvndl_3PCes'

    media = MediaFileUpload(upload_file_path, mimetype=mine_type, resumable=True)

    file_metadata = {
        'name': upload_file_name,
        'mimeType': mine_type,
        'parents': [folder_id]
    }
    file = drive_service.files().create(
            body=file_metadata, 
            media_body=media 
                ).execute()

    print(file['id'])

#単勝
if MAKEWHAT == 0 or MAKEWHAT == 2:
    tdf = win_onetime(year,field,times,day)
    tdf.to_excel("tmp/win{0}_{1}_{2}_{3}.xlsx".format(str(year),field,str(times),str(day)))
    tansyo_file_path = "tmp/win{0}_{1}_{2}_{3}.xlsx".format(str(year),field,str(times),str(day))
    upload_to_drive(tansyo_file_path)

#三連単
if MAKEWHAT == 1 or MAKEWHAT == 2:
    sdf = trifecta_onetime(year,field,times,day)
    sdf.to_excel("tmp/sanrentan{0}_{1}_{2}_{3}.xlsx".format(str(year),field,str(times),str(day)))
    sanrentan_file_path = "tmp/sanrentan{0}_{1}_{2}_{3}.xlsx".format(str(year),field,str(times),str(day))
    upload_to_drive(sanrentan_file_path)

# %%

# %%


# %%


# %%


# %%


# %%

# %%



