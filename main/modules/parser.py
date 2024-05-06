import re
import asyncio
from main.modules.schedule import update_schedule
from main.modules.usschedule import update_schedulex
from main.modules.utils import status_text
from main import status
from main.modules.db import get_animesdb, get_uploads, save_animedb
import feedparser
from main import queue
from main.inline import button1

def trim_title(title: str):
    pattern = r"^(.*?)\s*(S\d+E\d+)\s*(.*?)\s\d{3,4}p\s(.*?)\sWEB-DL.*?\((.*?),.*?\)$"
    match = re.match(pattern, title)
    if match:
        titler, episode, extra, source, at = match.groups()
        if at=="Dual-Audio":
            if source=="HIDI":
                source = source.replace("HIDI", "HIDIVE")
                title = f"[AniDL] {titler.strip()} - {episode.strip()} [Web ~ {source.strip()}][480p x265 10Bit][Dual-Audio ~ Opus].mkv"
            else:
                title = f"[AniDL] {titler.strip()} - {episode.strip()} [Web ~ {source.strip()}][480p x265 10Bit][Dual-Audio ~ Opus].mkv"
        else:
            if source=="HIDI":
                source = source.replace("HIDI", "HIDIVE")
                title = f"[AniDL] {at.strip()} - {episode.strip()} [Web ~ {source.strip()}][480p x265 10Bit][Dual-Audio ~ Opus].mkv"
            else:
                title = f"[AniDL] {at.strip()} - {episode.strip()} [Web ~ {source.strip()}][480p x265 10Bit][Dual-Audio ~ Opus].mkv"
    return title

def multi_sub(title: str):
    subtitle = title.split()[-1] 
    return subtitle

def parse():
    a = feedparser.parse("https://nyaa.si/?page=rss&q=dual&c=0_0&f=0&u=varyg1001")
    b = a["entries"]
    data = []    

    for i in b:
        item = {}
        item['title'] = trim_title(i['title'])
        item['size'] = i['nyaa_size']   
        item['link'] = "magnet:?xt=urn:btih:" + i['nyaa_infohash']
        data.append(item)
        data.reverse()
    return data

async def auto_parser():
    while True:
        try:
            await status.edit(await status_text("Parsing Rss, Fetching Magnet Links..."),reply_markup=button1)
        except:
            pass

        rss = parse()
        data = await get_animesdb()
        uploaded = await get_uploads()

        saved_anime = []
        for i in data:
            saved_anime.append(i["name"])

        uanimes = []
        for i in uploaded:
            uanimes.append(i["name"])
        
        for i in rss:
            if i["title"] not in uanimes and i["title"] not in saved_anime:
                if ".mkv" in i["title"] or ".mp4" in i["title"]:
                    title = i["title"]
                    await save_animedb(title,i)

        data = await get_animesdb()
        for i in data:
            if i["data"] not in queue:
                queue.append(i["data"])    
                print("Saved ", i["name"])   

        try:
            await update_schedulex()
        except:
            pass

        await asyncio.sleep(60)
