SELECT MIN(movie_info_idx.info) AS rating,
       MIN(title.title) AS movie_title
FROM info_type,
     keyword,
     movie_info_idx,
     movie_keyword,
     title
WHERE info_type.info ='rating'
  AND keyword.keyword LIKE '%sequel%'
  AND movie_info_idx.info > '9.0'
  AND title.production_year > 2010
  AND title.id = movie_info_idx.movie_id
  AND title.id = movie_keyword.movie_id
  AND movie_keyword.movie_id = movie_info_idx.movie_id
  AND keyword.id = movie_keyword.keyword_id
  AND info_type.id = movie_info_idx.info_type_id;

