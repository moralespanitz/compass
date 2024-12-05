SELECT MIN(link_type.link) AS link_type,
       MIN(title.title) AS first_movie,
       MIN(title.title) AS second_movie
FROM keyword,
     link_type,
     movie_keyword,
     movie_link,
     title,
     title
WHERE keyword.keyword ='10,000-mile-club'
  AND movie_keyword.keyword_id = keyword.id
  AND title.id = movie_keyword.movie_id
  AND movie_link.movie_id = title.id
  AND movie_link.linked_movie_id = title.id
  AND link_type.id = movie_link.link_type_id
  AND movie_keyword.movie_id = title.id;

