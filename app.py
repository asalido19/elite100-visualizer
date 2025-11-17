#!/usr/bin/env python3
"""
Elite 100 Visualizer - Interactive Dash App
Allows filtering by brand, drivetrain, and engine type with real-time visualization updates
"""

import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re
from pathlib import Path
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# ============================================================================
# Data Loading and Parsing
# ============================================================================

DATA_PATH = Path('elite100.csv')
df = pd.read_csv(DATA_PATH, skipinitialspace=True)

# Strip spaces from column names
df.columns = df.columns.str.strip()

# Strip trailing spaces from string columns
string_cols = df.select_dtypes(include='object').columns
for col in string_cols:
    df[col] = df[col].str.strip()

# ============================================================================
# Time Parsing Functions
# ============================================================================

def parse_time_to_seconds(t):
    """Convert time string like '01:39.289' to seconds (float)"""
    if pd.isna(t):
        return np.nan
    s = str(t).strip()
    m = re.match(r'^(?:(\d+):)?(\d{1,2}(?:\.\d+)?)$', s)
    if m:
        min_part = m.group(1)
        sec_part = m.group(2)
        minutes = int(min_part) if min_part is not None else 0
        try:
            seconds = float(sec_part)
        except ValueError:
            return np.nan
        return minutes * 60.0 + seconds
    nums = re.findall(r'\d+\.?\d*', s)
    if len(nums) == 1:
        return float(nums[0])
    return np.nan

def seconds_to_duration(sec, decimals=3):
    """Convert seconds (float) to mm:ss format"""
    if pd.isna(sec):
        return ''
    minutes = int(sec // 60)
    remaining_sec = sec % 60
    if decimals == 1:
        return f'{minutes:02d}:{remaining_sec:04.1f}'
    else:
        return f'{minutes:02d}:{remaining_sec:06.3f}'

# ============================================================================
# Data Preparation
# ============================================================================

df['Time_sec'] = df['Time'].apply(parse_time_to_seconds)
df['Time_orig'] = df['Time']
df['Time_duration'] = df['Time_sec'].apply(seconds_to_duration)

df_plot = df.dropna(subset=['Brand', 'Time_sec']).copy()
df_plot['Brand'] = df_plot['Brand'].astype(str)
df_plot['EngineL_clean'] = pd.to_numeric(df_plot['EngineL'], errors='coerce')

# Get unique values for filters
all_brands = sorted(df_plot['Brand'].unique().tolist())
all_drivetrains = sorted(df_plot['Drivetrain'].unique().tolist())
all_engine_types = sorted(df_plot['EngineType'].unique().tolist())

# ============================================================================
# Dash App Setup
# ============================================================================

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title='Elite 100 Visualizer')

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1([
                    html.Span("ELITE ", style={'color': '#FFD700', 'marginRight': '0px'}),
                    html.Span("100", style={'color': '#000000', 'WebkitTextStroke': '2px #FFD700', 'marginRight': '12px'}),
                    html.Span("visualizer", style={'color': '#888888', 'fontSize': '28px', 'fontStyle': 'italic', 'verticalAlign': 'middle'})
                ], style={'marginTop': '16px', 'marginBottom': '16px', 'textAlign': 'left', 'display': 'flex', 'alignItems': 'center'})
            ])
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='filter-stats', className="text-muted small")
        ], id='stats-col', md=3),
        
        dbc.Col([
            dbc.Row([
                dbc.Col([html.Label("Brand:", className="fw-bold")], width=5, style={'paddingRight': '0'}),
                dbc.Col([
                    dcc.Dropdown(
                        id='brand-dropdown',
                        options=[{'label': 'All Brands', 'value': 'ALL'}] + 
                                [{'label': b, 'value': b} for b in all_brands],
                        value='ALL',
                        multi=True,
                        clearable=False,
                        style={'color': 'black', 'backgroundColor': 'white', 'width': '100%'}
                    )
                ], style={'paddingLeft': '8px', 'flex': '1'})
            ], className="mb-3 g-0", style={'alignItems': 'flex-start', 'width': '100%'}),
            
            dbc.Row([
                dbc.Col([html.Label("Drivetrain:", className="fw-bold")], width=5, style={'paddingRight': '0'}),
                dbc.Col([
                    dcc.Dropdown(
                        id='drivetrain-dropdown',
                        options=[{'label': 'All', 'value': 'ALL'}] + 
                                [{'label': d, 'value': d} for d in all_drivetrains],
                        value='ALL',
                        multi=True,
                        clearable=False,
                        style={'color': 'black', 'backgroundColor': 'white', 'width': '100%'}
                    )
                ], style={'paddingLeft': '8px', 'flex': '1'})
            ], className="mb-3 g-0", style={'alignItems': 'flex-start', 'width': '100%'}),
            
            dbc.Row([
                dbc.Col([html.Label("Engine Type:", className="fw-bold")], width=5, style={'paddingRight': '0'}),
                dbc.Col([
                    dcc.Dropdown(
                        id='engine-dropdown',
                        options=[{'label': 'All', 'value': 'ALL'}] + 
                                [{'label': e, 'value': e} for e in all_engine_types],
                        value='ALL',
                        multi=False,
                        clearable=False,
                        style={'color': 'black', 'backgroundColor': 'white', 'width': '100%'}
                    )
                ], style={'paddingLeft': '8px', 'flex': '1'})
            ], className="mb-3 g-0", style={'alignItems': 'flex-start', 'width': '100%'}),
            
            dbc.Row([
                dbc.Col([html.Label("Model, Chassis:", className="fw-bold")], width=5, style={'paddingRight': '0'}),
                dbc.Col([
                    dcc.Input(
                        id='model-chassis-input',
                        type='text',
                        placeholder='e.g., Civic Type R, 992.1',
                        style={'color': 'black', 'backgroundColor': 'white', 'width': '100%', 'padding': '8px'},
                        debounce=True
                    )
                ], style={'paddingLeft': '8px', 'flex': '1'})
            ], className="mb-2 g-0", style={'alignItems': 'flex-start', 'width': '100%'}),
            html.Div("Comma-separated, word match", className="small text-muted", style={'textAlign': 'right'})
        ], id='filters-col', md=6)
    ], className="mb-4 mt-4 g-3"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='elite-graph', style={'height': '800px', 'width': '100%', 'overflow': 'auto'}, responsive=True)
        ])
    ]),
    
], fluid=True, className="bg-dark text-white", style={'backgroundColor': '#111'})

