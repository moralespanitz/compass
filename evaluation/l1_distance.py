import numpy as np
from .config import (
    COMPASS_RESULTS as compass_file,
    POSTGRES_RESULTS as postgres_file,
    L1_DISTANCE_RESULTS as output_file
)

def extract_tables(join_order):
    """
    Extract table names from a join order string in order of appearance.
    
    Args:
        join_order (str): String representing the join order with ⨝ operator
        
    Returns:
        list: List of table names in order of appearance
    """
    tables = []
    seen = set()
    current = ""
    
    for c in join_order:
        if c.isspace() or c in '()⨝':
            if current and current not in seen:
                tables.append(current)
                seen.add(current)
            current = ""
        else:
            current += c
            
    # Add the last table if it exists
    if current and current not in seen:
        tables.append(current)
        
    return tables

def l1_distance(join_order_c, join_order_s):
    """
    Calculate normalized L1 distance between two query plans based on table positions.
    
    Args:
        join_order_c (str): First join order string
        join_order_s (str): Second join order string
        
    Returns:
        float: Normalized L1 distance between the two plans
    """
    # Extract tables from both join orders
    C = extract_tables(join_order_c)
    S = extract_tables(join_order_s)
    
    # Verify both lists have the same tables
    if len(C) != len(S):
        raise ValueError("The two sub-plan lists have different sizes")
        
    # Create position map for C (1-based indexing)
    pos_c = {table: i+1 for i, table in enumerate(C)}
    
    # Calculate L1 distance
    sum_dist = 0
    for i, table in enumerate(S):
        if table not in pos_c:
            raise ValueError(f"Table '{table}' is present in S but not in C")
        pos_in_c = pos_c[table]
        pos_in_s = i + 1  # 1-based indexing
        sum_dist += abs(pos_in_s - pos_in_c)
        
    # Normalize the distance
    normalized_l1 = sum_dist / len(C)
    
    return normalized_l1

def parse_results_file(filename):
    """Parse query plans from a results file."""
    plans = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Split by comma and handle quoted join order
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 2:
                continue
                
            sql_file = parts[0].strip()
            join_order = parts[1].strip(' "')  # Remove quotes
            
            plans[sql_file] = join_order
            
    return plans

def save_results(compass_plans, postgres_plans, output_file):
    """Save L1 distances between corresponding query plans."""
    with open(output_file, 'w') as f:
        f.write("L1 Distance Results between Compass and PostgreSQL Query Plans\n")
        f.write("=====================================================\n\n")
        
        # Process all SQL files that appear in both sets
        for sql_file in sorted(set(compass_plans.keys()) & set(postgres_plans.keys())):
            compass_plan = compass_plans[sql_file]
            postgres_plan = postgres_plans[sql_file]
            
            f.write(f"SQL File: {sql_file}\n")
            f.write("-" * len(f"SQL File: {sql_file}") + "\n")
            
            try:
                distance = l1_distance(compass_plan, postgres_plan)
                tables = extract_tables(compass_plan)
                
                f.write(f"Tables ({len(tables)}): {', '.join(tables)}\n")
                f.write(f"Compass Plan:  {compass_plan}\n")
                f.write(f"Postgres Plan: {postgres_plan}\n")
                f.write(f"L1 Distance:   {distance:.4f}\n")
                f.write("\n")
            except ValueError as e:
                f.write(f"Error: {str(e)}\n\n")

if __name__ == "__main__":
    # Parse both result files
    compass_plans = parse_results_file(compass_file)
    postgres_plans = parse_results_file(postgres_file)
    
    # Calculate and save L1 distances
    save_results(compass_plans, postgres_plans, output_file)
    print(f"Results have been saved to {output_file}")
