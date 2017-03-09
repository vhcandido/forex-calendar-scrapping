#!/bin/bash

rm fx_events.csv
scrapy runspider forex_calendar.py -o fx_events.csv
