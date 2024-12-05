SELECT MIN(name.name) AS member_in_charnamed_american_movie,
       MIN(name.name) AS a1
FROM cast_info,
     company_name,
     keyword,
     movie_companies,
     movie_keyword,
     name,
     title
WHERE company_name.country_code ='[us]'
  AND keyword.keyword ='character-name-in-title'
  AND name.name LIKE 'B%'
  AND name.id = cast_info.person_id
  AND cast_info.movie_id = title.id
  AND title.id = movie_keyword.movie_id
  AND movie_keyword.keyword_id = keyword.id
  AND title.id = movie_companies.movie_id
  AND movie_companies.company_id = company_name.id
  AND cast_info.movie_id = movie_companies.movie_id
  AND cast_info.movie_id = movie_keyword.movie_id
  AND movie_companies.movie_id = movie_keyword.movie_id;

