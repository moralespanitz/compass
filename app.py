import gradio as gr
import pandas as pd
import os
from pathlib import Path

COMPASS_RESULTS = "data/compass-resultados_cleaned.txt"
POSTGRES_RESULTS = "data/postgres-resultados_cleaned.txt"
JOB_DIR = "job"

def load_results():
    compass_df = pd.read_csv(COMPASS_RESULTS, names=['query', 'plan', 'joins', 'time'])
    postgres_df = pd.read_csv(POSTGRES_RESULTS, names=['query', 'plan', 'joins', 'time'])
    return compass_df, postgres_df

def get_sql_files():
    return sorted([f.name for f in Path(JOB_DIR).glob("*.sql")])

def display_results(sql_file):
    compass_df, postgres_df = load_results()
    compass_result = compass_df[compass_df['query'] == sql_file].iloc[0]
    postgres_result = postgres_df[postgres_df['query'] == sql_file].iloc[0]
    
    with open(os.path.join(JOB_DIR, sql_file), 'r') as f:
        query_content = f.read()
    
    html = f"""
    <div style='max-width: 1200px; margin: 0 auto;'>
        <div style='margin-top: 20px;'>
            <h3>SQL Query:</h3>
            <pre style='background: #f5f5f5; padding: 15px; border-radius: 4px; margin-bottom: 20px;'>{query_content}</pre>
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px;'>
            <div style='background: #f5f5f5; padding: 20px; border-radius: 8px;'>
                <h3>Compass Results</h3>
                <p><b>Joins:</b> {compass_result['joins']}</p>
                <p><b>Time:</b> {compass_result['time']} seconds</p>
                <p><b>Plan:</b></p>
                <pre style='white-space: pre-wrap; word-break: break-word;'>{compass_result['plan']}</pre>
            </div>
            <div style='background: #f5f5f5; padding: 20px; border-radius: 8px;'>
                <h3>Postgres Results</h3>
                <p><b>Joins:</b> {postgres_result['joins']}</p>
                <p><b>Time:</b> {postgres_result['time']} seconds</p>
                <p><b>Plan:</b></p>
                <pre style='white-space: pre-wrap; word-break: break-word;'>{postgres_result['plan']}</pre>
            </div>
        </div>
    </div>
    """
    return html

sql_files = get_sql_files()
iface = gr.Interface(
    fn=display_results,
    inputs=gr.Dropdown(choices=sql_files, label="Select SQL Query"),
    outputs=gr.HTML(),
    title="Query Results Comparison",
    description="Compare query execution results between Compass and Postgres"
)

if __name__ == "__main__":
    iface.launch()