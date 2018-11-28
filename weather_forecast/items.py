# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeatherForecastItem(scrapy.Item):
    city_code = scrapy.Field()
    date_created = scrapy.Field()
    type_of = scrapy.Field()
    forecast = scrapy.Field()
    temperature = scrapy.Field()
    realfeel = scrapy.Field()
    wind = scrapy.Field()
    gusts = scrapy.Field()
