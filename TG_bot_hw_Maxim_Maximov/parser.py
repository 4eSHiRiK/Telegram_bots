import requests
from lxml import html

page = requests.get('https://practicum.yandex.ru/blog/top-knig-po-python/', headers={
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'})

tree = html.fromstring(page.content)
first_book = tree.xpath('//*[@id="id1"]/div/div/div/div[2]/div/p/span/span//text()')[0]
second_book = tree.xpath('//*[@id="post-content-text"]/div/div/div/div/h6/p/span//text()')[0]
third_book = tree.xpath('//*[@id="post-content-text"]/div/div/div/div/h6/p/span/span//text()')[0]

print(page)