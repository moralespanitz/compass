import os
import re
import matplotlib.pyplot as plt

# Paths to the result files
compass_file_path = 'compass-resultados.txt'
postgres_file_path = 'postgres-resultados.txt'

# Function to parse a resultados.txt file
def parse_resultados(file_path):
    results = {}
    execution_time_pattern = re.compile(r"\b(\d+\.\d+) seconds\b")
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split(', ')
            if len(parts) >= 3:
                try:
                    sql_file = parts[0].strip() if len(parts) > 0 else 'Unknown'
                    total_rows = int(parts[1].split(': ')[1].strip()) if 'Total Intermediate Rows' in parts[1] else 'N/A'
                    # Use regex to extract execution time
                    match = execution_time_pattern.search(line)
                    if match:
                        execution_time = float(match.group(1))
                        results[sql_file] = {
                            'total_rows': total_rows,
                            'execution_time': execution_time
                        }
                        print(f"Parsed: {sql_file} with execution time {execution_time} seconds")
                    else:
                        print(f"Execution time not found in line: {line.strip()}")
                except (IndexError, ValueError) as e:
                    print(f"Skipping malformed line: {line.strip()} due to error: {e}")
    return results

# Parse both files
compass_results = parse_resultados(compass_file_path)
postgres_results = parse_resultados(postgres_file_path)

# Debugging: Print parsed results
print("Compass Results:", compass_results)
print("Postgres Results:", postgres_results)

# Compare the results
comparison = []
for sql_file in compass_results:
    if sql_file in postgres_results:
        compass_exec_time = compass_results[sql_file]['execution_time']
        postgres_exec_time = postgres_results[sql_file]['execution_time']
        compass_rows = compass_results[sql_file]['total_rows']
        postgres_rows = postgres_results[sql_file]['total_rows']
        comparison.append({
            'sql_file': sql_file,
            'compass_exec_time': compass_exec_time,
            'postgres_exec_time': postgres_exec_time,
        })

# Debugging: Print comparison results
print("Comparison Results:", comparison)

# Debugging: Print comparison results
for result in comparison:
    print(f"SQL File: {result['sql_file']}")
    print(f"Compass Execution Time: {result['compass_exec_time']} seconds")
    print(f"Postgres Execution Time: {result['postgres_exec_time']} seconds")
    print("---")

# Extract data for plotting
sql_files = [result['sql_file'] for result in comparison]
compass_exec_times = [result['compass_exec_time'] for result in comparison]
postgres_exec_times = [result['postgres_exec_time'] for result in comparison]

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(sql_files, compass_exec_times, label='Compass Execution Time', marker='o')
plt.plot(sql_files, postgres_exec_times, label='Postgres Execution Time', marker='x')
plt.xlabel('SQL Files')
plt.ylabel('Execution Time (seconds)')
plt.title('Runtime Comparison')
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
# Save the plot as a PNG file
plt.savefig('runtime.png')
plt.show()