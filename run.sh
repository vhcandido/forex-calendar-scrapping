#!/bin/bash

rm fx_events.json
scrapy runspider forex_calendar.py -o fx_events.json
cat fx_events.json
