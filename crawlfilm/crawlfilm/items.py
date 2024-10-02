# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class CrawlfilmItem(scrapy.Item):
    movie_id = scrapy.Field()
    name = scrapy.Field()
    origin_name = scrapy.Field()
    content = scrapy.Field()
    type = scrapy.Field(default="single")
    status = scrapy.Field(default='completed')
    thumb_url = scrapy.Field()
    trailer_url = scrapy.Field()
    duration = scrapy.Field()
    episode_current = scrapy.Field(default="Full")
    episode_total = scrapy.Field(default="1")
    quality = scrapy.Field()
    lang = scrapy.Field()
    notify = scrapy.Field()
    showtimes = scrapy.Field()
    tmdb_vote_average = scrapy.Field(default=0)
    tmdb_vote_count = scrapy.Field(default=0)
    slug = scrapy.Field()
    year = scrapy.Field()
    view = scrapy.Field(default=0)
    is_copyright = scrapy.Field(default=False)
    chieurap = scrapy.Field(default=False)
    poster_url = scrapy.Field()
    sub_docquyen = scrapy.Field(default=False)
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    episodes = scrapy.Field()
    movie_genres = scrapy.Field()
    movie_countries = scrapy.Field()
    movie_actors = scrapy.Field()
    movie_directors = scrapy.Field()
    link_film = scrapy.Field()
    server_name = scrapy.Field()

