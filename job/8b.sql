SELECT MIN(aka_name.name) AS acress_pseudonym,
       MIN(title.title) AS japanese_anime_movie
FROM aka_name,
     cast_info,
     company_name,
     movie_companies,
     name,
     role_type,
     title
WHERE cast_info.note ='(voice: English version)'
  AND company_name.country_code ='[jp]'
  AND movie_companies.note LIKE '%(Japan)%'
  AND movie_companies.note NOT LIKE '%(USA)%'
  AND (movie_companies.note LIKE '%(2006)%'
       OR movie_companies.note LIKE '%(2007)%')
  AND name.name LIKE '%Yo%'
  AND name.name NOT LIKE '%Yu%'
  AND role_type.role ='actress'
  AND title.production_year BETWEEN 2006 AND 2007
  AND (title.title LIKE 'One Piece%'
       OR title.title LIKE 'Dragon Ball Z%')
  AND aka_name.person_id = name.id
  AND name.id = cast_info.person_id
  AND cast_info.movie_id = title.id
  AND title.id = movie_companies.movie_id
  AND movie_companies.company_id = company_name.id
  AND cast_info.role_id = role_type.id
  AND aka_name.person_id = cast_info.person_id
  AND cast_info.movie_id = movie_companies.movie_id;

