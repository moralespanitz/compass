SELECT MIN(title.title) AS american_movie
FROM company_type,
     info_type,
     movie_companies,
     movie_info,
     title
WHERE company_type.kind = 'production companies'
  AND movie_companies.note NOT LIKE '%(TV)%'
  AND movie_companies.note LIKE '%(USA)%'
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
  AND title.production_year > 1990
  AND title.id = movie_info.movie_id
  AND title.id = movie_companies.movie_id
  AND movie_companies.movie_id = movie_info.movie_id
  AND company_type.id = movie_companies.company_type_id
  AND info_type.id = movie_info.info_type_id;

