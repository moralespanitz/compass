def remove_intermediate_rows(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            if 'Total Intermediate Rows:' not in line:
                outfile.write(line)

# Remove intermediate rows from compass-resultados.txt
remove_intermediate_rows('../data/compass-resultados.txt', '../data/compass-resultados_cleaned.txt')

# Remove intermediate rows from postgres-resultados.txt
remove_intermediate_rows('../data/postgres-resultados.txt', '../data/postgres-resultados_cleaned.txt')