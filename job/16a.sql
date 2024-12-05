SELECT MIN(aka_name.name) AS cool_actor_pseudonym,
       MIN(title.title) AS series_named_after_char
FROM aka_name,
     cast_info,
     company_name,
     keyword,
     movie_companies,
     movie_keyword,
     name,
     title
WHERE company_name.country_code ='[us]'
  AND keyword.keyword ='character-name-in-title'
  AND title.episode_nr >= 50
  AND title.episode_nr < 100
  AND aka_name.person_id = name.id
  AND name.id = cast_info.person_id
  AND cast_info.movie_id = title.id
  AND title.id = movie_keyword.movie_id
  AND movie_keyword.keyword_id = keyword.id
  AND title.id = movie_companies.movie_id
  AND movie_companies.company_id = company_name.id
  AND aka_name.person_id = cast_info.person_id
  AND cast_info.movie_id = movie_companies.movie_id
  AND cast_info.movie_id = movie_keyword.movie_id
  AND movie_companies.movie_id = movie_keyword.movie_id;

