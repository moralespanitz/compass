#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def read_intermediate_rows(filename):
    results = {}
    with open(filename, 'r') as f:
        current_query = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Split by comma and get the first part (query name)
            parts = line.split(',', 1)
            if len(parts) < 2:
                continue
                
            query_name = parts[0].strip()
            content = parts[1].strip()
            
            # Check if this is an intermediate rows line
            if "Total Intermediate Rows:" in content:
                rows = int(content.split(":")[1].strip())
                results[query_name] = rows
    
    return results

def get_join_count(query_name):
    # Extract join count from query results
    with open('postgres-resultados.txt', 'r') as f:
        for line in f:
            if query_name in line and not "Total Intermediate Rows" in line:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    try:
                        return int(parts[2].strip())
                    except ValueError:
                        continue
    return 0

def group_by_joins(rows_dict):
    # Create groups: 4-9 joins, 10-19 joins, 20-28 joins
    groups = {
        "4-9 joins": defaultdict(list),
        "10-19 joins": defaultdict(list),
        "20-28 joins": defaultdict(list)
    }
    
    for query, rows in rows_dict.items():
        join_count = get_join_count(query)
        
        if 4 <= join_count <= 9:
            groups["4-9 joins"]["rows"].append(rows)
            groups["4-9 joins"]["count"] += 1
        elif 10 <= join_count <= 19:
            groups["10-19 joins"]["rows"].append(rows)
            groups["10-19 joins"]["count"] += 1
        elif 20 <= join_count <= 28:
            groups["20-28 joins"]["rows"].append(rows)
            groups["20-28 joins"]["count"] += 1
    
    # Calculate averages
    averages = {}
    for group_name, group_data in groups.items():
        if group_data["rows"]:
            averages[group_name] = {
                "avg": sum(group_data["rows"]) / len(group_data["rows"]),
                "count": group_data["count"]
            }
        else:
            averages[group_name] = {"avg": 0, "count": 0}
    
    return averages

def plot_join_groups(compass_rows, postgres_rows):
    compass_groups = group_by_joins(compass_rows)
    postgres_groups = group_by_joins(postgres_rows)
    
    # Prepare data for plotting
    groups = list(compass_groups.keys())
    x = np.arange(len(groups))
    compass_avgs = [compass_groups[g]["avg"] for g in groups]
    postgres_avgs = [postgres_groups[g]["avg"] for g in groups]
    
    # Create plot
    plt.figure(figsize=(12, 6))
    width = 0.35
    
    # Create bars
    plt.bar(x - width/2, compass_avgs, width, label='COMPASS', color='lightblue', alpha=0.8)
    plt.bar(x + width/2, postgres_avgs, width, label='PostgreSQL', color='lightcoral', alpha=0.8)
    
    # Add counts on top of bars
    for i, v in enumerate(compass_avgs):
        plt.text(i - width/2, v, f'Total: {compass_groups[groups[i]]["count"]}', 
                ha='center', va='bottom')
    for i, v in enumerate(postgres_avgs):
        plt.text(i + width/2, v, f'Total: {postgres_groups[groups[i]]["count"]}', 
                ha='center', va='bottom')
    
    # Customize plot
    plt.xlabel('Number of Joins')
    plt.ylabel('Average Intermediate Rows')
    plt.title('Average Intermediate Rows by Join Groups')
    plt.xticks(x, groups)
    plt.yscale('log')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save plot
    plt.savefig('join_groups_comparison.png')
    print("Join groups comparison plot saved as join_groups_comparison.png")
    
    # Print averages
    print("\nAverage Intermediate Rows by Join Groups:")
    print("Group".ljust(15) + "Compass Avg".rjust(15) + "Postgres Avg".rjust(15) + 
          "Compass Count".rjust(15) + "Postgres Count".rjust(15))
    print("-" * 75)
    
    for group in groups:
        compass_avg = compass_groups[group]["avg"]
        postgres_avg = postgres_groups[group]["avg"]
        compass_count = compass_groups[group]["count"]
        postgres_count = postgres_groups[group]["count"]
        print(f"{group.ljust(15)}{int(compass_avg):>15}{int(postgres_avg):>15}"
              f"{compass_count:>15}{postgres_count:>15}")

def plot_comparison(compass_rows, postgres_rows, output_file='cardinality_comparison.png'):
    # Get all unique query names and sort them
    all_queries = sorted(set(compass_rows.keys()) | set(postgres_rows.keys()))
    
    # Prepare data for plotting
    x = np.arange(len(all_queries))
    compass_values = [compass_rows.get(q, 0) for q in all_queries]
    postgres_values = [postgres_rows.get(q, 0) for q in all_queries]
    
    # Create figure and axis with larger size
    plt.figure(figsize=(15, 10))
    
    # Plot bars
    width = 0.35
    plt.bar(x - width/2, compass_values, width, label='Compass', alpha=0.8)
    plt.bar(x + width/2, postgres_values, width, label='PostgreSQL', alpha=0.8)
    
    # Customize the plot
    plt.xlabel('Queries')
    plt.ylabel('Intermediate Rows (log scale)')
    plt.title('Comparison of Intermediate Rows: Compass vs PostgreSQL')
    plt.xticks(x, all_queries, rotation=45, ha='right')
    plt.yscale('log')  # Use log scale for better visualization
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save plot
    plt.savefig(output_file)
    print(f"Plot saved as {output_file}")
    
    # Create ratio plot
    plt.figure(figsize=(15, 10))
    ratios = [p/c if c != 0 else float('inf') for p, c in zip(postgres_values, compass_values)]
    plt.bar(x, ratios, alpha=0.8, color='green')
    
    plt.xlabel('Queries')
    plt.ylabel('Ratio (PostgreSQL/Compass)')
    plt.title('Ratio of PostgreSQL to Compass Intermediate Rows')
    plt.xticks(x, all_queries, rotation=45, ha='right')
    plt.yscale('log')  # Use log scale for better visualization
    plt.grid(True, alpha=0.3)
    
    # Add horizontal line at ratio = 1
    plt.axhline(y=1, color='r', linestyle='--', alpha=0.5)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save ratio plot
    plt.savefig('cardinality_ratio.png')
    print("Ratio plot saved as cardinality_ratio.png")

def main():
    compass_rows = read_intermediate_rows('compass-resultados.txt')
    postgres_rows = read_intermediate_rows('postgres-resultados.txt')
    
    print("Comparison of Intermediate Rows:")
    print("Query".ljust(15) + "Compass".rjust(15) + "Postgres".rjust(15) + "Difference".rjust(15) + "Ratio".rjust(10))
    print("-" * 70)
    
    # Get all unique query names
    all_queries = sorted(set(compass_rows.keys()) | set(postgres_rows.keys()))
    
    for query in all_queries:
        compass_count = compass_rows.get(query, 0)
        postgres_count = postgres_rows.get(query, 0)
        difference = abs(compass_count - postgres_count)
        ratio = postgres_count / compass_count if compass_count != 0 else float('inf')
        
        print(f"{query.ljust(15)}{str(compass_count).rjust(15)}{str(postgres_count).rjust(15)}"
              f"{str(difference).rjust(15)}{ratio:>10.2f}")
    
    # Generate plots
    plot_comparison(compass_rows, postgres_rows)
    plot_join_groups(compass_rows, postgres_rows)

if __name__ == "__main__":
    main()
