import matplotlib.pyplot as plt
import numpy as np
import re
from collections import defaultdict
from .config import (
    L1_DISTANCE_RESULTS as l1_distance_filepath,
    PLOTS_DIR
)
import os

def extract_query_info(file_path):
    """Extract query information from the text file."""
    query_info = []
    current_query = None
    tables = None
    
    with open(file_path, 'r') as f:
        text = f.read()
        
    for line in text.split('\n'):
        query_match = re.match(r'SQL File: (.+?)\.sql', line)
        tables_match = re.match(r'Tables \((\d+)\):', line)
        distance_match = re.match(r'.*L1 Distance:\s+(\d+\.\d+)', line)
        
        if query_match:
            current_query = query_match.group(1)
        elif tables_match and current_query:
            tables = int(tables_match.group(1))
        elif distance_match and current_query and tables:
            distance = float(distance_match.group(1))
            query_info.append({
                'query': current_query,
                'numTables': tables,
                'distance': distance,
                'queryFamily': re.sub(r'[a-z]', '', current_query)
            })
    
    return query_info

def calculate_family_stats(query_info):
    """Calculate statistics for each query family."""
    families = defaultdict(list)
    for query in query_info:
        families[query['queryFamily']].append(query)
    
    family_stats = []
    for family, queries in families.items():
        avg_distance = np.mean([q['distance'] for q in queries])
        num_tables = queries[0]['numTables']  # All queries in family have same number of tables
        family_stats.append({
            'queryFamily': int(family),
            'avgDistance': avg_distance,
            'numTables': num_tables,
            'numQueries': len(queries)
        })
    
    return sorted(family_stats, key=lambda x: x['queryFamily'])

def plot_analysis(query_info, family_stats):
    """Create the visualization plots."""
    plt.style.use('default')
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16))
    
    # Plot 1: L1 Distance vs Number of Tables (Scatter plot)
    num_tables = [q['numTables'] for q in query_info]
    distances = [q['distance'] for q in query_info]
    
    ax1.scatter(num_tables, distances, alpha=0.6)
    ax1.set_xlabel('Number of Tables')
    ax1.set_ylabel('L1 Distance')
    ax1.set_title('L1 Distance vs Number of Tables')
    
    # Calculate and add correlation coefficient
    correlation = np.corrcoef(num_tables, distances)[0, 1]
    ax1.text(0.02, 0.98, f'Correlation: {correlation:.2f}', 
             transform=ax1.transAxes, fontsize=10,
             verticalalignment='top')
    
    # Add grid
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Plot 2: Average L1 Distance by Query Family (Line plot)
    family_nums = [f['queryFamily'] for f in family_stats]
    avg_distances = [f['avgDistance'] for f in family_stats]
    
    ax2.plot(family_nums, avg_distances, marker='o', linewidth=2, markersize=8)
    ax2.set_xlabel('Query Family')
    ax2.set_ylabel('Average L1 Distance')
    ax2.set_title('Average L1 Distance by Query Family')
    
    # Add grid
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # Add size indicators for number of queries in family
    sizes = [f['numQueries'] * 50 for f in family_stats]  # Scale the sizes
    ax2.scatter(family_nums, avg_distances, s=sizes, alpha=0.3, 
                label='Size indicates number of queries in family')
    
    # Add legend
    ax2.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Save plot
    plot_path = os.path.join(PLOTS_DIR, 'l1_distance_analysis.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {plot_path}")
    
    # Calculate and print some statistics
    print("\nAnalysis Statistics:")
    print(f"Total number of queries: {len(query_info)}")
    print(f"Average L1 distance: {np.mean(distances):.2f}")
    print(f"Maximum L1 distance: {max(distances):.2f}")
    print(f"Minimum L1 distance: {min(distances):.2f}")
    print(f"Number of query families: {len(family_stats)}")
    print(f"\nCorrelation between number of tables and L1 distance: {correlation:.2f}")

def main():
    # Read and process data
    query_info = extract_query_info(l1_distance_filepath)
    family_stats = calculate_family_stats(query_info)
    
    # Create visualization
    plot_analysis(query_info, family_stats)

if __name__ == "__main__":
    main()