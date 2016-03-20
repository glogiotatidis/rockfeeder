#!/usr/bin/env python
import click
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from apscheduler.schedulers.blocking import BlockingScheduler


URL = 'http://www.rocking.gr/agenda/athens'


def fetch_events():
    events = {}
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'lxml')

    for datebox in soup.find_all('div', attrs={'class': 'date-box'}):
        date = datebox.find('h2').text

        for event_block in datebox.find_all(id='event-block'):
            groups = event_block.find('div', attrs={'class': 'groups'}).text
            city_venue = event_block.find('div', attrs={'class': 'city_venue'}).text
            price = event_block.find('small').text
            link = event_block.find('a').attrs['href']
            events[link] = {
                'price': price,
                'groups': groups,
                'city_venue': city_venue,
                'link': link,
                'date': date,
                }
    return events


def generate_feed(events):
    fg = FeedGenerator()
    fg.title('yo')
    fg.link( href='http://example.com', rel='alternate' )
    fg.description('f')
    for event in events.values():
        fe = fg.add_entry()
        fe.id(event['link'])
        fe.title(event['groups'])
        # fe.subtitle(u'{} / {}'.format(event['city_venue'], event['price']))
        # fe.link(href=event['link'])
    fg.rss_file('html/rss.xml')



def generate():
    print('Generating')
    events = fetch_events()
    generate_feed(events)


@click.command()
@click.option('--generate-once/--schedule', default=True)
@click.option('--minutes', default=60)
def main(generate_once, minutes):
    if generate_once:
        generate()
    else:
        print('Starting schedule, every {} minutes'.format(minutes))
        scheduler = BlockingScheduler()
        scheduler.add_job(generate, 'interval', minutes=1)
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

if __name__ == "__main__":
    main()
