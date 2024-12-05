SELECT MIN(title.title) AS movie_title
FROM keyword,
     movie_info,
     movie_keyword,
     title
WHERE keyword.keyword LIKE '%sequel%'
  AND movie_info.info IN ('Sweden',
                  'Norway',
                  'Germany',
                  'Denmark',
                  'Swedish',
                  'Denish',
                  'Norwegian',
                  'German')
  AND title.production_year > 2005
  AND title.id = movie_info.movie_id
  AND title.id = movie_keyword.movie_id
  AND movie_keyword.movie_id = movie_info.movie_id
  AND keyword.id = movie_keyword.keyword_id;