# ============================================================================
# Callbacks for Dropdown "All" Selection Management
# ============================================================================

@callback(
    Output('brand-dropdown', 'value'),
    Input('brand-dropdown', 'value')
)
def update_brand_dropdown(selected_brands):
    """Remove 'ALL' from selection when specific brands are selected"""
    if selected_brands is None:
        return 'ALL'
    if isinstance(selected_brands, list):
        # If 'ALL' is selected with other items, remove 'ALL'
        if len(selected_brands) > 1 and 'ALL' in selected_brands:
            return [b for b in selected_brands if b != 'ALL']
        # If only 'ALL' is selected, keep it
        if selected_brands == ['ALL']:
            return 'ALL'
        # If nothing selected, default to 'ALL'
        if len(selected_brands) == 0:
            return 'ALL'
    return selected_brands

@callback(
    Output('drivetrain-dropdown', 'value'),
    Input('drivetrain-dropdown', 'value')
)
def update_drivetrain_dropdown(selected_drivetrain):
    """Remove 'ALL' from selection when specific drivetrains are selected"""
    if selected_drivetrain is None:
        return 'ALL'
    if isinstance(selected_drivetrain, list):
        # If 'ALL' is selected with other items, remove 'ALL'
        if len(selected_drivetrain) > 1 and 'ALL' in selected_drivetrain:
            return [d for d in selected_drivetrain if d != 'ALL']
        # If only 'ALL' is selected, keep it
        if selected_drivetrain == ['ALL']:
            return 'ALL'
        # If nothing selected, default to 'ALL'
        if len(selected_drivetrain) == 0:
            return 'ALL'
    return selected_drivetrain

# ============================================================================
# Callback for Dynamic Filtering and Visualization
# ============================================================================

