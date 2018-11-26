# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeatherForecastItem(scrapy.Item):
    city_code = scrapy.Field()
    date_created = scrapy.Field()
    day_forecast = scrapy.Field()
    night_forecast = scrapy.Field()
    day_temperature = scrapy.Field()
    night_temperature = scrapy.Field()
    day_realfeel = scrapy.Field()
    night_realfeel = scrapy.Field()
    day_wind = scrapy.Field()
    night_wind = scrapy.Field()
    day_gusts = scrapy.Field()
    night_gusts = scrapy.Field()
    sunrise = scrapy.Field()
    sunset = scrapy.Field()
    moonrise = scrapy.Field()
    moonset = scrapy.Field()
