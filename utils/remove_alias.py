import os
import re

# Directory containing SQL files
SQL_DIRECTORY = os.path.join(os.path.dirname(__file__), '../job')

# Function to remove aliases from SQL query
def remove_aliases_from_sql(sql_content):
    # Simple regex to find and remove aliases (e.g., 'AS alias_name')
    return re.sub(r'\bAS\s+\w+', '', sql_content, flags=re.IGNORECASE)

# Function to replace aliases with full table names in SQL queries
def replace_aliases_with_table_names(sql_content):
    # Regex to find table aliases in the FROM clause
    alias_pattern = re.compile(r'(\bFROM\s+\w+\s+AS\s+\w+)', re.IGNORECASE)
    matches = alias_pattern.findall(sql_content)
    
    for match in matches:
        # Extract table name and alias
        parts = match.split()
        table_name = parts[1]
        alias = parts[3]
        
        # Replace alias with table name in the SQL content
        sql_content = re.sub(rf'\b{alias}\.', f'{table_name}.', sql_content)

    return sql_content

# Function to process all SQL files in the directory
def process_sql_files():
    count = 0
    for filename in os.listdir(SQL_DIRECTORY):
        if filename.endswith('.sql'):
            file_path = os.path.join(SQL_DIRECTORY, filename)
            try:
                with open(file_path, 'r') as file:
                    sql_content = file.read()
                # Replace aliases with table names
                updated_sql_content = replace_aliases_with_table_names(sql_content)
                # Write the updated SQL back to the file
                with open(file_path, 'w') as file:
                    file.write(updated_sql_content)
                count += 1
                print(f"Processed {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    print(f"\nCompleted! Processed {count} SQL files.")

if __name__ == "__main__":
    process_sql_files()