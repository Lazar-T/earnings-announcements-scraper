import csv
import requests
from lxml import html

writer = csv.writer(open('output.csv', 'wb'))
writer.writerow(['Company', 'Symbol', 'Time', 'Date'])

visited_urls = []


def scrape_page(url):
    visited_urls.append(url)

    page = requests.get(url)
    tree = html.fromstring(page.content)

    non_working_days = tree.xpath('//*[@color="gray"]/text()')

    if non_working_days and non_working_days not in visited_urls:
        for non_working_day in non_working_days:
            visited_urls.insert(0, non_working_day)
            print '%s is non working day.' % non_working_day

    if 'Conference' in tree.xpath('//b/text()'):
        for tr in tree.xpath('//tr[position() > 2 and count(td) = 6]'):

            date = tree.xpath('//center/b/text()')[0]
            company, symbol, eps, time, add, conf_call = [td.text_content() for td in tr.xpath('.//td')]
            print company + '  |  ' + symbol + '  |  ' + time + '  |  ' + date

            writer.writerow([company, symbol, time, date])

    for tr in tree.xpath('//tr[position() > 2 and count(td) = 5]'):

        date = tree.xpath('//center/b/text()')[0]
        company, symbol, eps, time, add = [td.text_content() for td in tr.xpath('.//td')]
        print company + '  |  ' + symbol + '  |  ' + time + '  |  ' + date

        writer.writerow([company, symbol, time, date])

    next_day_urls = tree.xpath('//center/b/following-sibling::a/@href')[0:-1]

    for next_day_url in next_day_urls:
        if len(visited_urls) == 5:
            break

        absolute_url = 'http://biz.yahoo.com' + next_day_url
        if absolute_url not in visited_urls:
            scrape_page(absolute_url)

scrape_page('http://biz.yahoo.com/research/earncal/today.html')

if len(visited_urls) < 5:
    page = requests.get(visited_urls[-1])
    tree = html.fromstring(page.content)

    next_week_url = tree.xpath('//center/b/following-sibling::a/@href')[-1]
    absolute_next_week_url = 'http://biz.yahoo.com' + next_week_url
    scrape_page(absolute_next_week_url)
