import matplotlib.pyplot as plt
import numpy as np

# Read execution times from files
compass_times = []
postgres_times = []

with open('data/compass-resultados.txt', 'r') as file:
    for line in file:
        parts = line.strip().split(', ')
        if len(parts) == 3:
            query, _, time = parts
            compass_times.append(float(time))

with open('data/postgres-resultados.txt', 'r') as file:
    for line in file:
        parts = line.strip().split(', ')
        if len(parts) == 4:
            query, _, _, time = parts
            postgres_times.append(float(time.split()[0]))

# Define categories
categories = ['4-9', '10-19', '20-28']

# Group data into categories (this needs to be adapted based on actual data)
compass_grouped = [np.mean(compass_times[:3]), np.mean(compass_times[3:6]), np.mean(compass_times[6:])]
postgres_grouped = [np.mean(postgres_times[:3]), np.mean(postgres_times[3:6]), np.mean(postgres_times[6:])]

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(categories, compass_grouped, marker='o', color='blue', label='COMPASS')
plt.plot(categories, postgres_grouped, marker='s', color='red', label='PostgreSQL')

plt.xlabel('Categorías')
plt.ylabel('Tiempo de Ejecución (ms)')
plt.title('Comparación de Tiempos de Ejecución')
plt.legend()
plt.grid(True)
plt.show()