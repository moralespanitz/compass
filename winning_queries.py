#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def read_results(filename):
    results = {}
    current_query = None
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            if "Total Intermediate Rows:" in line:
                query = line.split(',')[0].strip()
                rows = int(line.split(':')[1].strip())
                results[query] = rows
    
    return results

def get_join_count(query, results_file):
    with open(results_file, 'r') as f:
        for line in f:
            if query in line and '⨝' in line:
                return line.count('⨝')
    return 0

def categorize_by_joins(results, results_file):
    categories = {
        '4-9 joins': 0,
        '10-19 joins': 0,
        '20-28 joins': 0
    }
    
    for query in results:
        joins = get_join_count(query, results_file)
        if 4 <= joins <= 9:
            categories['4-9 joins'] += 1
        elif 10 <= joins <= 19:
            categories['10-19 joins'] += 1
        elif 20 <= joins <= 28:
            categories['20-28 joins'] += 1
    
    return list(categories.values())

def analyze_winners(compass_results, postgres_results):
    compass_wins = 0
    postgres_wins = 0
    ties = 0
    winning_queries = {'compass': [], 'postgres': []}
    
    # Get all unique queries
    all_queries = set(compass_results.keys()) | set(postgres_results.keys())
    
    for query in all_queries:
        compass_rows = compass_results.get(query, float('inf'))
        postgres_rows = postgres_results.get(query, float('inf'))
        
        # Debugging: Print information for 20-28 join queries
        joins = get_join_count(query, 'compass-resultados.txt')
        if 20 <= joins <= 28:
            print(f"Debug: {query} - Joins: {joins}, Compass Rows: {compass_rows}, PostgreSQL Rows: {postgres_rows}")
        
        if compass_rows < postgres_rows:
            compass_wins += 1
            winning_queries['compass'].append(query)
        elif postgres_rows < compass_rows:
            postgres_wins += 1
            winning_queries['postgres'].append(query)
        else:
            ties += 1
    
    return compass_wins, postgres_wins, ties, winning_queries

def plot_individual_queries(compass_results, postgres_results):
    queries = sorted(set(compass_results.keys()) | set(postgres_results.keys()))
    compass_values = [compass_results.get(q, float('inf')) for q in queries]
    postgres_values = [postgres_results.get(q, float('inf')) for q in queries]
    
    plt.figure(figsize=(16, 8))
    x = np.arange(len(queries))
    
    plt.plot(x, compass_values, 'o-', label='COMPASS', color='blue', alpha=0.8, linewidth=1.5, markersize=4)
    plt.plot(x, postgres_values, 's-', label='PostgreSQL', color='red', alpha=0.8, linewidth=1.5, markersize=4)
    
    plt.xlabel('Query Index')
    plt.ylabel('Intermediate Rows')
    plt.title('Intermediate Rows for Each Query')
    plt.xticks(x, queries, rotation=90)
    plt.yscale('log')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('individual_queries_analysis.png', dpi=150, bbox_inches='tight')
    print("Plot saved as individual_queries_analysis.png")

def main():
    # Read results
    compass_results = read_results('compass-resultados.txt')
    postgres_results = read_results('postgres-resultados.txt')
    
    # Analyze winners
    compass_wins, postgres_wins, ties, winning_queries = analyze_winners(compass_results, postgres_results)
    
    # Debug information
    print("\nDebug Information:")
    print(f"Total queries in compass results: {len(compass_results)}")
    print(f"Total queries in postgres results: {len(postgres_results)}")
    print(f"Total unique queries: {len(set(compass_results.keys()) | set(postgres_results.keys()))}")
    print(f"Queries in both systems: {len(set(compass_results.keys()) & set(postgres_results.keys()))}")
    print(f"Ties: {ties}")
    
    # Plot individual queries
    plot_individual_queries(compass_results, postgres_results)
    
    # Get wins by join category
    compass_by_joins = categorize_by_joins(
        {q: compass_results[q] for q in winning_queries['compass']},
        'compass-resultados.txt'
    )
    
    postgres_by_joins = categorize_by_joins(
        {q: postgres_results[q] for q in winning_queries['postgres']},
        'postgres-resultados.txt'  # Fixed: now using postgres file for postgres queries
    )
    
    # Print summary
    print("\nSummary of Results:")
    print(f"Total COMPASS wins: {compass_wins} ({compass_wins/(compass_wins + postgres_wins + ties)*100:.1f}%)")
    print(f"Total PostgreSQL wins: {postgres_wins} ({postgres_wins/(compass_wins + postgres_wins + ties)*100:.1f}%)")
    print(f"Total ties: {ties} ({ties/(compass_wins + postgres_wins + ties)*100:.1f}%)")
    print("\nWins by Join Count:")
    print("Join Count  |  COMPASS  |  PostgreSQL")
    print("-" * 40)
    for i, (c, p) in enumerate(zip(compass_by_joins, postgres_by_joins)):
        join_range = ['4-9', '10-19', '20-28'][i]
        print(f"{join_range:10} |  {c:8d} |  {p:10d}")
    
    # Print winning queries
    print("\nWinning Queries by System:")
    print("\nCOMPASS wins:")
    for query in sorted(winning_queries['compass']):
        joins = get_join_count(query, 'compass-resultados.txt')
        print(f"{query}: {joins} joins")
    
    print("\nPostgreSQL wins:")
    for query in sorted(winning_queries['postgres']):
        joins = get_join_count(query, 'postgres-resultados.txt')
        print(f"{query}: {joins} joins")

    # Plotting total wins
    plt.figure(figsize=(15, 6))
    plt.subplot(1, 2, 1)
    bars1 = plt.bar(['COMPASS', 'PostgreSQL'], [compass_wins, postgres_wins], 
                   color=['lightblue', 'lightcoral'])
    plt.title('Total Winning Queries')
    plt.ylabel('Number of Queries')
    
    # Adding text on top of bars
    total_comparisons = compass_wins + postgres_wins + ties
    for bar, value in zip(bars1, [compass_wins, postgres_wins]):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), 
                f'{value}\n({value/total_comparisons*100:.1f}%)', 
                ha='center', va='bottom')
    
    # Plotting wins by number of joins
    plt.subplot(1, 2, 2)
    bar_width = 0.35
    index = np.arange(3)
    
    bars2 = plt.bar(index, compass_by_joins, bar_width, 
                   label='COMPASS', color='lightblue')
    bars3 = plt.bar(index + bar_width, postgres_by_joins, bar_width,
                   label='PostgreSQL', color='lightcoral')
    
    plt.xlabel('Number of Joins')
    plt.ylabel('Number of Queries')
    plt.title('Winning Queries by Join Count')
    plt.xticks(index + bar_width/2, ['4-9', '10-19', '20-28'])
    plt.legend()
    
    # Add value labels on bars
    for bars in [bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height,
                    f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('winning_queries_analysis.png', dpi=300, bbox_inches='tight')
    print("\nAnalysis plot saved as winning_queries_analysis.png")

if __name__ == "__main__":
    main()