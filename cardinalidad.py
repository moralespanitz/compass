import matplotlib.pyplot as plt
import numpy as np

# Read data from files
compass_data = []
postgres_data = []

with open('data/compass-resultados.txt', 'r') as file:
    for line in file:
        parts = line.strip().split(', ')
        if len(parts) == 3:
            query, plan, cardinality = parts
            compass_data.append((query, plan, int(cardinality)))

with open('data/postgres-resultados.txt', 'r') as file:
    for line in file:
        parts = line.strip().split(', ')
        if len(parts) == 4:
            query, plan, cardinality, _ = parts
            postgres_data.append((query, plan, int(cardinality)))

# Write to a new text file
with open('data/cardinality_comparison.txt', 'w') as file:
    file.write('Cardinality Comparison between Compass and PostgreSQL\n')
    file.write('=' * 50 + '\n\n')
    for compass, postgres in zip(compass_data, postgres_data):
        file.write(f'SQL File: {compass[0]}\n')
        file.write('-' * 20 + '\n')
        file.write(f'Compass Plan: {compass[1]}\n')
        file.write(f'Postgres Plan: {postgres[1]}\n')
        file.write(f'Compass Cardinality: {compass[2]}\n')
        file.write(f'Postgres Cardinality: {postgres[2]}\n\n')

# Define categories
categories = ['4-9', '10-19', '20-28']

# Example: Group data into categories (this needs to be adapted based on actual data)
compass_grouped = [np.mean([x[2] for x in compass_data[:3]]), np.mean([x[2] for x in compass_data[3:6]]), np.mean([x[2] for x in compass_data[6:]])]
postgres_grouped = [np.mean([x[2] for x in postgres_data[:3]]), np.mean([x[2] for x in postgres_data[3:6]]), np.mean([x[2] for x in postgres_data[6:]])]

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(categories, compass_grouped, marker='o', color='blue', label='COMPASS')
plt.plot(categories, postgres_grouped, marker='s', color='red', label='PostgreSQL')

plt.yscale('log')
plt.xlabel('Tiempo de Ejecución (ms)')
plt.ylabel('Cardinalidad (log scale)')
plt.title('Comparación de Cardinalidad')
plt.legend()
plt.grid(True)
plt.show()