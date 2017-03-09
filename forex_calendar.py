import scrapy
import calendar
from scrapy.selector import Selector

class FXCalendarSpider(scrapy.Spider):
    month_dict = {v.lower(): k for k,v in enumerate(calendar.month_abbr)}
    name = "events"
    custom_settings = {
            'LOG_FILE': 'scrapy.log',
    }
    allowed_domains = ['forexfactory.com']

    base_url = 'https://www.forexfactory.com/calendar.php?month=%s.%d'

    # Every month of the following years
    year_list = [ 2017 ]
    month_list = [ m.lower() for m in calendar.month_abbr ]
    start_urls = [ base_url % (month, year) for month in month_list for year in year_list ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                    url = url,
                    meta = {
                        'dont_redirect': True,
                    },
                    callback = self.parse_page1
                )

    def parse_page1(self, response):
        date_dict = {}
        time = None

        date_dict['year'] = response.url[-4:]

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

            # Create data entries
            item = {
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
            }

            request = scrapy.Request(
                    url = 'https://www.forexfactory.com/flex.php?do=ajax&contentType=Content&flex=calendar_mainCal&details=%d' % int(item['eventid']),
                    meta = {
                        'dont_redirect': True,
                    },
                    callback = self.parse_page2)
            request.meta['item'] = item

            yield request

    def parse_page2(self, response):
        item = response.meta['item']

        body_text = response.xpath('//flex/text()').extract_first()
        event = Selector(text = body_text)

        cal_specs = event.xpath('.//table[./tr and contains(@class,"calendarspecs")]')
        # or csl_specs = event.xpath('.//table[./tr]').css('table.calendarspecs')

        # All specs, except Source and Next Release, are text descriptions
        # Source and Next Release are links to somewhere else
        tr_xpath = './tr[./td[contains(text(), "%s")]]'
        td_xpath = '/td[contains(@class,"calendarspecs__specdescription")]/text()'

        item['measures'] = cal_specs.xpath(tr_xpath % 'Measures' + td_xpath).extract_first()
        item['usual_effect'] = cal_specs.xpath(tr_xpath % 'Usual Effect' + td_xpath).extract_first()
        item['frequency'] = cal_specs.xpath(tr_xpath % 'Frequency' + td_xpath).extract_first()
        item['why_care'] = cal_specs.xpath(tr_xpath % 'Why Traders' + td_xpath).extract_first()
        item['also_called'] = cal_specs.xpath(tr_xpath % 'Also Called' + td_xpath).extract_first()

        item['source_name'] = cal_specs.xpath(tr_xpath % 'Source' + '/td/a/text()').extract_first()
        item['source_latest_url'] = cal_specs.xpath(tr_xpath % 'Source' + '/td/span/a/@href').extract_first()

        a = cal_specs.xpath(tr_xpath % 'Next Release' + '/td/a[contains(@class, "calendarspecs__nextdetails")]')
        item['next_release_date'] = a.xpath('text()').extract_first()
        item['next_release_url'] = a.xpath('@href').extract_first()
        item['next_release_eventid'] = item['next_release_url'].split('=')[-1] if item['next_release_url'] else None

        yield item
