import streamlit as st
import pandas as pd
import plotly.express as px

df_stamps = pd.read_csv("stamps_com.csv")
df_transport = pd.read_csv("transport_com.csv")
df_ipass = pd.read_csv("ipass_com.csv")

st.set_page_config(page_title="Telangana Growth Dashboard", layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem;
    }

    h1, h2, h3, h4 {
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
        overflow-wrap: break-word;
        word-break: break-word;
    }

    html, body, .main {
        overflow-x: hidden !important;
        overflow-y: auto !important;
    }

    .stTabs {
        margin-top: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4 = st.tabs(["Introduction","🏢 Stamps Department", "🚗 Transport Department", "🏭 TS-iPASS Investments"])
with tab1:
    st.markdown("""
    ## 📊 Telangana Growth & Investment Dashboard Summary

    This interactive dashboard presents an analysis of growth and investment patterns facilitated by stamps department,transport department and IPass Investment data in various sectors and districts across fiscal years.

    **Key Features:**
    - 🔍 **Year-wise Sector Analysis** – See which sectors attracted the most investment each year.
    - 🗺️ **District-wise Distribution** – Understand how new estamp registration implementation is going down and how vehicles are sold at district and analysis with time and how investments are spread across districts.
    - 📈 **Monthly Trend Analysis** – Explore how investments vary month-by-month for each sector.
    - 🎯 **Interactive Filtering** – Use dropdowns to explore specific years, sectors, or districts.

    **Purpose:**  
    To provide data-driven insights for policy makers, businesses, and researchers interested in industrial investment patterns in Telangana.

    ---
    """)


    st.subheader("Raw Data Preview (optional)")
    data_tab = st.selectbox("Select a dataset to preview", ["Stamps", "Transport", "Ipass"])

    if data_tab == "Stamps":
        st.write(df_stamps.head())
    elif data_tab == "Transport":
        st.write(df_transport.head())
    elif data_tab == "Ipass":
        st.write(df_ipass.head())
with tab2:
    st.markdown("<h2 style='text-align: center; font-size:24px;'>Stamps Department Analysis</h2>", unsafe_allow_html=True)
    #Plot-1
    
    df_rev = df_stamps.groupby('district')['documents_registered_rev'].sum().sort_values(ascending=False).reset_index()
    growth = (
    df_stamps[df_stamps['fiscal_year'] == 2022].groupby('district')['documents_registered_rev'].sum()/
    df_stamps[df_stamps['fiscal_year'] == 2019].groupby('district')['documents_registered_rev'].sum()- 1) * 100
    growth_df = growth.reset_index()
    growth_df.columns = ['district', 'growth_pct']
    growth_df = growth_df.sort_values('growth_pct', ascending=False)
    fig1 = px.bar(growth_df, x='district', y='growth_pct', color='district', barmode='group',title="District-wise % Growth in Document Registration Revenue (2019–2022)")
    fig1.update_layout(bargap=0,height=400)
    

    #Plot-2

    stamp_df_2022 = df_stamps[df_stamps["fiscal_year"] == 2022].copy()
    stamp_df_2022 = stamp_df_2022[stamp_df_2022["estamps_challans_rev"] > stamp_df_2022["documents_registered_rev"]].copy()
    stamp_df_2022["revenue_diff"] = (stamp_df_2022["estamps_challans_rev"] - stamp_df_2022["documents_registered_rev"])
    district_diff = (stamp_df_2022.groupby("district")["revenue_diff"].sum().sort_values(ascending=False))
    top_10_districts = district_diff.head(10).reset_index()
    fig2 = px.bar(
    top_10_districts,
    x='district',
    y='revenue_diff',
    color='district',  # Automatically assigns unique colors
    title='Top 10 Districts where Stamp Revenue > Document Revenue in FY22',
    labels={'district': 'District', 'revenue_diff': 'Revenue Difference (₹ Cr)'})
    fig2.update_layout(title_x=0.2,height=400)


    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

        
        
    # Plot-3
    years = df_ipass['fiscal_year'].unique().tolist()
    years.sort(reverse=True)

    selected_year = st.selectbox("Enter the Year", years)
    st.markdown(f"<h4 style='font-size:20px;'>Stamp Registration Revenue during FY {selected_year}</h4>", unsafe_allow_html=True)


    # Filter for selected year
    stamp_df_fy = df_stamps[df_stamps['fiscal_year'] == selected_year]
    revenue_fy = stamp_df_fy.groupby('district')['estamps_challans_rev'].sum().reset_index()

    # Handle case where all revenue values are the same
    if revenue_fy['estamps_challans_rev'].nunique() > 1:
        # Safe qcut with duplicates='drop'
        revenue_fy['revenue_segment'] = pd.qcut(
            revenue_fy['estamps_challans_rev'],
            q=3,
            labels=['Low', 'Medium', 'High'],
            duplicates='drop'
        )
    else:
        revenue_fy['revenue_segment'] = 'Low'

    # Define colors
    segment_colors = {
        'Low': '#D62728',     # dark red
        'Medium': '#FF7F0E',  # orange
        'High': '#2CA02C'     # dark green
    }

    # Add color column
    revenue_fy['color'] = revenue_fy['revenue_segment'].map(segment_colors)

    # Plotly Bar Chart
    fig3 = px.bar(
        revenue_fy,
        x='district',
        y='estamps_challans_rev',
        color='revenue_segment',
        color_discrete_map=segment_colors,
        labels={
            'district': 'District',
            'estamps_challans_rev': 'Total Revenue (₹ Cr)',
            'revenue_segment': 'Revenue Segment'
        },
        title=f'District Revenue Segments FY {selected_year}'
    )

    # Center the title
    fig3.update_layout(title_x=0.25,height=400)


    col_center = st.columns([1, 2, 1])  # middle column is wider

    with col_center[1]:
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.markdown("<h2 style='text-align: center; font-size:24px;'>Transport Department Analysis</h2>", unsafe_allow_html=True)

    # Plot - 1
    
    df_transport['fiscal_year']=df_transport['fiscal_year'].astype('object')
    df_transport['total_sales'] = df_transport.select_dtypes(include='number').sum(axis=1)
    transport_season=(df_transport.groupby(['Mmm','district'])['total_sales'].sum().reset_index())
    pivot_sales = transport_season.pivot(index='Mmm', columns='district', values='total_sales')
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot_sales = pivot_sales.reindex(month_order)

    district_list = pivot_sales.columns.tolist()
    selected_district = st.selectbox("Select a District", district_list)

    # --- PLOT FOR SELECTED DISTRICT ---
    fig4= px.line(
        pivot_sales,
        x=pivot_sales.index,
        y=selected_district,
        title=f"Monthly Transport Sales in {selected_district}",
        labels={"x": "Month", "y": "Total Sales"}
    )
    fig4.update_layout(title_x=0.25,height=400)

    ## Plot-2

    
    transport_2022=df_transport[df_transport['fiscal_year']==2022].copy()
    transport_2022_vehicleClass=transport_2022.groupby('district')[['vehicleClass_MotorCycle','vehicleClass_MotorCar','vehicleClass_AutoRickshaw','vehicleClass_Agriculture']].sum().copy()
    districts = transport_2022_vehicleClass.index.tolist()
    selected_data = transport_2022_vehicleClass.loc[selected_district]

    # Create a bar chart using Plotly
    fig5 = px.bar(
        x=selected_data.index,
        y=selected_data.values,
        labels={'x': 'Vehicle Class', 'y': 'Number of Vehicles Sold'},
        text=selected_data.values,
        title=f"Vehicle Class Distribution in {selected_district} (2022)",
    )
    fig5.update_traces(marker_color='red', width=0.5)
    fig5.update_layout(yaxis_title="Vehicles Sold", xaxis_title="Vehicle Class")
    fig5.update_layout(title_x=0.25,height=400)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig4, use_container_width=True)
    with col2:
        st.plotly_chart(fig5, use_container_width=True)

    # Plot - 3: Vehicle Sales Growth

    # --- Data Processing ---
    transport_2022 = df_transport[df_transport['fiscal_year'] == 2022].copy()
    transport_2021 = df_transport[df_transport['fiscal_year'] == 2021]

    transport_2022_fuel = transport_2022.groupby('district')[['fuel_type_petrol','fuel_type_diesel','fuel_type_electric']].sum()
    transport_2021_fuel = transport_2021.groupby('district')[['fuel_type_petrol','fuel_type_diesel','fuel_type_electric']].sum()

    transport_2022_fuel['petrol_growth'] = ((transport_2022_fuel['fuel_type_petrol'] - transport_2021_fuel['fuel_type_petrol']) / transport_2021_fuel['fuel_type_petrol']) * 100
    transport_2022_fuel['diesel_growth'] = ((transport_2022_fuel['fuel_type_diesel'] - transport_2021_fuel['fuel_type_diesel']) / transport_2021_fuel['fuel_type_diesel']) * 100
    transport_2022_fuel['electric_growth'] = ((transport_2022_fuel['fuel_type_electric'] - transport_2021_fuel['fuel_type_electric']) / transport_2021_fuel['fuel_type_electric']) * 100

    transport_2022_fuel['total_growth'] = transport_2022_fuel[['petrol_growth', 'diesel_growth', 'electric_growth']].mean(axis=1)

    top3 = transport_2022_fuel.sort_values(by='total_growth', ascending=False).head(5).reset_index()
    bottom3 = transport_2022_fuel.sort_values(by='total_growth', ascending=True).head(5).reset_index()

    top_bottom = pd.concat([top3, bottom3])
    top_bottom = top_bottom.sort_values('total_growth')

    # --- Plotly Bar Chart ---
    fig6 = px.bar(
        top_bottom,
        x='total_growth',
        y='district',
        color='total_growth',
        color_continuous_scale='RdBu_r',
        orientation='h',
        title='Top and Bottom 5 Districts by Vehicle Sales Growth (FY22 vs FY21)',
        labels={'total_growth': 'Growth %', 'district': 'District'}
    )
    fig6.update_layout(title_x=0.3, height=400)

    # --- Streamlit Layout ---
    col3, col4 = st.columns([1, 1.2])  # Wider space for plot

    with col3:
        st.markdown("### 🔍 Key Insights from Monthly Transport Vehicles Sold")
        st.markdown("""
        - Motorcycles are the most preferred in almost all districts  
        - Second preference varies:
            - In agriculture-based districts (e.g., Jangaon, Jayashankar Bhupalpally): Agriculture vehicles are second  
            - In urban districts: Motorcars take second place
        """)

    with col4:
        st.plotly_chart(fig6, use_container_width=True)


