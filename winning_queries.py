import matplotlib.pyplot as plt
import numpy as np

# Example data for demonstration
compass_wins = 63
postgres_wins = 39

# Wins by category
compass_by_joins = [20, 30, 13]  # Example: [4-9 joins, 10-19 joins, 20-28 joins]
postgres_by_joins = [17, 22, 10]

# Plotting total wins
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
bars1 = plt.bar(['COMPASS', 'PostgreSQL'], [compass_wins, postgres_wins], color=['lightblue', 'lightcoral'])
plt.title('Total de Queries Ganadas')
plt.ylabel('Número de Queries')

# Adding text on top of bars
for bar, value in zip(bars1, [compass_wins, postgres_wins]):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 5, f'{value} ({value / (compass_wins + postgres_wins) * 100:.1f}%)', ha='center', va='bottom')

# Plotting wins by number of joins
plt.subplot(1, 2, 2)
bar_width = 0.35
index = np.arange(len(compass_by_joins))
bars2 = plt.bar(index, compass_by_joins, bar_width, label='COMPASS', color='lightblue')
bars3 = plt.bar(index + bar_width, postgres_by_joins, bar_width, label='PostgreSQL', color='lightcoral')

plt.xlabel('Número de Joins')
plt.ylabel('Número de Queries')
plt.title('Winning Queries por Número de Joins')
plt.xticks(index + bar_width / 2, ['4-9 Joins', '10-19 Joins', '20-28 Joins'])
plt.legend()

# Adding text on top of bars
for bars in [bars2, bars3]:
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 1, f'{int(bar.get_height())}', ha='center', va='bottom')

plt.tight_layout()
plt.show()