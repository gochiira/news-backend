from time import sleep
from random import randint
from linenotify import LineNotifyClient
import lxml.html
import requests


def getGochiusaNews():
    resp = requests.get(
        "https://gochiusa.com/bloom/news/list00010000.html",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
        }
    )
    resp.encoding = 'utf8'
    page = lxml.html.fromstring(resp.text)
    days = page.xpath("//td[@class='day']/text()")
    texts = page.xpath("//span[@class='new_ic']/a/text()")
    links = page.xpath("//span[@class='new_ic']/a/@href")
    links = [
        link if not link.startswith('../')
        else f'https://gochiusa.com/bloom/{link[3:]}'
        for link in links
    ]
    return [
        {"day": day, "text": text, "link": link}
        for day, text, link in zip(days, texts, links)
    ]


def main(notifyApiKey):
    old_titles = [n['text'] for n in getGochiusaNews()]
    cl = LineNotifyClient(notifyApiKey)
    print("PROJECT AUTO RABBIT initialized.")
    while True:
        print("Scraping page...")
        news = getGochiusaNews()
        for n in news:
            if n["text"] not in old_titles:
                print("Found new data.")
                cl.sendNotify(f"\n<{n['text']}>\n{n['link']}")
                sleep(3)
        old_titles = [n['text'] for n in news]
        sleep(randint(30, 60))


if __name__ == "__main__":
    conn = SQLHandler()
    main(notifyApiKey)
