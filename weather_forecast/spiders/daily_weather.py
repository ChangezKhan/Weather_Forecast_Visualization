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
        'FEED_EXPORT_FIELDS': ["city_code", "date_created", "type_of", "forecast", "temperature", "realfeel", "wind", "gusts"]
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
            
        day_item = WeatherForecastItem()
        
        day_item['city_code'] = response.meta['city_code']
        day_item['date_created'] = datetime.datetime.today().strftime('%Y-%m-%d')
        day_item['type_of'] = "Day"

        temperature_list = response.xpath('//div[@id="detail-day-night"]//span/text()').extract()

        temp_day_temperature = temperature_list[0]
        temp_day_realfeel = temperature_list[2]

        forecast_list = response.xpath('//div[@id="detail-day-night"]//div[@class="cond"]/text()').extract()

        day_item['forecast'] = forecast_list[0].strip()

        day_item['temperature'] = int(re.search(r'\d+', temp_day_temperature).group())
        day_item['realfeel'] = int(re.search(r'\d+', temp_day_realfeel).group())

        wind_stats_list = response.xpath('//div[@id="detail-day-night"]//ul[@class="wind-stats"]//li/strong/text()').extract()

        day_item['wind'] = wind_stats_list[0]
        day_item['gusts'] = wind_stats_list[1]
            
        yield day_item
        
        night_item = WeatherForecastItem()
        
        night_item['city_code'] = response.meta['city_code']
        night_item['date_created'] = datetime.datetime.today().strftime('%Y-%m-%d')
        night_item['type_of'] = "Night"
        
        temp_night_temperature = temperature_list[4]
        temp_night_realfeel = temperature_list[6]
                
        night_item['forecast'] = forecast_list[1].strip()
        
        night_item['temperature'] = int(re.search(r'\d+', temp_night_temperature).group())
        night_item['realfeel'] = int(re.search(r'\d+', temp_night_realfeel).group())
                
        night_item['wind'] = wind_stats_list[2]
        night_item['gusts'] = wind_stats_list[3]
        
        yield night_item
