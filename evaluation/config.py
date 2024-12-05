import os

# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define common directories
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PLOTS_DIR = os.path.join(PROJECT_ROOT, 'plots')

# Result files
COMPASS_RESULTS = os.path.join(DATA_DIR, 'compass-resultados.txt')
POSTGRES_RESULTS = os.path.join(DATA_DIR, 'postgres-resultados.txt')
L1_DISTANCE_RESULTS = os.path.join(DATA_DIR, 'l1-distanceResults.txt')

# SQL directory
SQL_DIR = os.path.join(PROJECT_ROOT, 'job')

# Plot output paths
CARDINALITY_COMPARISON_PLOT = os.path.join(PLOTS_DIR, 'cardinality_comparison.png')
CARDINALITY_RATIO_PLOT = os.path.join(PLOTS_DIR, 'cardinality_ratio.png')

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)