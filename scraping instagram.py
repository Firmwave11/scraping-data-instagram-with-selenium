import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pandas as pd 
import re
import string
c = webdriver.Chrome('D:\Chromedriver\chromedriver')

c.get("https://www.instagram.com/jktinfo/")
time.sleep(1)

elem = c.find_element_by_tag_name("body")

no_of_pagedowns = 20

while no_of_pagedowns:
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    no_of_pagedowns-=1

soup = BeautifulSoup(c.page_source, 'html.parser')
body = soup.find('body')
script = body.find('script')
page_json = script.text.strip().replace('window._sharedData =', '').replace(';', '')
def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"                           
                                "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)
data = json.loads(page_json)
doc = pd.DataFrame(data)
result = pd.DataFrame(columns=['Tanggal','Like', 'Komen', 'Video', 'Caption'])
for post in data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
    timestamp = post['node']['taken_at_timestamp']
    likedby = post['node']['edge_liked_by']['count']
    comments = post['node']['edge_media_to_comment']['count']
    isVideo = post['node']['is_video']
    caption = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
    caption2 = deEmojify(caption)
    captionNew = caption2.translate(str.maketrans('','', string.punctuation) )
    result = result.append( {
            'Tanggal' : datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'Like' :likedby,
            'Komen':comments,
            'Video':isVideo,
            'Caption':captionNew.replace("\n", " ").replace("\u2063", "").replace("\xa0", "").replace("\u2049","") }, ignore_index=True)
result
dict2 = result.to_dict(orient='records')
with open('jktinfo.json', 'w') as fp:
    json.dump(dict2, fp, sort_keys=True, indent=4)
