import scrapy
from crawlfilm.items import CrawlfilmItem
from slugify import slugify  # Import slugify

class MovieSpider(scrapy.Spider):
    name = "123_movies"
    start_urls = ['https://ww4.123moviesfree.net/movies/']

    def parse(self, response):
        # Extract movie URLs from the movie list page and visit each movie detail page
        movie_urls = response.css('div.card.h-100 a::attr(href)').getall()
        for url in movie_urls:
            yield response.follow(url, self.parse_movie)
                # Xử lý trang tiếp theo
        # Xử lý trang tiếp theo
        # next_page = response.css('a.page-link[aria-label="Next"]::attr(href)').get()  # Tìm đường dẫn đến trang tiếp theo
        # if next_page:
        #     yield response.follow(next_page, self.parse)  # Tiếp tục crawl trang tiếp theo

    def parse_movie(self, response):
        # Create an instance of CrawlfilmItem
        item = CrawlfilmItem()
        
        # Extract movie link and slug
        # movie_link = response.url
        # item['slug'] = movie_link.split('/')[-2]  # Lấy slug từ URL
        # # Extract title
        item['name'] = response.css('h1.card-title::text').get()
                # Create a slug from the name
        if item['name']:
            item['slug'] = slugify(item['name'])

        item['origin_name'] = response.css('h1.card-title::text').get()
        # Extract description
        item['content'] = response.css('div.fst-italic::text').get()
        # Extract genres
        item['movie_genres'] = response.css('p:contains("Genre") a::text').getall()
        # Extract actors
        item['movie_actors'] = response.css('p:contains("Actor") a::text').getall()
        # Extract directors
        directors = response.xpath('//p[strong[contains(text(), "Director")]]/text()').getall()
        item['movie_directors'] = [director.strip() for director in directors if director.strip()]
        # Extract country
        item['movie_countries'] = response.xpath('//p[strong[contains(text(),"Country")]]/a/text()').getall()
        # Extract quality
        item['quality'] = response.css('p:contains("Quality") span::text').get()
        # Extract duration
        item['duration'] = response.xpath('//p[strong[contains(text(),"Duration")]]/text()').get().strip()
        year_text = response.css('p:contains("Release") a::text').get()
        if year_text and year_text.isdigit():
            item['year'] = int(year_text)
        else:
            item['year'] = None  # Hoặc giá trị mặc định nếu không có dữ liệu hợp lệ
        item['poster_url'] = response.css('picture img::attr(data-src)').get()
        item['lang'] = 'English'
        item['server_name'] = '123movies'
        item['link_film'] = response.url
        # Return the item
        yield item