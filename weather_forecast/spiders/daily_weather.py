# -*- coding: utf-8 -*-
import scrapy
import re
import datetime

from weather_forecast.items import WeatherForecastItem

class DailyWeatherSpider(scrapy.Spider):
    name = 'daily_weather'
    allowed_domains = ['www.accuweather.com']
    start_urls = ['https://www.accuweather.com/en/world-weather']

    custom_settings = {
        # specifies exported fields and order
        'FEED_EXPORT_FIELDS': ["city_code", "date_created", "day_forecast", "night_forecast", "day_temperature", "night_temperature", "day_realfeel", "night_realfeel", "day_wind", "night_wind", "day_gusts", "night_gusts", "sunrise", "sunset", "moonrise", "moonset"]
      }

    def parse(self, response):
        url = response.xpath('(//div[@class="full-width-button"])[3]/a/@href').extract_first()
        yield scrapy.Request(url, callback=self.parse_regions)

    def parse_regions(self, response):
        region_url_list = response.xpath('//div[@class="info"]/h6/a/@href').extract()
        region_name_list = response.xpath('//div[@class="info"]/h6/a/em/text()').extract()

        for index in range(len(region_url_list)-1):
            region_url = region_url_list[index]
            if region_url == "https://www.accuweather.com/en/browse-locations/asi":
                request = scrapy.Request(region_url, callback = self.parse_countries)
                yield request

    def parse_countries(self, response):
        country_url_list = response.xpath('//div[@class="info"]/h6/a/@href').extract()
        country_name_list = response.xpath('//div[@class="info"]/h6/a/em/text()').extract()

        for index in range(len(country_url_list)-1):
            country_url = country_url_list[index]
            if country_url == "https://www.accuweather.com/en/browse-locations/asi/in":
                request = scrapy.Request(country_url, callback = self.parse_states)
                yield request

    def parse_states(self, response):
        state_url_list = response.xpath('//div[@class="info"]/h6/a/@href').extract()
        state_name_list = response.xpath('//div[@class="info"]/h6/a/em/text()').extract()

        for index in range(len(state_url_list)-1):
            state_url = state_url_list[index]
            #if state_url == "https://www.accuweather.com/en/browse-locations/asi/in/mh":
            request = scrapy.Request(state_url, callback = self.parse_cities)
            yield request

    def parse_cities(self, response):
        city_url_list = response.xpath('//div[@class="info"]/h6/a/@href').extract()

        for index in range(len(city_url_list)-1):
            city_url = city_url_list[index]
            #if city_url == "https://www.accuweather.com/en/in/andheri-west/3352413/weather-forecast/3352413":
            request = scrapy.Request(city_url, callback = self.parse_city_weather)
            request.meta['city_code'] = city_url.split("/")[-1]
            yield request

    def parse_city_weather(self, response):
        city_daily_weather_url = response.xpath('//div[@id="feed-tabs"]/a/@href').extract_first()
        request = scrapy.Request(city_daily_weather_url, callback = self.get_daily_weather)
        request.meta['city_code'] = response.meta['city_code']
        yield request

    def get_daily_weather(self, response):
            
        item = WeatherForecastItem()
        
        item['city_code'] = response.meta['city_code']
        item['date_created'] = datetime.datetime.today().strftime('%Y-%m-%d')

        temperature_list = response.xpath('//div[@id="detail-day-night"]//span/text()').extract()

        temp_day_temperature = temperature_list[0]
        temp_night_temperature = temperature_list[4]
        temp_day_realfeel = temperature_list[2]
        temp_night_realfeel = temperature_list[6]

        forecast_list = response.xpath('//div[@id="detail-day-night"]//div[@class="cond"]/text()').extract()

        item['day_forecast'] = forecast_list[0].strip()
        item['night_forecast'] = forecast_list[1].strip()

        item['day_temperature'] = int(re.search(r'\d+', temp_day_temperature).group())
        item['night_temperature'] = int(re.search(r'\d+', temp_night_temperature).group())
        item['day_realfeel'] = int(re.search(r'\d+', temp_day_realfeel).group())
        item['night_realfeel'] = int(re.search(r'\d+', temp_night_realfeel).group())

        wind_stats_list = response.xpath('//div[@id="detail-day-night"]//ul[@class="wind-stats"]//li/strong/text()').extract()

        item['day_wind'] = wind_stats_list[0]
        item['night_wind'] = wind_stats_list[2]
        item['day_gusts'] = wind_stats_list[1]
        item['night_gusts'] = wind_stats_list[3]

        sun_desc_list = response.xpath('//div[@id="feature-sun"]//span/text()').extract()

        item['sunrise'] = sun_desc_list[0]
        item['sunset'] = sun_desc_list[1]

        moon_desc_list = response.xpath('//div[@id="feature-moon"]//span/text()').extract()

        item['moonrise'] = moon_desc_list[0]
        item['moonset'] = moon_desc_list[1]

        yield item
