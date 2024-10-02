import psycopg2

class PostgresPipeline:
    def open_spider(self, spider):
        # Kết nối đến database
        self.connection = psycopg2.connect(
            host='171.254.95.242',
            port='5432',
            database='searchfilm',
            user='postgres',
            password='20112003'
        )
        self.cursor = self.connection.cursor()
        
        # Kiểm tra kết nối
        try:
            self.cursor.execute("SELECT 1")
            print("Kết nối thành công đến cơ sở dữ liệu!")
        except Exception as e:
            print(f"Không thể kết nối đến cơ sở dữ liệu: {e}")

    def close_spider(self, spider):
        # Đóng kết nối khi spider kết thúc
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        # Kiểm tra xem phim có tồn tại trong database không
        self.cursor.execute('SELECT movie_id FROM "Movie" WHERE slug = %s', (item['slug'],))
        result = self.cursor.fetchone()

        if result:
            # Nếu phim đã tồn tại, chỉ thêm episode mới
            movie_id = result[0]
            self.add_episode(item, movie_id)
        else:
            # Nếu phim chưa tồn tại, thêm phim mới và các mối quan hệ liên quan
            movie_id = self.add_movie(item)
            self.add_genres(item, movie_id)
            self.add_actors(item, movie_id)
            self.add_directors(item, movie_id)
            self.add_countries(item, movie_id)
            self.add_episode(item, movie_id)

        # Commit thay đổi vào database
        self.connection.commit()
        return item

    def add_movie(self, item):
        # Thêm phim mới vào bảng Movie
        self.cursor.execute("""
            INSERT INTO "Movie" (name, origin_name, content, type, status, thumb_url, trailer_url, 
                                 duration, quality, lang, slug, year, tmdb_vote_average, 
                                 tmdb_vote_count, poster_url, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING movie_id
        """, (
            item['name'], item.get('origin_name'), item.get('content'), item.get('type', 'single'),
            item.get('status'), item.get('thumb_url'), item.get('trailer_url'),
            item.get('duration'), item.get('quality'), item.get('lang'), item['slug'], 
            item.get('year'), item.get('tmdb_vote_average'), item.get('tmdb_vote_count'), 
            item.get('poster_url')
        ))
        movie_id = self.cursor.fetchone()[0]
        return movie_id

    def add_episode(self, item, movie_id):
        # Kiểm tra xem episode đã tồn tại chưa dựa trên movie_id và slug
        self.cursor.execute("""
            SELECT episode_id FROM "Episode" WHERE movie_id = %s AND slug = %s
        """, (movie_id, item['slug']))
        episode_result = self.cursor.fetchone()

        if not episode_result:
            # Nếu episode chưa tồn tại, thêm episode mới
            self.cursor.execute("""
                INSERT INTO "Episode" (movie_id, server_name, name, slug, link_film, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                movie_id, item.get('server_name'), item.get('name'), item['slug'], item.get('link_film')
            ))
        else:
            print(f"Episode '{item['slug']}' đã tồn tại, không thêm mới.")

    def add_genres(self, item, movie_id):
        # Kiểm tra và thêm thể loại
        for genre in item.get('movie_genres', []):
            self.cursor.execute('SELECT genre_id FROM "Genre" WHERE name = %s', (genre,))
            genre_result = self.cursor.fetchone()
            if not genre_result:
                # Nếu thể loại chưa tồn tại, thêm thể loại mới
                self.cursor.execute('INSERT INTO "Genre" (name, slug) VALUES (%s, %s) RETURNING genre_id', (genre, genre.lower().replace(' ', '-')))
                genre_id = self.cursor.fetchone()[0]
            else:
                genre_id = genre_result[0]
            # Liên kết thể loại với phim
            self.cursor.execute('INSERT INTO "MovieGenre" (movie_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING', (movie_id, genre_id))

    def add_actors(self, item, movie_id):
        # Kiểm tra và thêm diễn viên
        for actor in item.get('movie_actors', []):
            self.cursor.execute('SELECT actor_id FROM "Actor" WHERE name = %s', (actor,))
            actor_result = self.cursor.fetchone()
            if not actor_result:
                self.cursor.execute('INSERT INTO "Actor" (name) VALUES (%s) RETURNING actor_id', (actor,))
                actor_id = self.cursor.fetchone()[0]
            else:
                actor_id = actor_result[0]
            self.cursor.execute('INSERT INTO "MovieActor" (movie_id, actor_id) VALUES (%s, %s) ON CONFLICT DO NOTHING', (movie_id, actor_id))

    def add_directors(self, item, movie_id):
        # Kiểm tra và thêm đạo diễn
        for director in item.get('movie_directors', []):
            self.cursor.execute('SELECT director_id FROM "Director" WHERE name = %s', (director,))
            director_result = self.cursor.fetchone()
            if not director_result:
                self.cursor.execute('INSERT INTO "Director" (name) VALUES (%s) RETURNING director_id', (director,))
                director_id = self.cursor.fetchone()[0]
            else:
                director_id = director_result[0]
            self.cursor.execute('INSERT INTO "MovieDirector" (movie_id, director_id) VALUES (%s, %s) ON CONFLICT DO NOTHING', (movie_id, director_id))

    def add_countries(self, item, movie_id):
        # Kiểm tra và thêm quốc gia
        for country in item.get('movie_countries', []):
            self.cursor.execute('SELECT country_id FROM "Country" WHERE name = %s', (country,))
            country_result = self.cursor.fetchone()
            if not country_result:
                self.cursor.execute('INSERT INTO "Country" (name, slug) VALUES (%s, %s) RETURNING country_id', (country, country.lower().replace(' ', '-')))
                country_id = self.cursor.fetchone()[0]
            else:
                country_id = country_result[0]
            self.cursor.execute('INSERT INTO "MovieCountry" (movie_id, country_id) VALUES (%s, %s) ON CONFLICT DO NOTHING', (movie_id, country_id))
