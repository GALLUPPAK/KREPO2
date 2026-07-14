import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Household Consumption Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Clean, professional CSS
st.markdown("""
    <style>
    /* REMOVE INTERNAL SCROLLING - EXTEND VIEWPORT */
    .main {
        overflow: visible !important;
    }

    section.main > div {
        overflow: visible !important;
    }

    .block-container {
        overflow: visible !important;
        max-height: none !important;
    }

    /* Hide Streamlit's scrollbar */
    ::-webkit-scrollbar {
        display: none;
    }

    html, body {
        overflow: visible !important;
        height: auto !important;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* ... rest of your CSS ... */
    
    </style>
""", unsafe_allow_html=True)

# Constants
TOTAL_HOUSEHOLDS_PAKISTAN = 38_340_566  # 2023 Census data

# Clean, professional CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .item-title {
        font-size: 2rem;
        font-weight: 600;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3b82f6;
    }
    
    .info-box {
        background: #f0f9ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    
    /* STRETCH SIDEBAR TO FULL HEIGHT */
    [data-testid="stSidebar"] {
        min-height: 100vh !important;
        height: auto !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        min-height: 100vh !important;
        height: 100% !important;
        padding-bottom: 3rem;
    }
    
    /* Sidebar background color - extend to full height */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        min-height: 100vh;
    }
    
    section[data-testid="stSidebar"] > div {
        min-height: 100vh;
        background-color: #f8f9fa;
    }
    
    /* Remove extra spacing that causes gaps */
    .css-1d391kg {
        padding-bottom: 2rem !important;
    }
    
    /* For embedded view - hide scrollbars */
    section.main > div {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    
    .main .block-container {
        max-width: 100%;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load dataset with correct column mapping"""
    # Read with 2-row header
    df = pd.read_excel('data.xlsx', header=[0,1])
    
    # Create clean single-level column names
    new_col_names = []
    for i in range(len(df.columns)):
        col_map = {
            0: 'Serial_No',
            1: 'Consumption_Period',
            2: 'Item',
            # Columns D-I: Actual period values (not used in dashboard)
            3: 'Actual_Total', 4: 'Actual_Q1', 5: 'Actual_Q2', 
            6: 'Actual_Q3', 7: 'Actual_Q4', 8: 'Actual_Q5',
            # Columns J-N: Pre-calculated values
            9: 'Daily_Total_J',
            10: 'Yearly_Amount',
            11: 'Total_Households',
            12: 'Consuming_Households',  # Use this!
            13: 'Total_Market_Value',     # Use this!
            # Columns O-T: Daily expenditure by quintile (USE THESE!)
            14: 'Daily_Total',   # Column O
            15: 'Daily_Q1',      # Column P
            16: 'Daily_Q2',      # Column Q
            17: 'Daily_Q3',      # Column R
            18: 'Daily_Q4',      # Column S
            19: 'Daily_Q5',      # Column T
            # Quintile participation (columns 20-25)
            20: 'Total_Percent',  # Column U - Total (same as National)
            21: 'Q1_Percent',     # Column V - Quintile 1 participation
            22: 'Q2_Percent',     # Column W - Quintile 2 participation
            23: 'Q3_Percent',     # Column X - Quintile 3 participation
            24: 'Q4_Percent',     # Column Y - Quintile 4 participation
            25: 'Q5_Percent',     # Column Z - Quintile 5 participation
            # Provincial percentages (columns 26-30)
            26: 'KP_Percent',
            27: 'Punjab_Percent',
            28: 'Sindh_Percent',
            29: 'Balochistan_Percent',
            30: 'Islamabad_Percent',
            # National percentages (columns 31-33)
            31: 'National_Percent',  # Column AF - NATIONAL PARTICIPATION
            32: 'Rural_Percent',     # National Rural
            33: 'Urban_Percent',     # National Urban
            # Province Urban/Rural (columns 34+)
            34: 'KP_Rural_Percent',
            35: 'KP_Urban_Percent',
            36: 'Punjab_Rural_Percent',
            37: 'Punjab_Urban_Percent',
            38: 'Sindh_Rural_Percent',
            39: 'Sindh_Urban_Percent',
            40: 'Balochistan_Rural_Percent',
            41: 'Balochistan_Urban_Percent',
            42: 'Islamabad_Rural_Percent',
            43: 'Islamabad_Urban_Percent'
        }
        new_col_names.append(col_map.get(i, f'Col_{i}'))
    
    df.columns = new_col_names
    
    # Clean consumption period
    df['Consumption_Period'] = df['Consumption_Period'].str.strip().str.upper()
    
    # Extract item description
    df['Item_Code'] = df['Item'].astype(str).str.split(' ').str[0]
    df['Item_Description'] = df['Item'].astype(str).str.split(' ', n=1).str[1].fillna(df['Item'].astype(str))
    
    return df

def create_participation_chart(item_data):
    """Create participation rate chart by quintile"""
    quintiles = ['Q1\n(Poorest\n20%)', 'Q2\n(Lower-\nMiddle)', 'Q3\n(Middle\n20%)', 'Q4\n(Upper-\nMiddle)', 'Q5\n(Richest\n20%)']
    percentages = [
        item_data['Q1_Percent'] * 100,
        item_data['Q2_Percent'] * 100,
        item_data['Q3_Percent'] * 100,
        item_data['Q4_Percent'] * 100,
        item_data['Q5_Percent'] * 100
    ]
    
    colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6']
    
    # Calculate households per quintile (each quintile is 20% of total)
    households_per_quintile = TOTAL_HOUSEHOLDS_PAKISTAN * 0.2
    
    fig = go.Figure(go.Bar(
        x=quintiles,
        y=percentages,
        marker_color=colors,
        text=[f'{p:.1f}%' for p in percentages],
        textposition='outside',
        textfont=dict(size=14, weight='bold'),
        customdata=[[households_per_quintile * (p/100)] for p in percentages],
        hovertemplate='<b>%{x}</b><br>Participation: %{y:.1f}%<br>' +
                      'Households: %{customdata[0]:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '<b>% of Households That Consumed This Item (by Income Group)</b>',
            'font': {'size': 18, 'color': '#1e293b'}
        },
        yaxis_title='<b>Participation Rate (%)</b>',
        xaxis_title='<b>Income Quintile</b>',
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        yaxis=dict(gridcolor='#f1f5f9', range=[0, max(percentages) * 1.2])
    )
    
    return fig

def create_expenditure_chart_all_quintiles(item_data, period='FORTNIGHTLY'):
    """Create per capita expenditure chart with ALL quintiles"""
    quintiles = ['Q1\n(Poorest)', 'Q2', 'Q3\n(Middle)', 'Q4', 'Q5\n(Richest)']
    # Determine period multiplier
    if 'FORTNIGHTLY' in period.upper():
        mult = 14
    elif 'MONTHLY' in period.upper():
        mult = 30
    else:
        mult = 365
    
    values = [
        item_data['Daily_Q1'] * mult,
        item_data['Daily_Q2'] * mult,
        item_data['Daily_Q3'] * mult,
        item_data['Daily_Q4'] * mult,
        item_data['Daily_Q5'] * mult
    ]
    
    colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6']
    
    fig = go.Figure(go.Bar(
        x=quintiles,
        y=values,
        marker_color=colors,
        text=[f'PKR {v:,.0f}' for v in values],
        textposition='outside',
        textfont=dict(size=14, weight='bold'),
        hovertemplate='<b>%{x}</b><br>Daily: PKR %{y:,.2f}<br>' +
                      'Monthly: PKR ' + '%{customdata:,.0f}<extra></extra>',
        customdata=[v * 30 for v in values]
    ))
    
    fig.update_layout(
        title={
            'text': f'<b>{period} Per Capita Expenditure by Income Quintile</b>',
            'font': {'size': 18, 'color': '#1e293b'}
        },
        yaxis_title=f'<b>{period} Expenditure (PKR)</b>',
        xaxis_title='<b>Income Quintile</b>',
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        yaxis=dict(gridcolor='#f1f5f9')
    )
    
    return fig

def create_time_period_chart_all_quintiles(item_data):
    """Create expenditure across time periods for ALL quintiles"""
    periods = ['Daily', 'Weekly', 'Monthly', 'Yearly']
    
    # Calculate values for each quintile across periods
    quintile_data = {
        'Overall Pakistan': [item_data['Daily_Total'], item_data['Daily_Total'] * 7, 
                            item_data['Daily_Total'] * 30, item_data['Daily_Total'] * 365],
        'Q1 (Poorest 20%)': [item_data['Daily_Q1'], item_data['Daily_Q1'] * 7,
                              item_data['Daily_Q1'] * 30, item_data['Daily_Q1'] * 365],
        'Q2': [item_data['Daily_Q2'], item_data['Daily_Q2'] * 7,
               item_data['Daily_Q2'] * 30, item_data['Daily_Q2'] * 365],
        'Q3 (Middle 20%)': [item_data['Daily_Q3'], item_data['Daily_Q3'] * 7,
                            item_data['Daily_Q3'] * 30, item_data['Daily_Q3'] * 365],
        'Q4': [item_data['Daily_Q4'], item_data['Daily_Q4'] * 7,
               item_data['Daily_Q4'] * 30, item_data['Daily_Q4'] * 365],
        'Q5 (Richest 20%)': [item_data['Daily_Q5'], item_data['Daily_Q5'] * 7,
                             item_data['Daily_Q5'] * 30, item_data['Daily_Q5'] * 365]
    }
    
    colors = {
        'Overall Pakistan': '#8b5cf6',
        'Q1 (Poorest 20%)': '#ef4444',
        'Q2': '#f97316',
        'Q3 (Middle 20%)': '#eab308',
        'Q4': '#22c55e',
        'Q5 (Richest 20%)': '#3b82f6'
    }
    
    fig = go.Figure()
    
    for name, values in quintile_data.items():
        fig.add_trace(go.Bar(
            name=name,
            x=periods,
            y=values,
            marker_color=colors[name],
            text=[f'PKR {v:,.0f}' for v in values],
            textposition='inside' if name != 'Overall Pakistan' else 'outside',
            textfont=dict(size=10, color='white' if name != 'Overall Pakistan' else 'black'),
            hovertemplate=f'<b>{name}</b><br>%{{x}}: PKR %{{y:,.2f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': '<b>Per Capita Expenditure Across Time Periods (All Income Groups)</b>',
            'font': {'size': 18, 'color': '#1e293b'}
        },
        yaxis_title='<b>Expenditure (PKR)</b>',
        xaxis_title='<b>Time Period</b>',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        yaxis=dict(gridcolor='#f1f5f9'),
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_province_chart(item_data):
    """Create provincial participation chart"""
    provinces = ['Khyber\nPakhtunkhwa', 'Punjab', 'Sindh', 'Balochistan', 'Islamabad']
    percentages = [
        item_data['KP_Percent'] * 100,
        item_data['Punjab_Percent'] * 100,
        item_data['Sindh_Percent'] * 100,
        item_data['Balochistan_Percent'] * 100,
        item_data['Islamabad_Percent'] * 100
    ]
    
    # Colors representing each province
    colors = ['#16a34a', '#eab308', '#3b82f6', '#ef4444', '#8b5cf6']
    
    fig = go.Figure(go.Bar(
        x=provinces,
        y=percentages,
        marker_color=colors,
        text=[f'{p:.1f}%' for p in percentages],
        textposition='outside',
        textfont=dict(size=14, weight='bold'),
        hovertemplate='<b>%{x}</b><br>Participation: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '<b>Provincial Consumption Pattern</b>',
            'font': {'size': 18, 'color': '#1e293b'}
        },
        yaxis_title='<b>% of Households Consuming</b>',
        xaxis_title='<b>Province/Territory</b>',
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        yaxis=dict(gridcolor='#f1f5f9', range=[0, max(percentages) * 1.2])
    )
    
    return fig

def create_urban_rural_chart(item_data):
    """Create urban vs rural comparison chart"""
    locations = ['National\nRural', 'National\nUrban']
    percentages = [
        item_data['Rural_Percent'] * 100,
        item_data['Urban_Percent'] * 100
    ]
    
    colors = ['#16a34a', '#3b82f6']
    
    fig = go.Figure(go.Bar(
        x=locations,
        y=percentages,
        marker_color=colors,
        text=[f'{p:.1f}%' for p in percentages],
        textposition='outside',
        textfont=dict(size=16, weight='bold'),
        hovertemplate='<b>%{x}</b><br>Participation: %{y:.1f}%<extra></extra>',
        width=0.5
    ))
    
    fig.update_layout(
        title={
            'text': '<b>Urban vs Rural Consumption (National Level)</b>',
            'font': {'size': 18, 'color': '#1e293b'}
        },
        yaxis_title='<b>% of Households Consuming</b>',
        xaxis_title='<b>Area Type</b>',
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        yaxis=dict(gridcolor='#f1f5f9', range=[0, max(percentages) * 1.2])
    )
    
    return fig

def create_province_urban_rural_chart(item_data):
    """Create within-province urban vs rural comparison"""
    provinces = ['KP', 'Punjab', 'Sindh', 'Balochistan', 'Islamabad']
    
    rural_data = [
        item_data['KP_Rural_Percent'] * 100,
        item_data['Punjab_Rural_Percent'] * 100,
        item_data['Sindh_Rural_Percent'] * 100,
        item_data['Balochistan_Rural_Percent'] * 100,
        item_data['Islamabad_Rural_Percent'] * 100
    ]
    
    urban_data = [
        item_data['KP_Urban_Percent'] * 100,
        item_data['Punjab_Urban_Percent'] * 100,
        item_data['Sindh_Urban_Percent'] * 100,
        item_data['Balochistan_Urban_Percent'] * 100,
        item_data['Islamabad_Urban_Percent'] * 100
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Rural',
        x=provinces,
        y=rural_data,
        marker_color='#16a34a',
        text=[f'{v:.1f}%' for v in rural_data],
        textposition='inside',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{x} Rural</b><br>Participation: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        name='Urban',
        x=provinces,
        y=urban_data,
        marker_color='#3b82f6',
        text=[f'{v:.1f}%' for v in urban_data],
        textposition='inside',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{x} Urban</b><br>Participation: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '<b>Urban vs Rural Within Each Province</b>',
            'font': {'size': 18, 'color': '#1e293b'}
        },
        yaxis_title='<b>% of Households Consuming</b>',
        xaxis_title='<b>Province/Territory</b>',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        yaxis=dict(gridcolor='#f1f5f9'),
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_market_size_chart(item_data):
    """Create total market size visualization"""
    overall_participation = (item_data['National_Percent'] + item_data['National_Percent'] + 
                            item_data['National_Percent'] + item_data['National_Percent'] + 
                            item_data['National_Percent']) / 5
    
    total_consuming = TOTAL_HOUSEHOLDS_PAKISTAN * overall_participation
    total_not_consuming = TOTAL_HOUSEHOLDS_PAKISTAN * (1 - overall_participation)
    
    labels = ['Households<br>Consuming', 'Households NOT<br>Consuming']
    values = [total_consuming, total_not_consuming]
    # Vibrant colors that work in both light and dark mode
    colors = ['#10b981', '#f59e0b']  # Green for consuming, Orange for not consuming
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(
            colors=colors,
            line=dict(color='white', width=3)  # White border for better separation
        ),
        textposition='inside',
        textinfo='label+percent',
        textfont=dict(size=16, color='white', family='Inter, sans-serif', weight='bold'),
        hovertemplate='<b>%{label}</b><br>Count: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>',
        hole=0.5,  # Larger hole for better donut effect
        pull=[0.05, 0]  # Slightly pull out the consuming segment
    ))
    
    fig.update_layout(
        title={
            'text': f'<b>Total Market Size in Pakistan</b><br><sub>Based on {TOTAL_HOUSEHOLDS_PAKISTAN:,} households (2023 Census)</sub>',
            'font': {'size': 18, 'color': '#1e293b'}
        },
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[{
            'text': f'<b>{total_consuming/1_000_000:.2f}M</b><br><span style="font-size:14px">Households</span>',
            'x': 0.5, 'y': 0.5,
            'font': {'size': 24, 'color': '#10b981', 'family': 'Inter, sans-serif'},
            'showarrow': False
        }],
        font=dict(family='Inter, sans-serif'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color='#1e293b')
        )
    )
    
    return fig



@st.cache_data
def calc_total_market(df):
    """Calculate total market for all items"""
    total = 0
    for _, row in df.iterrows():
        part = row["National_Percent"]
        consuming = TOTAL_HOUSEHOLDS_PAKISTAN * part
        total += (row['Daily_Total'] * 365) * consuming
    return total

def create_comprehensive_export(df):
    """Create comprehensive Excel export with specific columns and formatting"""
    from io import BytesIO
    import openpyxl
    from openpyxl.styles import numbers
    
    export_data = []
    
    for _, row in df.iterrows():
        # Get period info
        period = str(row['Consumption_Period']).strip().upper()
        if 'FORTNIGHTLY' in period:
            period_name = 'Fortnightly'
        elif 'MONTHLY' in period:
            period_name = 'Monthly'
        else:
            period_name = 'Yearly'
        
        # Calculate key metrics
        national_participation = row['National_Percent']
        consuming_households = TOTAL_HOUSEHOLDS_PAKISTAN * national_participation
        
        # Yearly values
        yearly_total = row['Daily_Total'] * 365
        yearly_market_size = yearly_total * consuming_households
        
        export_data.append({
            'Market Rank': 0,  # Will be set after sorting
            'Item Name': row['Item'],
            'Survey Period': period_name,
            'Consuming Households': int(consuming_households),
            'Yearly Total Spend (PKR)': yearly_total,
            'Total Yearly Market Size (PKR)': yearly_market_size,
            '% of Total Market': 0,  # Will be calculated after sorting
            'Market Size (Billion PKR)': yearly_market_size / 1_000_000_000,
            'National Participation %': national_participation * 100,
            'National Rural %': row['Rural_Percent'] * 100,
            'National Urban %': row['Urban_Percent'] * 100,
            'Punjab %': row['Punjab_Percent'] * 100,
            'Sindh %': row['Sindh_Percent'] * 100,
            'KP %': row['KP_Percent'] * 100,
            'Balochistan %': row['Balochistan_Percent'] * 100,
            'Islamabad %': row['Islamabad_Percent'] * 100,
        })
    
    # Create DataFrame
    df_export = pd.DataFrame(export_data)
    
    # Sort by Total Yearly Market Size (descending)
    df_export = df_export.sort_values('Total Yearly Market Size (PKR)', ascending=False)
    df_export = df_export.reset_index(drop=True)
    
    # Add rank
    df_export['Market Rank'] = range(1, len(df_export) + 1)
    
    # Calculate % of total market
    total_market = df_export['Total Yearly Market Size (PKR)'].sum()
    df_export['% of Total Market'] = (df_export['Total Yearly Market Size (PKR)'] / total_market) * 100
    
    # Reorder columns to match exact specification
    column_order = [
        'Market Rank',
        'Item Name',
        'Survey Period',
        'Consuming Households',
        'Yearly Total Spend (PKR)',
        'Total Yearly Market Size (PKR)',
        '% of Total Market',
        'Market Size (Billion PKR)',
        'National Participation %',
        'National Rural %',
        'National Urban %',
        'Punjab %',
        'Sindh %',
        'KP %',
        'Balochistan %',
        'Islamabad %'
    ]
    
    df_export = df_export[column_order]
    
    # Create Excel file with formatting
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='All Items', index=False)
        
        # Get the worksheet
        worksheet = writer.sheets['All Items']
        
        # Format columns
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            # Consuming Households - thousands separator
            row[3].number_format = '#,##0'
            
            # Yearly Total Spend (PKR) - thousands separator, 2 decimals
            row[4].number_format = '#,##0.00'
            
            # Total Yearly Market Size (PKR) - thousands separator, 2 decimals
            row[5].number_format = '#,##0.00'
            
            # % of Total Market - 2 decimal places with %
            row[6].number_format = '0.00'
            
            # Market Size (Billion PKR) - 2 decimal places
            row[7].number_format = '#,##0.00'
            
            # All percentages (8-15) - 2 decimal places
            for col_idx in range(8, 16):
                row[col_idx].number_format = '0.00'
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output

def get_provincial_insight(item_name, prov_data, highest, lowest):
    """Item-specific provincial insight"""
    item_lower = item_name.lower()
    gap = prov_data[highest] - prov_data[lowest]
    
    if any(w in item_lower for w in ['milk', 'meat', 'chicken', 'beef', 'fish', 'egg', 'fruit', 'vegetable']):
        return f"**🍖 Food Analysis:** {highest} ({prov_data[highest]:.1f}%) shows highest consumption, {lowest} ({prov_data[lowest]:.1f}%) lowest. Gap of {gap:.1f}% reflects dietary preferences and income."
    elif any(w in item_lower for w in ['barber', 'salon', 'education', 'school', 'university', 'tuition']):
        return f"**💼 Service Analysis:** {highest} leads at {prov_data[highest]:.1f}%, {lowest} at {prov_data[lowest]:.1f}%. {gap:.1f}% variation indicates service availability and urbanization differences."
    elif any(w in item_lower for w in ['rent', 'electricity', 'gas', 'water', 'house']):
        return f"**🏠 Housing/Utility:** {highest} ({prov_data[highest]:.1f}%) vs {lowest} ({prov_data[lowest]:.1f}%). {gap:.1f}% difference reflects urbanization and housing markets."
    elif any(w in item_lower for w in ['transport', 'vehicle', 'petrol', 'cng']):
        return f"**🚗 Transportation:** {highest} shows {prov_data[highest]:.1f}% usage, {lowest} shows {prov_data[lowest]:.1f}%. {gap:.1f}% gap indicates infrastructure development."
    else:
        return f"**📊 Provincial Pattern:** {highest} leads ({prov_data[highest]:.1f}%), {lowest} lowest ({prov_data[lowest]:.1f}%). Regional variation: {gap:.1f}%"

def main():
    # Header with Gallup Pakistan branding
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        try:
            st.image("https://www.gallup.com.pk/Logo.png", width=150)
        except:
            st.markdown("**GALLUP PAKISTAN**")
    
    with col2:
        st.markdown('<h1 class="main-title">Household Consumption Analysis</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">Comprehensive Provincial & Urban-Rural Analysis | Powered by Gallup Pakistan</p>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("")  # Spacing
    
    # Educational Introduction
    with st.expander("📚 **How to Use This Dashboard** (Click to expand)", expanded=False):
        st.markdown("""
        ### Welcome! This dashboard helps you understand household consumption patterns across Pakistan.
        
        **What's Available:**
        - ✅ **Provincial breakdown** - See how KP, Punjab, Sindh, Balochistan, and Islamabad differ
        - ✅ **Urban vs Rural** - Compare city and village consumption patterns
        - ✅ **Market size** - See actual number of households consuming each item
        - ✅ **Complete quintile data** - All 5 income groups shown everywhere
        
        **How to Use:**
        1. **Select any item** from sidebar (all 285 items available)
        2. **Scroll through 8 sections** of analysis on this page
        3. **Read the blue explanation boxes** before each chart
        4. **Click "Learn More"** expandable sections for detailed concepts
        
        **What You'll Learn:**
        - Income inequality patterns
        - Geographic variations (provinces)
        - Urban-rural differences
        - Market sizing and business potential
        - Consumer behavior analysis
        
        💡 **Tip**: Compare similar items (e.g., Beef vs Chicken) to understand substitution patterns!
        """)
    
    # Load data
    try:
        df = load_data()
    except FileNotFoundError:
        st.error("❌ Data file not found! Please ensure 'data.xlsx' is in the same directory.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 Select Item to Analyze")
        st.markdown("---")
        
        st.info("💡 **Tip**: Use search to quickly find items!")
        
        search_term = st.text_input(
            "🔎 Search Items",
            placeholder="e.g., milk, rice, chicken",
            help="Type any word to filter the list"
        )
        
        if search_term:
            available_items = df[df['Item_Description'].str.contains(search_term, case=False, na=False)]['Item_Description'].tolist()
            if not available_items:
                st.warning(f"⚠️ No items found matching '{search_term}'. Showing all items.")
                available_items = df['Item_Description'].tolist()
        else:
            available_items = df['Item_Description'].tolist()
        
        # Ensure we have items before showing selectbox
        if available_items:
            selected_item = st.selectbox(
                "📦 Select Item",
                available_items,
                help=f"Choose from {len(available_items)} consumption items"
            )
        else:
            st.error("❌ No items available. Please check data file.")
            st.stop()
        
        st.markdown("---")
        
        with st.expander("❓ Quick Help"):
            st.markdown("""
            **Common Items to Explore:**
            - Milk fresh
            - Chicken Meat  
            - Rice
            - Wheat flour
            - Eggs
            - Beef
            
            **Key Analysis Points:**
            - Income inequality (Q1 vs Q5)
            - Urban vs Rural differences
            - Provincial variations
            - Market size potential
            """)
        
        st.markdown("---")
        st.markdown(f"📊 **Total Items:** {len(df)}")
        if search_term:
            st.markdown(f"🔍 **Filtered:** {len(available_items)}")
        
        # Export Button
        st.markdown("---")
        st.markdown("### 📥 Export Data")
        
        if st.button("📊 Download All Items (Excel)", use_container_width=True, type="primary"):
            with st.spinner("Preparing comprehensive export..."):
                excel_file = create_comprehensive_export(df)
                st.download_button(
                    label="⬇️ Download Excel File",
                    data=excel_file,
                    file_name="household_consumption_analysis_all_items.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                st.success("✅ File ready! Click above to download.")
                st.caption("📋 Includes: All 285 items sorted by market size, participation rates, quintile data, provincial breakdown, and more!")
    
        
        st.markdown("---")
        st.markdown("### 💰 Total Market")
        total_mkt = calc_total_market(df)
        st.metric("All Items Combined", f"PKR {total_mkt/1_000_000_000_000:.2f}T")
        st.caption(f"{total_mkt/1_000_000_000:.0f}B PKR/year")

    # Get item data
    item_data = df[df['Item_Description'] == selected_item].iloc[0]
    consumption_period = str(item_data["Consumption_Period"]).strip()
    
    # Item Title
    st.markdown(f'''<div class="item-title">
        📦 {selected_item}
        <br>
        <span style="display:inline-block;background:#fbbf24;color:#78350f;padding:0.5rem 1.5rem;border-radius:20px;font-weight:700;font-size:1.1rem;margin-top:0.5rem;border:2px solid #f59e0b;">📅 {consumption_period} CONSUMPTION</span>
    </div>''', unsafe_allow_html=True)
    
    # Calculate overall participation
    overall_participation = (item_data['National_Percent'] + item_data['National_Percent'] + 
                            item_data['National_Percent'] + item_data['National_Percent'] + 
                            item_data['National_Percent']) / 5 * 100
    
    total_consuming_households = TOTAL_HOUSEHOLDS_PAKISTAN * (overall_participation / 100)
    
    # ===================================================================================
    # SECTION 1: OVERALL STATISTICS
    # ===================================================================================
    st.markdown('<div class="section-title">1️⃣ Overall National Statistics</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>📖 What this shows:</strong> Key summary statistics about this item at the national level.
        These numbers give you a quick overview before diving into details.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Determine period days for text
    if 'FORTNIGHTLY' in consumption_period:
        period_days = 14
        period_text = "fortnight"
    elif 'MONTHLY' in consumption_period:
        period_days = 30
        period_text = "month"
    else:
        period_days = 365
        period_text = "year"
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Participation Rate</div>
            <div class="metric-value" style="color: #3b82f6;">{overall_participation:.1f}%</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.5rem;">
                {overall_participation:.0f} out of 100<br>households buy this<br>in {period_days} days ({period_text})
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Total Market Size</div>
            <div class="metric-value" style="color: #10b981;">{total_consuming_households/1_000_000:.2f}M</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.5rem;">
                {total_consuming_households:,.0f}<br>households nationwide
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">{consumption_period} Spending</div>
            <div class="metric-value" style="color: #f59e0b;">PKR {(item_data['Daily_Total'] * (14 if 'FORTNIGHTLY' in consumption_period else 30 if 'MONTHLY' in consumption_period else 365)):,.2f}</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.5rem;">
                Per household<br>(average)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        inequality_ratio = item_data['Daily_Q5'] / item_data['Daily_Q1'] if item_data['Daily_Q1'] > 0 else 0
        color = '#22c55e' if inequality_ratio < 2 else '#eab308' if inequality_ratio < 4 else '#ef4444'
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Income Inequality</div>
            <div class="metric-value" style="color: {color};">{inequality_ratio:.2f}x</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.5rem;">
                Rich spend {inequality_ratio:.1f}x<br>more than poor
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        yearly_per_hh = item_data['Daily_Total'] * 365
        total_mkt_pkr = yearly_per_hh * total_consuming_households
        st.markdown(f"""
        <div class="metric-box" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border: 3px solid #92400e; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);">
            <div class="metric-label" style="color: white; font-weight: 700; font-size: 1rem;">💰 TOTAL MARKET SIZE</div>
            <div class="metric-value" style="color: white; font-size: 2.2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">PKR {total_mkt_pkr/1_000_000_000:.2f}B</div>
            <div style="font-size: 0.8rem; color: #fef3c7; margin-top: 0.5rem; font-weight: 600;">
                YEARLY MARKET VALUE<br>FOR THIS ITEM
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"📊 **Calculation:** PKR {item_data['Daily_Total']:,.2f}/day × 365 days × {total_consuming_households:,.0f} households")
    
    # Explanation of key metrics
    with st.expander("💡 **Understanding These Metrics** (Click to learn)"):
        st.markdown(f"""
        ### What Do These Numbers Mean?
        
        #### 🔹 **Participation Rate: {overall_participation:.1f}%**
        - **Simple meaning**: Out of 100 Pakistani households, about **{overall_participation:.0f} buy this item**
        - **How calculated**: Average of all 5 income groups (quintiles)
        - **Why it matters**: Shows if item is common (>50%), regular (20-50%), or rare (<20%)
        
        #### 🔹 **Total Market Size: {total_consuming_households/1_000_000:.2f} Million Households**
        - **What it is**: Actual number of Pakistani households consuming this item
        - **Formula**: {TOTAL_HOUSEHOLDS_PAKISTAN:,} total households × {overall_participation:.1f}% participation
        - **Why businesses care**: Shows potential customer base for this product
        - **Context**: Pakistan has **38.34 million households** (2023 Census)
        
        #### 🔹 **Daily Spending: PKR {item_data['Daily_Total']:,.2f}**
        - **What it is**: Average amount one household spends per day on this item
        - **Monthly impact**: PKR {item_data['Daily_Total'] * 30:,.2f} per month
        - **Yearly impact**: PKR {item_data['Daily_Total'] * 365:,.2f} per year
        - **Note**: This is a **median** (middle value), not average
        
        #### 🔹 **Income Inequality: {inequality_ratio:.2f}x**
        - **What it means**: Richest 20% spend **{inequality_ratio:.1f} times more** than poorest 20%
        - **Classification**:
          - Low inequality (<2x): Similar spending across rich and poor → **Necessity**
          - Moderate (2-4x): Noticeable difference → **Normal good**
          - High (>4x): Large gap → **Luxury good**
        - **This item**: **{"Low inequality - Basic necessity" if inequality_ratio < 2 else "Moderate inequality - Normal good" if inequality_ratio < 4 else "High inequality - Luxury item"}**
        
        #### 💰 **Total Market Size (Yearly PKR): PKR {(item_data['Daily_Total'] * 365 * total_consuming_households)/1_000_000_000:.2f} Billion**
        - **What it is**: TOTAL yearly spending on this item across ALL of Pakistan
        - **Formula**: Daily spending × 365 days × Total consuming households
        - **Calculation**: PKR {item_data['Daily_Total']:,.2f} × 365 × {total_consuming_households:,.0f} = **PKR {(item_data['Daily_Total'] * 365 * total_consuming_households)/1_000_000_000:.2f}B**
        - **Why it matters**: 
          - Shows complete market opportunity for businesses
          - Indicates economic impact of this item
          - Helps with investment decisions
          - Used for policy planning and budgeting
        - **THIS IS A YEARLY VALUE** - represents annual market size
        """)
    
    # Market Size Visualization
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(create_market_size_chart(item_data), use_container_width=True)
    with col2:
        st.markdown("""
        ### 📊 Understanding Market Size
        
        **What the pie chart shows:**
        - Blue slice = Households consuming this item
        - Gray slice = Households NOT consuming
        
        **Why this matters:**
        """)
        
        if overall_participation > 50:
            st.success(f"""
            ✅ **Large Market** ({overall_participation:.0f}% participation)
            - Over half of Pakistani households buy this
            - Mass market product
            - High business potential
            - Essential/common item
            """)
        elif overall_participation > 20:
            st.info(f"""
            ℹ️ **Medium Market** ({overall_participation:.0f}% participation)
            - Regular item with steady demand
            - Moderate business potential
            - Normal consumer good
            """)
        else:
            st.warning(f"""
            ⚠️ **Niche Market** ({overall_participation:.0f}% participation)
            - Specialized or luxury item
            - Limited target audience
            - Small but focused market
            """)
    
    # ===================================================================================
    # SECTION 2: INCOME GROUP ANALYSIS
    # ===================================================================================
    st.markdown('<div class="section-title">2️⃣ Who Buys This Item? (Income Analysis)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>📖 What this shows:</strong> Participation rates across 5 income groups (quintiles).
        This tells us if this item is consumed equally by all income levels, or mainly by rich/poor.
        <br><br>
        <strong>💡 Key concept:</strong> Quintile = 20% of population. Q1 = poorest 20%, Q5 = richest 20%.
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(create_participation_chart(item_data), use_container_width=True)
    
    # Interpretation
    participation_gap = (item_data['National_Percent'] - item_data['National_Percent']) * 100
    
    st.markdown("### 📊 Pattern Analysis:")
    
    if abs(participation_gap) < 10:
        st.success(f"""
        ✅ **Equal Participation Pattern**
        - Gap between rich and poor: Only {abs(participation_gap):.1f}%
        - **Interpretation**: This is a **necessity** or **basic staple**
        - All income groups need/use this item equally
        - Examples of similar items: Salt, basic grains, water
        """)
    elif participation_gap > 10:
        st.warning(f"""
        📈 **Rich Buy More Pattern**
        - Rich households are **{participation_gap:.1f}% more likely** to buy this
        - **Interpretation**: This is a **normal good** or **luxury item**
        - As income increases, people buy more of this
        - Higher income = higher quality or more quantity
        """)
    else:
        st.info(f"""
        📉 **Poor Buy More Pattern**
        - Poor households are **{abs(participation_gap):.1f}% more likely** to buy this
        - **Interpretation**: This is an **inferior good**
        - Rich people switch to better alternatives
        - Example: Cheap grains instead of expensive ones
        """)
    
    # ===================================================================================
    # SECTION 3: HOW MUCH DO THEY SPEND
    # ===================================================================================
    st.markdown('<div class="section-title">3️⃣ How Much Do They Spend? (All Income Groups)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>📖 What this shows:</strong> {consumption_period} spending amount for EACH income group.
        Even if everyone buys an item, richer people might spend more (buying premium quality or larger quantities).
        <br><br>
        <strong>🎯 Look for:</strong> The height difference between bars shows income inequality in spending.
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(create_expenditure_chart_all_quintiles(item_data, consumption_period), use_container_width=True)
    
    # Detailed breakdown of spending
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 💰 {consumption_period} Spending by Group:")
        st.markdown(f"""
        - **Q1 (Poorest)**: PKR {item_data['Daily_Q1'] * period_days:,.2f}
        - **Q2**: PKR {item_data['Daily_Q2'] * period_days:,.2f}  
        - **Q3 (Middle)**: PKR {item_data['Daily_Q3'] * period_days:,.2f}
        - **Q4**: PKR {item_data['Daily_Q4'] * period_days:,.2f}
        - **Q5 (Richest)**: PKR {item_data['Daily_Q5'] * period_days:,.2f}
        """)
    
    with col2:
        st.markdown("### 📊 Inequality Analysis:")
        if inequality_ratio > 4:
            st.error(f"""
            🔴 **High Inequality** ({inequality_ratio:.1f}x)
            - Large spending gap
            - Luxury or premium item
            - Rich spend much more
            """)
        elif inequality_ratio > 2:
            st.warning(f"""
            ⚠️ **Moderate Inequality** ({inequality_ratio:.1f}x)
            - Noticeable difference
            - Normal consumer good
            - Income matters
            """)
        else:
            st.success(f"""
            ✅ **Low Inequality** ({inequality_ratio:.1f}x)
            - Similar spending
            - Basic necessity
            - Everyone needs it equally
            """)
    
    # ===================================================================================
    
    # ===================================================================================
    # SECTION 4: PROVINCIAL ANALYSIS (Section 4 removed - renumbered from 5)
    # ===================================================================================
    st.markdown('<div class="section-title">4️⃣ Provincial Consumption Patterns</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>📖 What this shows:</strong> How consumption varies across Pakistan's provinces and territories.
        Geographic location affects what people buy due to culture, climate, and local availability.
        <br><br>
        <strong>🗺️ Pakistan's Divisions:</strong> KP (Khyber Pakhtunkhwa), Punjab, Sindh, Balochistan, and Islamabad Capital Territory.
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(create_province_chart(item_data), use_container_width=True)
    
    # Provincial comparison analysis
    province_data = {
        'KP': item_data['KP_Percent'] * 100,
        'Punjab': item_data['Punjab_Percent'] * 100,
        'Sindh': item_data['Sindh_Percent'] * 100,
        'Balochistan': item_data['Balochistan_Percent'] * 100,
        'Islamabad': item_data['Islamabad_Percent'] * 100
    }
    
    highest_province = max(province_data, key=province_data.get)
    lowest_province = min(province_data, key=province_data.get)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"""
        ⬆️ **Highest Consumption: {highest_province}**
        - **{province_data[highest_province]:.1f}%** of households consume this
        - {province_data[highest_province]:.0f} out of 100 households
        - This province shows highest demand
        """)
    
    with col2:
        st.warning(f"""
        ⬇️ **Lowest Consumption: {lowest_province}**
        - **{province_data[lowest_province]:.1f}%** of households consume this
        - {province_data[lowest_province]:.0f} out of 100 households
        - This province shows lowest demand
        """)
    
    gap = province_data[highest_province] - province_data[lowest_province]
    st.info(f"""
    📊 **Provincial Variation**: There's a **{gap:.1f}% difference** between highest and lowest consuming provinces.
    This shows {'strong regional preferences' if gap > 30 else 'moderate regional variation' if gap > 15 else 'relatively uniform consumption'} across Pakistan.
    """)
    
        # ===================================================================================
    # SECTION 6: URBAN VS RURAL (NATIONAL)
    # ===================================================================================
    st.markdown('<div class="section-title">5️⃣ Urban vs Rural Divide (National Level)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>📖 What this shows:</strong> Comparison between city (urban) and village (rural) consumption at the national level.
        <br><br>
        <strong>🏘️ Definitions:</strong>
        - <strong>Urban</strong> = Cities and towns with developed infrastructure
        - <strong>Rural</strong> = Villages and countryside areas
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(create_urban_rural_chart(item_data), use_container_width=True)
    
    # Analysis
    urban_rate = item_data['Urban_Percent'] * 100
    rural_rate = item_data['Rural_Percent'] * 100
    urban_rural_gap = urban_rate - rural_rate
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        ### 🏙️ Urban Areas
        **Participation**: {urban_rate:.1f}%
        
        {"✅ Higher consumption in cities" if urban_rural_gap > 10 else "✅ Similar to rural areas" if abs(urban_rural_gap) < 10 else "⬇️ Lower than rural"}
        
        **Characteristics:**
        - More income opportunities
        - Better market access
        - More variety available
        - Higher purchasing power
        """)
    
    with col2:
        st.markdown(f"""
        ### 🌾 Rural Areas
        **Participation**: {rural_rate:.1f}%
        
        {"✅ Higher consumption in villages" if urban_rural_gap < -10 else "✅ Similar to urban areas" if abs(urban_rural_gap) < 10 else "⬇️ Lower than urban"}
        
        **Characteristics:**
        - Agriculture-based economy
        - Traditional consumption
        - Local production
        - Limited market access
        """)
    
    if abs(urban_rural_gap) < 10:
        st.success(f"""
        ✅ **Minimal Urban-Rural Gap** ({abs(urban_rural_gap):.1f}% difference)
        - This item is consumed equally in cities and villages
        - Suggests it's a basic necessity available everywhere
        - No significant urban-rural divide for this product
        """)
    elif urban_rural_gap > 10:
        st.info(f"""
        🏙️ **Urban Preference** ({urban_rural_gap:.1f}% higher in cities)
        - Cities show higher consumption
        - Might be a modern/processed item
        - Could require refrigeration or special storage
        - Possibly more expensive or luxury item
        """)
    else:
        st.info(f"""
        🌾 **Rural Preference** ({abs(urban_rural_gap):.1f}% higher in villages)
        - Villages show higher consumption
        - Might be traditional or locally produced
        - Could be agricultural product
        - Possibly cheaper alternative item
        """)
    
    # ===================================================================================
    # SECTION 7: WITHIN-PROVINCE URBAN-RURAL
    # ===================================================================================
    st.markdown('<div class="section-title">6️⃣ Urban vs Rural Within Each Province</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>📖 What this shows:</strong> Urban-rural comparison separately for each province.
        This helps identify if urban-rural differences are consistent across Pakistan or vary by region.
        <br><br>
        <strong>🔍 What to look for:</strong> Are urban areas always higher? Or does it vary by province?
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(create_province_urban_rural_chart(item_data), use_container_width=True)
    
    # Detailed analysis
    st.markdown("### 📊 Provincial Urban-Rural Breakdown:")
    
    province_ur_data = {
        'Province': ['KP', 'Punjab', 'Sindh', 'Balochistan', 'Islamabad'],
        'Rural %': [
            f"{item_data['KP_Rural_Percent'] * 100:.1f}%",
            f"{item_data['Punjab_Rural_Percent'] * 100:.1f}%",
            f"{item_data['Sindh_Rural_Percent'] * 100:.1f}%",
            f"{item_data['Balochistan_Rural_Percent'] * 100:.1f}%",
            f"{item_data['Islamabad_Rural_Percent'] * 100:.1f}%"
        ],
        'Urban %': [
            f"{item_data['KP_Urban_Percent'] * 100:.1f}%",
            f"{item_data['Punjab_Urban_Percent'] * 100:.1f}%",
            f"{item_data['Sindh_Urban_Percent'] * 100:.1f}%",
            f"{item_data['Balochistan_Urban_Percent'] * 100:.1f}%",
            f"{item_data['Islamabad_Urban_Percent'] * 100:.1f}%"
        ],
        'Gap': [
            f"{(item_data['KP_Urban_Percent'] - item_data['KP_Rural_Percent']) * 100:+.1f}%",
            f"{(item_data['Punjab_Urban_Percent'] - item_data['Punjab_Rural_Percent']) * 100:+.1f}%",
            f"{(item_data['Sindh_Urban_Percent'] - item_data['Sindh_Rural_Percent']) * 100:+.1f}%",
            f"{(item_data['Balochistan_Urban_Percent'] - item_data['Balochistan_Rural_Percent']) * 100:+.1f}%",
            f"{(item_data['Islamabad_Urban_Percent'] - item_data['Islamabad_Rural_Percent']) * 100:+.1f}%"
        ]
    }
    
    province_ur_df = pd.DataFrame(province_ur_data)
    st.dataframe(province_ur_df, use_container_width=True, hide_index=True)
    
    st.markdown("""
    **💡 How to read the Gap column:**
    - **Positive (+)**: Urban areas consume MORE than rural
    - **Negative (-)**: Rural areas consume MORE than urban
    - **Near 0**: Similar consumption in both
    """)
    
    # ===================================================================================
    # SECTION 8: COMPLETE DATA TABLE
    # ===================================================================================
    st.markdown('<div class="section-title">7️⃣ Complete Data Reference Table</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>📖 What this shows:</strong> All numbers in one comprehensive table for easy reference and comparison.
        Use this section to copy specific data points for your research or assignments.
    </div>
    """, unsafe_allow_html=True)
    
    # Create comprehensive table with separate sections
    
    # Section 1: Income Groups
    # Income Group Analysis table removed - showed incorrect daily conversions
    
    # Section 2: Geographic - National Level
    st.markdown("#### 🗺️ National Geographic Analysis")
    national_geo_data = {
        'Geographic Division': [
            'National Rural',
            'National Urban',
            'Urban-Rural Gap',
            'Total Market Size',
            'Income Inequality (Q5/Q1)'
        ],
        'Value': [
            f"{item_data['Rural_Percent'] * 100:.1f}%",
            f"{item_data['Urban_Percent'] * 100:.1f}%",
            f"{urban_rural_gap:+.1f}%",
            f"{total_consuming_households:,.0f} households",
            f"{inequality_ratio:.2f}x"
        ]
    }
    national_geo_df = pd.DataFrame(national_geo_data)
    st.dataframe(national_geo_df, use_container_width=True, hide_index=True)
    
    # Section 3: Provincial Participation
    st.markdown("#### 🏛️ Provincial Participation Rates")
    provincial_data = {
        'Province/Territory': [
            'Khyber Pakhtunkhwa',
            'Punjab',
            'Sindh',
            'Balochistan',
            'Islamabad'
        ],
        'Participation Rate': [
            f"{item_data['KP_Percent'] * 100:.1f}%",
            f"{item_data['Punjab_Percent'] * 100:.1f}%",
            f"{item_data['Sindh_Percent'] * 100:.1f}%",
            f"{item_data['Balochistan_Percent'] * 100:.1f}%",
            f"{item_data['Islamabad_Percent'] * 100:.1f}%"
        ]
    }
    provincial_df = pd.DataFrame(provincial_data)
    st.dataframe(provincial_df, use_container_width=True, hide_index=True)
    
    # Section 4: Provincial Urban-Rural Breakdown
    st.markdown("#### 🏙️ Provincial Urban-Rural Breakdown")
    provincial_ur_data = {
        'Province': [
            'KP',
            'Punjab',
            'Sindh',
            'Balochistan',
            'Islamabad'
        ],
        'Rural %': [
            f"{item_data['KP_Rural_Percent'] * 100:.1f}%",
            f"{item_data['Punjab_Rural_Percent'] * 100:.1f}%",
            f"{item_data['Sindh_Rural_Percent'] * 100:.1f}%",
            f"{item_data['Balochistan_Rural_Percent'] * 100:.1f}%",
            f"{item_data['Islamabad_Rural_Percent'] * 100:.1f}%"
        ],
        'Urban %': [
            f"{item_data['KP_Urban_Percent'] * 100:.1f}%",
            f"{item_data['Punjab_Urban_Percent'] * 100:.1f}%",
            f"{item_data['Sindh_Urban_Percent'] * 100:.1f}%",
            f"{item_data['Balochistan_Urban_Percent'] * 100:.1f}%",
            f"{item_data['Islamabad_Urban_Percent'] * 100:.1f}%"
        ],
        'Gap (Urban-Rural)': [
            f"{(item_data['KP_Urban_Percent'] - item_data['KP_Rural_Percent']) * 100:+.1f}%",
            f"{(item_data['Punjab_Urban_Percent'] - item_data['Punjab_Rural_Percent']) * 100:+.1f}%",
            f"{(item_data['Sindh_Urban_Percent'] - item_data['Sindh_Rural_Percent']) * 100:+.1f}%",
            f"{(item_data['Balochistan_Urban_Percent'] - item_data['Balochistan_Rural_Percent']) * 100:+.1f}%",
            f"{(item_data['Islamabad_Urban_Percent'] - item_data['Islamabad_Rural_Percent']) * 100:+.1f}%"
        ]
    }
    provincial_ur_df = pd.DataFrame(provincial_ur_data)
    st.dataframe(provincial_ur_df, use_container_width=True, hide_index=True)
    
    # ===================================================================================
    # EDUCATIONAL RESOURCES
    # ===================================================================================
    with st.expander("📚 **Complete Reference Guide: Key Concepts & Methodology**"):
        st.markdown("""
        ### 📖 Essential Terms & Definitions
        
        #### 🔹 **Quintile**
        - Divides population into 5 equal parts (each 20%)
        - Q1 = Bottom 20% (lowest income), Q5 = Top 20% (highest income)
        - Used globally to study income inequality
        - Example: If 100 people ranked by income, Q1 = person 1-20, Q5 = person 81-100
        
        #### 🔹 **Participation Rate**
        - Percentage of households that purchased an item
        - Different from expenditure amount
        - Formula: (Households buying item / Total households) × 100
        - Indicates market penetration: High (>50%) = mass market, Low (<20%) = niche
        
        #### 🔹 **Median vs Average**
        - **Median**: Middle value when data is sorted
        - **Average**: Sum divided by count
        - Why median is used: Not affected by extreme outliers
        - More representative for income and expenditure data
        
        #### 🔹 **Per Capita**
        - Latin for "per person" or "per head"
        - Total amount divided by number of people/households
        - Shows individual household share
        - Used for cross-population comparisons
        
        #### 🔹 **Market Size**
        - Total number of potential consumers
        - Formula: Total population × Participation rate
        - Measured in number of households
        - Essential for business planning and market analysis
        
        #### 🔹 **Inequality Ratio (Q5/Q1)**
        - Compares highest income to lowest income spending
        - 1.0 = perfect equality, Higher value = more inequality
        - <2x = Low inequality, 2-4x = Moderate, >4x = High
        - Indicates if item is necessity (low) or luxury (high)
        
        ---
        
        ### 🎓 Economic Classifications
        
        #### **Types of Consumer Goods**
        
        **1. Normal Goods**
        - Demand increases proportionally with income
        - Most consumer products fall in this category
        - Examples: Clothing, quality food, electronics
        - Positive income elasticity
        
        **2. Luxury Goods (Superior Goods)**
        - Demand increases more than proportionally with income
        - High income elasticity of demand
        - Primarily consumed by higher income groups
        - Examples: Premium brands, jewelry, luxury vehicles
        
        **3. Inferior Goods**
        - Demand decreases as income increases
        - Negative income elasticity
        - Lower income groups consume more, higher income groups switch to alternatives
        - Examples: Lower-grade staples, budget alternatives
        
        **4. Necessity Goods (Essential Goods)**
        - Consumed by all income groups regardless of income level
        - Low income elasticity
        - Essential for basic needs
        - Examples: Basic food items, utilities, essential medicines
        
        #### 📊 **Income Elasticity of Demand**
        - Measures responsiveness of demand to income changes
        - Formula: % change in quantity demanded / % change in income
        - Positive = Normal good, Negative = Inferior good
        - >1 = Luxury good, <1 = Necessity
        
        ---
        
        ### 🏙️ **Geographic & Demographic Factors**
        
        **Urban-Rural Consumption Differences:**
        
        **Urban Areas:**
        - Higher average household incomes
        - Better market access and product variety
        - Modern lifestyle and consumption patterns
        - Greater exposure to marketing and brands
        - Infrastructure for storage (refrigeration, etc.)
        
        **Rural Areas:**
        - Agriculture-based economy
        - Traditional consumption preferences
        - Local production and consumption
        - Limited market access in remote areas
        - Preference for natural/unprocessed items
        
        **Provincial Variations:**
        - Agricultural production differences (local availability)
        - Cultural and ethnic preferences
        - Climate and geographic factors
        - Income level disparities
        - Transportation and market access
        
        ---
        
        ### 🔬 Analytical Framework
        
        #### **Step 1: Assess Market Penetration**
        - >50% participation = Mass market item (necessity)
        - 20-50% participation = Regular consumer good
        - <20% participation = Niche market (luxury/specialty)
        
        #### **Step 2: Income Group Analysis**
        - Compare Q1 vs Q5 participation rates
        - Similar rates (difference <10%) = Necessity
        - Q5 significantly higher (>20%) = Luxury/Superior good
        - Q1 higher = Inferior good
        
        #### **Step 3: Inequality Assessment**
        - Calculate Q5/Q1 expenditure ratio
        - <2x = Equitable consumption pattern
        - 2-4x = Moderate inequality
        - >4x = High inequality (luxury characteristic)
        
        #### **Step 4: Geographic Pattern Analysis**
        - Large provincial variations = Cultural/regional factors
        - Consistent urban > rural = Modern/processed product
        - Rural > urban = Traditional/agricultural product
        
        #### **Step 5: Market Size Estimation**
        - Multiply participation rate by 38.34 million households
        - Segment by urban/rural (68% urban, 32% rural nationally)
        - Consider provincial distribution
        
        #### **Step 6: Product Classification**
        - Synthesize all factors
        - Classify as necessity, normal, inferior, or luxury good
        - Identify primary target market segments
        
        ---
        
        ### 💼 Business & Policy Applications
        
        **For Market Research:**
        - Identify and size target customer segments
        - Estimate total addressable market (TAM)
        - Understand price sensitivity across segments
        - Develop distribution and channel strategies
        
        **For Pricing Strategy:**
        - High inequality items = Premium pricing opportunities in urban/affluent segments
        - Low inequality items = Competitive, volume-based pricing
        - Consider provincial cost-of-living variations
        - Segment pricing by urban/rural markets
        
        **For Distribution Planning:**
        - High urban participation = Focus on city retail networks
        - High rural participation = Develop rural distribution channels
        - Provincial variations = Customize regional strategies
        - Consider infrastructure and logistics requirements
        
        **For Policy Analysis:**
        - High inequality items = Potential subsidy targets
        - Low participation in necessities = Access improvement needed
        - Urban-rural gaps = Infrastructure development priorities
        - Provincial disparities = Regional development focus areas
        
        ---
        
        ### 📊 Data Methodology
        
        **Data Source:**
        - Pakistan Household Integrated Economic Survey (HIES)
        - Nationally representative sample
        - Census 2023 household count: 38,340,566
        
        **What This Data Represents:**
        ✅ Median (middle value) household expenditure
        ✅ Household-level consumption (not individual)
        ✅ Participation rates (percentage of households consuming)
        ✅ Geographic breakdown (provincial and urban/rural)
        ✅ Income quintile stratification
        
        **Data Limitations:**
        ❌ Does not show quantity/volume purchased
        ❌ Does not capture quality or brand differences
        ❌ No information on purchase frequency
        ❌ Seasonal variations not reflected
        ❌ Individual-level consumption not available
        
        **Why Median is Used:**
        - Robust to extreme values and outliers
        - More representative for skewed income distributions
        - Better for inequality analysis
        - Standard practice in economic research
        
        ---
        
        ### 🎯 Use Cases & Applications
        
        **Academic Research:**
        - Income inequality studies
        - Consumer behavior analysis
        - Economic development research
        - Regional economics
        - Poverty and welfare analysis
        
        **Business Planning:**
        - Market opportunity assessment
        - Product positioning strategy
        - Pricing and promotion planning
        - Distribution channel design
        - Competitive analysis
        
        **Policy Development:**
        - Poverty alleviation programs
        - Subsidy targeting
        - Regional development planning
        - Food security assessment
        - Consumer protection policies
        
        **Investment Analysis:**
        - Sector opportunity evaluation
        - Market sizing for investors
        - Consumer trend analysis
        - Regional investment potential
        - Risk assessment
        
        ---
        
        ### 📝 Recommended Research Questions
        
        - Which products show highest income inequality?
        - How do urban-rural consumption gaps vary by province?
        - What items exhibit inferior good characteristics?
        - Which provinces show unique consumption patterns?
        - What is the market potential for specific product categories?
        - How do necessity vs luxury classifications vary geographically?
        
        """)
    
    # ===================================================================================
    # FOOTER
    # ===================================================================================
    st.markdown("---")
    st.info("""
    **📊 About This Data:**
    
    **Source**: Pakistan Household Integrated Economic Survey (HIES) - Gallup Pakistan
    - **Coverage**: All provinces with complete urban-rural breakdown
    - **Metric**: Median daily per capita household expenditure
    - **Total Items**: 285 consumption items tracked
    
    **Applications:**
    - Market research and business planning
    - Economic and policy analysis
    - Academic research
    - Investment opportunity assessment
    - Consumer behavior studies
    - Regional development planning
    """)
    
    st.markdown("---")
    
    # Footer with Gallup branding
    st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 1.5rem; background: #f8fafc; border-radius: 10px;'>
        <p style='font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;'>📊 Pakistan Household Consumption Analysis Dashboard</p>
        <p style='margin-bottom: 0.4rem;'><strong>Powered by Gallup Pakistan</strong> | Comprehensive Provincial & Income Analysis</p>
        <p style='font-size: 0.9rem; color: #94a3b8;'>
            💡 <strong>Analysis Tip:</strong> Compare similar items (Beef vs Chicken, Rice vs Wheat) to understand substitution patterns and income effects
        </p>
        <p style='font-size: 0.8rem; color: #94a3b8; margin-top: 1rem;'>
            © Gallup Pakistan | www.gallup.com.pk
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()