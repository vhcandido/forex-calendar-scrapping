import scrapy

class FXCalendarSpider(scrapy.Spider):
    name = "events"
    # URLs to get the current and next month data
    base_url = 'http://www.forexfactory.com/calendar.php?month=%s'
    start_urls = [
            base_url % 'this',
            base_url % 'next',
    ]

    def parse(self, response):
        date = None
        time = None

        # Filter table rows from the specified classes
        css_str = 'tr.calendar__row.calendar_row'
        for event in response.css(css_str):
            # Some of these rows have more classes that refers to wheter it's a new day or different colors
            # (see page code for more information)

            if not event.css('td span.date::text').extract_first() is None:
                # It's a tr.newday, so we can get the date and use it for others rows within this day
                date = event.css('td span.date::text').extract_first() + ' ' + \
                    event.css('td span.date span::text').extract_first()

                # It's a tr.newday, so it must not get the time from the last row
                time = None

            if not event.css('td.calendar__cell.calendar__time.time::text').extract_first() is None:
                # It's the first row in this time, so we can save it for others rows within this time
                time = event.css('td.calendar__cell.calendar__time.time::text').extract_first()

            # Create data entries
            # (see page code for more information)
            yield {
                    'date': date,
                    'time': time,
                    'currency': event.css('td.calendar__cell.calendar__currency.currency::text').extract_first(),
                    'impact': event.css('td.calendar__cell.calendar__impact.impact' + \
                        ' div.calendar__impact-icon' + \
                        ' span::attr("class")').extract_first(),
                    'event': event.css('td.calendar__cell.calendar__event.event' + \
                            ' div span.calendar__event-title::text').extract_first(),

                    #'detail':,
                    #'actual':,
                    #'forecast':,
                    #'previous':,
                    #'graph':,
            }
