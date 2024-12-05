SELECT MIN(movie_info_idx.info) AS rating,
       MIN(title.title) AS northern_dark_movie
FROM info_type,
     info_type,
     keyword,
     kind_type,
     movie_info,
     movie_info_idx,
     movie_keyword,
     title
WHERE info_type.info = 'countries'
  AND info_type.info = 'rating'
  AND keyword.keyword IN ('murder',
                    'murder-in-title',
                    'blood',
                    'violence')
  AND kind_type.kind = 'movie'
  AND movie_info.info IN ('Sweden',
                  'Norway',
                  'Germany',
                  'Denmark',
                  'Swedish',
                  'Denish',
                  'Norwegian',
                  'German',
                  'USA',
                  'American')
  AND movie_info_idx.info < '8.5'
  AND title.production_year > 2010
  AND kind_type.id = title.kind_id
  AND title.id = movie_info.movie_id
  AND title.id = movie_keyword.movie_id
  AND title.id = movie_info_idx.movie_id
  AND movie_keyword.movie_id = movie_info.movie_id
  AND movie_keyword.movie_id = movie_info_idx.movie_id
  AND movie_info.movie_id = movie_info_idx.movie_id
  AND keyword.id = movie_keyword.keyword_id
  AND info_type.id = movie_info.info_type_id
  AND info_type.id = movie_info_idx.info_type_id;
