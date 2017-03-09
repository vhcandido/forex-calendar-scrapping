import scrapy
import calendar

class FXCalendarSpider(scrapy.Spider):
    month_dict = {v.lower(): k for k,v in enumerate(calendar.month_abbr)}
    name = "events"
    allowed_domains = ['forexfactory.com']

    base_url = 'https://www.forexfactory.com/calendar.php?month=%s.%d'

    # Every month of the following years
    year_list = [ 2017 ]
    month_list = [ m.lower() for m in calendar.month_abbr ]
    start_urls = [ base_url % (month, year) for month in month_list for year in year_list ]


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url = url, callback = self.parse_first_call)


    def parse_first_call(self, response):
        date_dict = {}
        time = None

        # Filter table rows from the specified classes
        #XPath: response.xpath('//tr[contains(@class,"calendar_row")]')
        #CSS: response.css('tr.calendar_row')
        for event in response.xpath('//tr[not(contains(@class, "noevent"))]').css('tr.calendar_row'):
            # Some of these rows have more classes that refers to wheter it's a new day or different colors

            #CSS:: event.css('tr::attr(class)').extract_first():
            if 'newday' in event.xpath('@class').extract_first():
                # It's a tr.newday, so we can get the date and use it for others rows within this day
                date_dict['weekday'] = event.css('td span.date::text').extract_first()
                date_dict['month'], date_dict['day'] = event.css('td span.date span::text').extract_first().lower().split()

                # It's a tr.newday, so it must not get the time from the last row
                time = None

            #XPath: event.xpath('.//td[contains(@class,"time")]/text()').extract_first()
            if event.css('td.calendar__time.time::text'):
                # It's the first row at this time, so we can save it for other rows within this time
                time = event.css('td.calendar__time.time::text').extract_first()

            date_dict['year'] = response.url[-4:]

            # Create data entries
            yield {
                    'weekday': date_dict['weekday'],
                    'date': '%d-%02d-%02d' % (
                        int( date_dict.get('year') ),
                        self.month_dict[ date_dict.get('month') ],
                        int( date_dict.get('day') )
                        ),
                    'time': time,
                    'currency': event.css('td.currency::text').extract_first(),
                    'impact': event.css('td.impact div span').xpath('@class').extract_first(),
                    'event': event.css('td.event div span::text').extract_first(),
                    'previous': event.css('td.previous::text').extract_first(),
                    'actual': event.css('td.actual::text').extract_first(),
                    'forecast': event.css('td.forecast::text').extract_first(),
                    'eventid': event.xpath('@data-eventid').extract_first()
                    #'detail':,
                    #'graph':,
            }
