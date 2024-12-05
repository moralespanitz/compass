SELECT MIN(aka_name.name) AS actress_pseudonym,
       MIN(title.title) AS japanese_movie_dubbed
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
  AND name.name LIKE '%Yo%'
  AND name.name NOT LIKE '%Yu%'
  AND role_type.role ='actress'
  AND aka_name.person_id = name.id
  AND name.id = cast_info.person_id
  AND cast_info.movie_id = title.id
  AND title.id = movie_companies.movie_id
  AND movie_companies.company_id = company_name.id
  AND cast_info.role_id = role_type.id
  AND aka_name.person_id = cast_info.person_id
  AND cast_info.movie_id = movie_companies.movie_id;

