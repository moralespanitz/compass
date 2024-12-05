SELECT MIN(name.name) AS of_person,
       MIN(title.title) AS biography_movie
FROM aka_name,
     cast_info,
     info_type,
     link_type,
     movie_link,
     name,
     person_info,
     title
WHERE aka_name.name LIKE '%a%'
  AND info_type.info ='mini biography'
  AND link_type.link ='features'
  AND name.name_pcode_cf BETWEEN 'A' AND 'F'
  AND (name.gender='m'
       OR (name.gender = 'f'
           AND name.name LIKE 'B%'))
  AND person_info.note ='Volker Boehm'
  AND title.production_year BETWEEN 1980 AND 1995
  AND name.id = aka_name.person_id
  AND name.id = person_info.person_id
  AND cast_info.person_id = name.id
  AND title.id = cast_info.movie_id
  AND movie_link.linked_movie_id = title.id
  AND link_type.id = movie_link.link_type_id
  AND info_type.id = person_info.info_type_id
  AND person_info.person_id = aka_name.person_id
  AND person_info.person_id = cast_info.person_id
  AND aka_name.person_id = cast_info.person_id
  AND cast_info.movie_id = movie_link.linked_movie_id;

