import scrapy


class FXCalendarSpider(scrapy.Spider):
    name = "events"
    start_urls = [
            'http://www.forexfactory.com/calendar.php',
    ]

    def parse(self, response):
        css_str = 'tr.calendar__row.calendar_row.calendar__row--grey.calendar__row--new-day.newday'
        css_str = 'tr.calendar__row.calendar_row'

        date = None
        time = None
        for event in response.css(css_str):

            if not event.css('td span.date::text').extract_first() is None:
                time = None # It's a tr.newday, so it must not get the time from the last row
                date = event.css('td span.date::text').extract_first() + ' ' + \
                event.css('td span.date span::text').extract_first()

            if not event.css('td.calendar__cell.calendar__time.time::text').extract_first() is None:
                time = event.css('td.calendar__cell.calendar__time.time::text').extract_first()

            yield {
                    'date': date,
                    'time': time,
                    'currency': event.css('td.calendar__cell.calendar__currency.currency::text').extract_first(),
                    #'calendar_impact':,
                    #'event':,
                    #'detail':,
                    #'actual':,
                    #'forecast':,
                    #'previous':,
                    #'graph':,
                    #'': quote.css('span.text::text').extract_first(),
                    #'author': quote.xpath('span/small/text()').extract_first(),
            }

        #next_page = response.css('li.next a::attr("href")').extract_first()
        #if next_page is not None:
        #    next_page = response.urljoin(next_page)
        #    yield scrapy.Request(next_page, callback=self.parse)
