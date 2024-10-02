import scrapy
from crawlfilm.items import CrawlfilmItem
from slugify import slugify  # Import slugify

class TvSeriesSpider(scrapy.Spider):
    name = "123_movies_tv_series"
    start_urls = ['https://ww4.123moviesfree.net/tv-series/']

    def parse(self, response):
        # Extract TV series URLs from the TV series list page and visit each series detail page
        series_urls = response.css('div.card.h-100 a::attr(href)').getall()
        for url in series_urls:
            yield response.follow(url, self.parse_series)

        # Xử lý trang tiếp theo
        next_page = response.css('a.page-link[aria-label="Next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_series(self, response):
        # Create an instance of CrawlfilmItem
        item = CrawlfilmItem()

        # Extract series link and slug
        # series_link = response.url
        # item['slug'] = series_link.split('/')[-2]  # Lấy slug từ URL
        
        # Extract series title
        item['name'] = response.css('h1.card-title::text').get()
        item['origin_name'] = response.css('h1.card-title::text').get()

        if item['name']:
            item['slug'] = slugify(item['name'])
        
        # Extract description
        item['content'] = response.css('div.fst-italic::text').get()
        
        # Extract genres
        item['movie_genres'] = response.css('p:contains("Genre") a::text').getall()
        
        # Extract actors
        item['movie_actors'] = response.css('p:contains("Actor") a::text').getall()
        
        # Extract directors
        directors = response.xpath('//p[strong[contains(text(), "Director")]]/text()').getall()
        item['movie_directors'] = [director.strip() for director in directors if director.strip()]
        
        # Extract countries
        item['movie_countries'] = response.xpath('//p[strong[contains(text(),"Country")]]/a/text()').getall()
        
        # Extract quality
        item['quality'] = 'HD'
        episode_current = response.css('p:contains("Episode") span::text').get()

        item['episode_total'] = episode_current
        item['episode_current'] = episode_current
        # Extract duration (might represent episode runtime in this case)
        item['duration'] = response.xpath('//p[strong[contains(text(),"Duration")]]/text()').get().strip()
        
        # Extract year (release year)
        year_text = response.css('p:contains("Release") a::text').get()
        if year_text and year_text.isdigit():
            item['year'] = int(year_text)
        else:
            item['year'] = None  # Nếu không có giá trị hợp lệ
        
        # Extract poster URL
        item['poster_url'] = response.css('picture img::attr(data-src)').get()
        
        # Other TV-specific fields
        item['lang'] = 'English'
        item['server_name'] = '123movies'
        item['link_film'] = response.url
        
        # Return the item
        yield item
