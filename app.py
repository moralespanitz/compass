import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from evaluation.config import COMPASS_RESULTS as compass_filepath, POSTGRES_RESULTS as postgres_filepath, PLOTS_DIR
from evaluation import l1_distance, plot_l1_distance, cardinality, winning_queries

def load_data():
    # Get runtime data
    compass_results = parse_resultados(compass_filepath)
    postgres_results = parse_resultados(postgres_filepath)
    
    # Create comparison data
    comparison = []
    for sql_file in compass_results:
        if sql_file in postgres_results:
            compass_exec_time = compass_results[sql_file]['execution_time']
            postgres_exec_time = postgres_results[sql_file]['execution_time']
            comparison.append({
                'sql_file': sql_file,
                'compass_exec_time': compass_exec_time,
                'postgres_exec_time': postgres_exec_time,
            })
    return comparison

def create_runtime_plot():
    comparison = load_data()
    
    # Extract data for plotting
    sql_files = [result['sql_file'] for result in comparison]
    compass_exec_times = [result['compass_exec_time'] for result in comparison]
    postgres_exec_times = [result['postgres_exec_time'] for result in comparison]
    
    # Create plot
    plt.figure(figsize=(12, 6))
    plt.plot(sql_files, compass_exec_times, label='Compass Execution Time', marker='o')
    plt.plot(sql_files, postgres_exec_times, label='Postgres Execution Time', marker='x')
    plt.xlabel('SQL Files')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Runtime Comparison')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    # Save and return the plot
    runtime_plot = os.path.join(PLOTS_DIR, 'runtime.png')
    plt.savefig(runtime_plot)
    return runtime_plot

def calculate_statistics():
    comparison = load_data()
    
    # Calculate statistics
    total_queries = len(comparison)
    compass_wins = sum(1 for result in comparison 
                      if result['compass_exec_time'] < result['postgres_exec_time'])
    postgres_wins = sum(1 for result in comparison 
                       if result['postgres_exec_time'] < result['compass_exec_time'])
    
    # Format statistics text
    stats = f"""
    Total Queries: {total_queries}
    Compass Wins: {compass_wins} ({(compass_wins/total_queries)*100:.2f}%)
    Postgres Wins: {postgres_wins} ({(postgres_wins/total_queries)*100:.2f}%)
    """
    return stats

def run_all_analysis():
    # Run L1 distance analysis
    l1_distance.main()
    plot_l1_distance.main()
    
    # Run cardinality analysis
    cardinality.main()
    
    # Run winning queries analysis
    winning_queries.main()

def create_interface():
    with gr.Blocks() as interface:
        gr.Markdown("# Database Query Performance Analysis")
        
        with gr.Tab("Runtime Comparison"):
            gr.Image(create_runtime_plot(), label="Runtime Comparison Plot")
        
        with gr.Tab("Statistics"):
            gr.Textbox(calculate_statistics(), label="Performance Statistics", 
                      lines=5, interactive=False)
            
        with gr.Tab("Analysis"):
            run_button = gr.Button("Run Full Analysis")
            with gr.Row():
                with gr.Column():
                    gr.Image(os.path.join(PLOTS_DIR, "l1_distance_analysis.png"), label="L1 Distance Analysis")
                    gr.Image(os.path.join(PLOTS_DIR, "cardinality_comparison.png"), label="Cardinality Comparison")
                with gr.Column():
                    gr.Image(os.path.join(PLOTS_DIR, "cardinality_ratio.png"), label="Cardinality Ratio")
                    gr.Image(os.path.join(PLOTS_DIR, "winning_queries_analysis.png"), label="Winning Queries Analysis")
            
            run_button.click(fn=run_all_analysis)
    
    return interface

# Launch the interface
if __name__ == "__main__":
    # Run initial analysis
    run_all_analysis()
    
    # Launch the interface
    interface = create_interface()
    interface.launch()