@callback(
    [Output('elite-graph', 'figure'),
     Output('filter-stats', 'children')],
    [Input('brand-dropdown', 'value'),
     Input('drivetrain-dropdown', 'value'),
     Input('engine-dropdown', 'value'),
     Input('model-chassis-input', 'value')]
)
def update_visualization(selected_brands, selected_drivetrain, selected_engine, model_chassis_search):
    """Update the visualization based on filter selections"""
    
    # Apply filters
    filtered_df = df_plot.copy()
    
    # Handle multi-select brands (allow 'ALL' or list of brands)
    if selected_brands and not ('ALL' in selected_brands or selected_brands == 'ALL'):
        if isinstance(selected_brands, str):
            selected_brands = [selected_brands]
        filtered_df = filtered_df[filtered_df['Brand'].isin(selected_brands)]
    
    # Handle multi-select drivetrain
    if selected_drivetrain and not ('ALL' in selected_drivetrain or selected_drivetrain == 'ALL'):
        if isinstance(selected_drivetrain, str):
            selected_drivetrain = [selected_drivetrain]
        filtered_df = filtered_df[filtered_df['Drivetrain'].isin(selected_drivetrain)]
    
    if selected_engine != 'ALL':
        filtered_df = filtered_df[filtered_df['EngineType'] == selected_engine]
    
    # Handle model + chassis search (comma-separated, flexible word matching)
    if model_chassis_search and model_chassis_search.strip():
        search_terms = [term.strip().lower() for term in model_chassis_search.split(',')]
        # Match if any search term matches:
        # 1. Multi-word terms: exact match on model name
        # 2. Single-word terms: match any word in model name or chassis code
        def matches_any_term(model, chassis):
            model_lower = model.lower()
            chassis_lower = chassis.lower()
            model_words = model_lower.split()
            
            for term in search_terms:
                term_words = term.split()
                
                # Multi-word term: exact model match
                if len(term_words) > 1:
                    if term == model_lower:
                        return True
                else:
                    # Single-word term: match in model words or chassis
                    if term in model_words or term == chassis_lower:
                        return True
            return False
        filtered_df = filtered_df[filtered_df.apply(lambda row: matches_any_term(row['Model'], row['ChassisCode']), axis=1)]
    
    # Sort brands by fastest time
    if len(filtered_df) > 0:
        brand_fastest_time = filtered_df.groupby('Brand')['Time_sec'].min().sort_values()
        brand_order_simple = brand_fastest_time.index.tolist()
        brand_position_simple = {brand: i for i, brand in enumerate(brand_order_simple)}
        filtered_df = filtered_df.copy()
        filtered_df['Brand_X_simple'] = filtered_df['Brand'].map(brand_position_simple)
        
        # Calculate max text width
        brand_max_text_width = {}
        for brand in brand_order_simple:
            df_brand = filtered_df[filtered_df['Brand'] == brand]
            max_length = max([len(f"{row['Model']} {row['ChassisCode']}") for _, row in df_brand.iterrows()] or [0])
            brand_max_text_width[brand] = max_length
        
        char_width = 0.08
        max_brand_width = max(brand_max_text_width.values()) * char_width if brand_max_text_width else 0
        
        # Calculate responsive width: limit to 95% of common desktop width (1920px)
        # This allows for horizontal scrolling while respecting viewport constraints
        num_brands = len(brand_order_simple)
        # Base calculation: 100px per brand + 500px for margins/legend + text width
        content_width = num_brands * 100 + 500 + (max_brand_width * 200)
        # Cap at reasonable maximum (1600px) to fit most desktop viewports
        responsive_width = min(1600, max(900, content_width))
    else:
        brand_order_simple = []
        max_brand_width = 0
        responsive_width = 900
    
    # Create figure
    fig_simple = go.Figure()
    
    # Add vertical lines for each brand
    for i in range(len(brand_order_simple)):
        fig_simple.add_vline(x=i, line_dash='solid', line_color='rgba(0,0,0,0.5)', layer='below')
    
    # Sort entries and create visualization
    if len(filtered_df) > 0:
        df_sorted = filtered_df.sort_values(['Brand_X_simple', 'Time_sec']).reset_index(drop=True)
        min_time = filtered_df['Time_sec'].min()
        
        # Define legend order
        legend_order = [
            ('NA', 'RWD'), ('FI', 'RWD'),
            ('NA', 'AWD'), ('FI', 'AWD'),
            ('NA', 'FWD'), ('FI', 'FWD')
        ]
        
        # Add traces
        for engine_type, drivetrain in legend_order:
            df_subset = df_sorted[(df_sorted['EngineType'] == engine_type) & (df_sorted['Drivetrain'] == drivetrain)]
            
            if len(df_subset) == 0:
                continue
            
            legend_name = f"{drivetrain} {engine_type}"
            is_first = True
            
            for idx, row in df_subset.iterrows():
                y_pos = row['Time_sec']
                x_pos = row['Brand_X_simple']
                
                hover_text = (
                    f"<b>{row['Name']}</b><br>"
                    f"Model: {row['Model']}<br>"
                    f"Brand: {row['Brand']}<br>"
                    f"Time: {row['Time_duration']}<br>"
                    f"Engine: {row['EngineL']}L ({row['EngineType']})<br>"
                    f"Drivetrain: {row['Drivetrain']}<br>"
                    f"Rank: {row['Rank']}"
                )
                
                drivetrain_colors_simple = {
                    'RWD': 'rgb(255,0,0)',
                    'AWD': 'rgb(0,100,255)',
                    'FWD': 'rgb(0,255,0)'
                }
                text_color = drivetrain_colors_simple[drivetrain]
                
                marker_line = dict(width=2, color=text_color) if engine_type == 'FI' else dict(width=0)
                
                label_text = f"{row['Model']} {row['ChassisCode']}"
                
                # Add dot marker
                fig_simple.add_trace(go.Scatter(
                    x=[x_pos],
                    y=[y_pos],
                    mode='markers',
                    marker=dict(size=6, color=text_color if engine_type == 'NA' else 'rgba(0,0,0,0)',
                               line=marker_line, symbol='circle'),
                    hovertemplate=hover_text + '<extra></extra>',
                    name=legend_name,
                    showlegend=is_first,
                    legendgroup=legend_name
                ))
                
                # Add text label
                fig_simple.add_trace(go.Scatter(
                    x=[x_pos + 0.10],
                    y=[y_pos],
                    mode='text',
                    text=[label_text],
                    textposition='middle right',
                    textfont=dict(size=9, color='white'),
                    hoverinfo='skip',
                    showlegend=False,
                    legendgroup=legend_name
                ))
                
                is_first = False
        
        # Configure axes
        max_time = filtered_df['Time_sec'].max()
        
        tick_interval = 0.5
        tick_values = np.arange(np.ceil(min_time / tick_interval) * tick_interval,
                                max_time + tick_interval,
                                tick_interval)
        tick_values = np.sort(np.unique(np.concatenate([[min_time], tick_values])))
        
        tick_labels = []
        for t in tick_values:
            if t == min_time or (t % 1.0 < 0.01):
                tick_labels.append(seconds_to_duration(t, decimals=3))
            else:
                tick_labels.append('')
        
        fig_simple.update_yaxes(
            title_text='Lap Time - lowest is fastest',
            tickvals=tick_values,
            ticktext=tick_labels,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgb(80,80,80)'
        )
        
        x_max = len(brand_order_simple) - 1 + max_brand_width + 0.5
        fig_simple.update_xaxes(
            title_text='Brand (sorted by fastest time →)',
            tickvals=list(range(len(brand_order_simple))),
            ticktext=brand_order_simple,
            tickangle=45,
            range=[-0.5, x_max],
            fixedrange=True
        )
    
    fig_simple.update_layout(
        title='',
        height=800,
        width=responsive_width,
        autosize=False,
        margin=dict(l=60, r=30, t=20, b=160),
        hovermode='closest',
        plot_bgcolor='rgb(50,50,50)',
        paper_bgcolor='rgb(0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgb(80,80,80)', zerolinecolor='rgb(80,80,80)'),
        yaxis=dict(gridcolor='rgb(80,80,80)', zerolinecolor='rgb(80,80,80)'),
        legend=dict(
            traceorder='normal',
            yanchor='top',
            y=0.99,
            xanchor='right',
            x=0.99
        )
    )
    
    # Generate stats text
    total_vehicles = len(filtered_df)
    total_brands = filtered_df['Brand'].nunique() if len(filtered_df) > 0 else 0
    
    # Find fastest laptime
    if len(filtered_df) > 0:
        fastest_idx = filtered_df['Time_sec'].idxmin()
        fastest_row = filtered_df.loc[fastest_idx]
        stats_text = html.Div([
            html.Div(f"📊 {total_vehicles} vehicles | {total_brands} brands", 
                     style={'marginBottom': '12px', 'fontSize': '13px', 'color': 'white', 'textAlign': 'center'}),
            html.Div([
                html.Div("⚡ Fastest Laptime", style={'fontSize': '13px', 'marginBottom': '6px'}),
                html.Div(fastest_row['Name'], style={'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '8px'}),
                html.Div(fastest_row['Time_duration'], style={'marginBottom': '4px'}),
                html.Div(f"{fastest_row['Year']} {fastest_row['Brand']} {fastest_row['Model']} {fastest_row['ChassisCode']}", style={'marginBottom': '4px'}),
                html.Div(f"{fastest_row['EngineL']}L {fastest_row['EngineType']} - {fastest_row['Drivetrain']}", style={'marginBottom': '4px'}),
                html.Div(f"{fastest_row['RaceEvent']} • {fastest_row['Date']}", style={'marginBottom': '4px'}),
                html.Div(f"Elite 100 Rank: {fastest_row['Rank']}")
            ], style={'borderTop': '1px solid #444', 'paddingTop': '8px', 'padding': '12px', 'backgroundColor': '#000000', 'color': 'white', 'textAlign': 'center', 'fontSize': '13px', 'lineHeight': '1.4', 'borderRadius': '4px'})
        ], style={'color': 'white', 'textAlign': 'center'})
    else:
        stats_text = html.Div([
            html.Div(f"📊 {total_vehicles} vehicles | {total_brands} brands", 
                     style={'marginBottom': '12px', 'fontSize': '13px', 'color': 'white', 'textAlign': 'center'})
        ], style={'color': 'white', 'textAlign': 'center'})
    
    return fig_simple, stats_text

# ============================================================================
# Callback for Dynamic Stats Column Width
# ============================================================================

@callback(
    Output('stats-col', 'md'),
    Input('filter-stats', 'children')
)
def update_stats_column_width(stats_content):
    """Dynamically adjust stats column width based on content"""
    # Calculate approximate text width
    # Default to md=3 (25%), but can expand to md=4 (33%) if needed
    if stats_content and hasattr(stats_content, '__len__'):
        # If content exists and has substantial info, give it more space
        try:
            # Check if there's fasteset info (longer content)
            content_str = str(stats_content)
            if 'Elite 100 Rank' in content_str or 'Event' in content_str:
                return 4  # 33% width for more details
        except:
            pass
    return 3  # Default 25% width

# ============================================================================
# Run App
# ============================================================================

if __name__ == '__main__':
    import os
    
    # Detect environment
    is_deployed = os.getenv('REPLIT_DEPLOYMENT') == '1'
    is_replit = os.getenv('REPL_ID') is not None
    
    if is_deployed:
        # Production deployment: use port 8050 (matches .replit config), no debug
        host = '0.0.0.0'
        port = 8050
        debug = False
        print("🚀 Running in production deployment - binding to 0.0.0.0:8050")
    elif is_replit:
        # Replit development: use port 5000 for webview, with debug
        host = '0.0.0.0'
        port = 5000
        debug = True
        print("🚀 Running on Replit development - binding to 0.0.0.0:5000")
    else:
        # Local development
        host = '127.0.0.1'
        port = 5000
        debug = True
        print("🚀 Starting Elite 100 Visualizer Dash App")
        print("📱 Open your browser to: http://127.0.0.1:5000")
    
    app.run(debug=debug, host=host, port=port)