with tab4:
    # ---------------------- PAGE TITLE ----------------------
    st.markdown("<h2 style='text-align: center;'>TS-iPass Investments Analysis</h2>", unsafe_allow_html=True)

    # ---------------------- ROW 1: 3 Plots ----------------------
    row1_col1, row1_col2, row1_col3 = st.columns(3)

    # Select fiscal year (shared)
    fiscal_years = sorted(df_ipass['fiscal_year'].unique(), reverse=True)
    selected_year = row1_col1.selectbox("Select Fiscal Year", fiscal_years, key='year1')

    ## --- Plot 1: Top 5 Sectors ---
    ipass_selected = df_ipass[df_ipass['fiscal_year'] == selected_year]
    ipass_top_sectors = ipass_selected.groupby('sector')['investment in cr'].sum().nlargest(5).reset_index()

    fig7 = px.bar(ipass_top_sectors, x='sector', y='investment in cr', text='investment in cr', color='sector',
                  title=f'Top 5 Sectors - FY {selected_year}')
    fig7.update_traces(textposition='outside')
    fig7.update_layout(height=400, title_x=0.3, showlegend=False)
    row1_col1.plotly_chart(fig7, use_container_width=True)

    ## --- Plot 2: Sector Spread Across Districts ---
    sector_district = ipass_selected.groupby(['sector', 'district'])['investment in cr'].sum().reset_index()
    sector_growth = sector_district.groupby('sector')['district'].nunique().reset_index()
    sector_growth.columns = ['sector', 'num_districts_with_investment']
    sector_growth = sector_growth.sort_values(by='num_districts_with_investment', ascending=False)

    fig10 = px.bar(sector_growth, x='sector', y='num_districts_with_investment',
                   text='num_districts_with_investment', color='sector',
                   title=f'District Spread - FY {selected_year}')
    fig10.update_layout(height=400, xaxis_tickangle=45, title_x=0.3, showlegend=False)
    row1_col2.plotly_chart(fig10, use_container_width=True)

    ## --- Plot 3: Monthly Investment Trend by Sector ---
    ipass_monthly_investment = df_ipass.groupby(['sector', 'Mmm'])['investment in cr'].sum().reset_index()
    ipass_monthly_investment['Mmm'] = pd.Categorical(ipass_monthly_investment['Mmm'],
                                                     categories=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                                                     ordered=True)
    ipass_monthly_investment = ipass_monthly_investment.sort_values('Mmm')
    sector_list = ipass_monthly_investment['sector'].unique().tolist()
    selected_sector = row1_col3.selectbox("Select Sector", sector_list, key='sector1')
    monthly_filtered = ipass_monthly_investment[ipass_monthly_investment['sector'] == selected_sector]

    fig11 = px.line(monthly_filtered, x='Mmm', y='investment in cr',
                    title=f'Monthly Trend - {selected_sector}', markers=True)
    fig11.update_layout(height=400, xaxis_title='Month', yaxis_title='Investment (₹ Cr)',
                        title_x=0.3, xaxis_tickangle=-45)
    row1_col3.plotly_chart(fig11, use_container_width=True)

    # ---------------------- ROW 2: Long-Term View ----------------------
    st.markdown("### 📊 Long-Term Investment Trends (FY2019–2022)")
    row2_col1, row2_col2 = st.columns(2)

    ## --- Plot 4: Top Sectors by Total Investment ---
    ipass_invest = df_ipass.groupby('sector')['investment in cr'].sum().sort_values(ascending=False).reset_index()

    fig8 = px.bar(ipass_invest, x='sector', y='investment in cr', text='investment in cr',
                  color='investment in cr', color_continuous_scale='viridis',
                  title='Sectors by Total Investment')
    fig8.update_traces(texttemplate='%{text:.2f} Cr', textposition='outside')
    fig8.update_layout(xaxis_tickangle=60, height=500, coloraxis_showscale=False, title_x=0.3)
    row2_col1.plotly_chart(fig8, use_container_width=True)

    ## --- Plot 5: Districts by Total Investment ---
    ipass_districts = df_ipass.groupby('district')['investment in cr'].sum().sort_values(ascending=False).reset_index()

    fig9 = px.bar(ipass_districts, x='district', y='investment in cr', text='investment in cr',
                  color='investment in cr', color_continuous_scale='viridis',
                  title='Districts by Total Investment')
    fig9.update_traces(texttemplate='%{text:.2f} Cr', textposition='outside')
    fig9.update_layout(xaxis_tickangle=60, height=500, coloraxis_showscale=False, title_x=0.3)
    row2_col2.plotly_chart(fig9, use_container_width=True)
