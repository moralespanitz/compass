import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tempfile
import os
import graphviz

sql_files = [f for f in os.listdir('/Users/moralespanitz/me/undergraduate/ads/final/compass/job') if f.endswith('.sql')]

def analyze_sql(query, sql_file):
    cardinality_data = {
        'Compass': np.random.randint(1000, 10000, 50),
        'PostgreSQL': np.random.randint(2000, 20000, 50)
    }
    runtime_data = {
        'Compass': np.random.uniform(0.02, 0.28, 50),
        'PostgreSQL': np.random.uniform(0.01, 0.05, 50)
    }
    l1_distances = np.random.uniform(1.5, 4.5, 30)
    table_counts = np.random.randint(4, 15, 30)

    return [
        plot_cardinality_comparison(cardinality_data),
        plot_runtime_comparison(runtime_data),
        plot_l1_distance(l1_distances, table_counts),
        plot_winning_analysis(),
        visualize_join_plans(sql_file)
    ]

def plot_cardinality_comparison(data):
    plt.figure(figsize=(8, 6))
    plt.yscale('log')
    plt.bar(range(len(data['Compass'])), data['Compass'], label='Compass', alpha=0.7)
    plt.bar(range(len(data['PostgreSQL'])), data['PostgreSQL'], label='PostgreSQL', alpha=0.7)
    plt.xlabel('Query Index')
    plt.ylabel('Intermediate Rows (log scale)')
    plt.title('Comparison of Intermediate Rows: Compass vs PostgreSQL')
    plt.legend()
    return save_plot()

def plot_runtime_comparison(data):
    plt.figure(figsize=(8, 6))
    plt.plot(range(len(data['Compass'])), data['Compass'], 'b.-', label='Compass')
    plt.plot(range(len(data['PostgreSQL'])), data['PostgreSQL'], 'r.-', label='PostgreSQL')
    plt.xlabel('SQL Files')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Runtime Comparison')
    plt.legend()
    return save_plot()

def plot_l1_distance(distances, tables):
    plt.figure(figsize=(8, 6))
    plt.scatter(tables, distances)
    plt.xlabel('Number of Tables')
    plt.ylabel('L1 Distance')
    plt.title(f'L1 Distance vs Number of Tables\nCorrelation: {np.corrcoef(tables, distances)[0,1]:.2f}')
    return save_plot()

def plot_winning_analysis():
    plt.figure(figsize=(8, 6))
    winners = {'Compass': 87, 'PostgreSQL': 26}
    plt.bar(winners.keys(), winners.values(), color=['lightblue', 'salmon'])
    plt.title('Total Winning Queries')
    plt.ylabel('Number of Queries')
    for i, v in enumerate(winners.values()):
        plt.text(i, v + 1, f'{v}\n({v/(sum(winners.values()))*100:.1f}%)', ha='center')
    return save_plot()

def save_plot():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name)
    plt.close()
    return temp_file.name

def visualize_join_plans(query):
    compass_plan = {
        '1a.sql': "(ci ⨝ n ⨝ (mk ⨝ t ⨝ k))",
        # Add other queries as needed
    }
    postgres_plan = {
        '1a.sql': "(ci ⨝ n ⨝ (mk ⨝ t ⨝ k))",
        # Add other queries as needed
    }

    compass_graph = graphviz.Digraph('COMPASS')
    postgres_graph = graphviz.Digraph('Postgres')

    # Example for 1a.sql
    if query == '1a.sql':
        compass_graph.edge('ci', 'n')
        compass_graph.edge('n', 'mk')
        compass_graph.edge('mk', 't')
        compass_graph.edge('t', 'k')

        postgres_graph.edge('ci', 'n')
        postgres_graph.edge('n', 'mk')
        postgres_graph.edge('mk', 't')
        postgres_graph.edge('t', 'k')

    # Render the graphs
    compass_graph.render('compass_plan', format='png', cleanup=True)
    postgres_graph.render('postgres_plan', format='png', cleanup=True)

    return ['compass_plan.png', 'postgres_plan.png']

with gr.Blocks() as interface:
    gr.Markdown("# SQL Query Performance Analyzer")
    with gr.Row():
        # query_input = gr.Textbox(label="SQL Query", lines=5, placeholder="Enter your SQL query here...")
        file_input = gr.Dropdown(choices=sql_files, label="Select SQL File")
    
    with gr.Row():
        submit_btn = gr.Button("Analyze")
    
    with gr.Row():
        with gr.Column():
            card_plot = gr.Image(label="Cardinality Comparison")
        with gr.Column():
            runtime_plot = gr.Image(label="Runtime Analysis")
    
    with gr.Row():
        with gr.Column():
            l1_plot = gr.Image(label="L1 Distance Analysis")
        with gr.Column():
            win_plot = gr.Image(label="Winning Queries Analysis")
            
    with gr.Row():
        with gr.Column():
            compass_plan = gr.Image(label="COMPASS Join Plan")
        with gr.Column():
            postgres_plan = gr.Image(label="Postgres Join Plan")
            
    submit_btn.click(
        analyze_sql,
        inputs=[file_input],
        outputs=[card_plot, runtime_plot, l1_plot, win_plot, compass_plan, postgres_plan]
    )

if __name__ == "__main__":
    interface.launch()