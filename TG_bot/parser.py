import requests
from lxml import html

page = requests.get('https://www.gismeteo.by/', headers={
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'})

tree = html.fromstring(page.content)
city = tree.xpath('//a[@class="city-link link"]//text()')[0]
time = tree.xpath('//div[@class="current-time"]//text()')[0]
descr = tree.xpath('//div[@class="weather-description"]//text()')[0]
degrees = ''.join(tree.xpath('//div[@class="temperature"]//text()')[:2])
print(page)