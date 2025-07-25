import streamlit as st
import pandas as pd
import plotly.express as px

df_stamps = pd.read_csv("stamps_com.csv")
df_transport = pd.read_csv("transport_com.csv")
df_ipass = pd.read_csv("ipass_com.csv")

st.title("Telangana Growth Dashboard")

st.markdown("""
## 📊 Growth & Investment Dashboard Summary

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

tab1, tab2, tab3 = st.tabs(["🏢 Stamps Department", "🚗 Transport Department", "🏭 TS-iPASS Investments"])

with tab1:
    st.header("Stamps Department Analysis")
    #Plot-1
    st.subheader("District-wise % Growth in Document Registration Revenue (2019–2022)")
    df_rev = df_stamps.groupby('district')['documents_registered_rev'].sum().sort_values(ascending=False).reset_index()
    growth = (
    df_stamps[df_stamps['fiscal_year'] == 2022].groupby('district')['documents_registered_rev'].sum()/
    df_stamps[df_stamps['fiscal_year'] == 2019].groupby('district')['documents_registered_rev'].sum()- 1) * 100
    growth_df = growth.reset_index()
    growth_df.columns = ['district', 'growth_pct']
    growth_df = growth_df.sort_values('growth_pct', ascending=False)
    fig1 = px.bar(growth_df, x='district', y='growth_pct', color='district', barmode='group',title="District-wise % Growth")
    fig1.update_layout(bargap=0)
    st.plotly_chart(fig1)
    #Plot-2
    st.subheader("Top 10 Districts where Stamp Revenue > Document Revenue in FY22")
    stamp_df_2022 = df_stamps[df_stamps["fiscal_year"] == 2022].copy()
    stamp_df_2022 = stamp_df_2022[stamp_df_2022["estamps_challans_rev"] > stamp_df_2022["documents_registered_rev"]].copy()
    stamp_df_2022["revenue_diff"] = (stamp_df_2022["estamps_challans_rev"] - stamp_df_2022["documents_registered_rev"])
    district_diff = (stamp_df_2022.groupby("district")["revenue_diff"].sum().sort_values(ascending=False))
    top_10_districts = district_diff.head(10).reset_index()
    fig = px.bar(
    top_10_districts,
    x='district',
    y='revenue_diff',
    color='district',  # Automatically assigns unique colors
    title='Top 10 Districts where Stamp Revenue > Document Revenue in FY22',
    labels={'district': 'District', 'revenue_diff': 'Revenue Difference (₹ Cr)'})
    st.plotly_chart(fig)
    # Table and Insights
    st.subheader("How Effective was the implementation of estamp registration instead of document registration ? ")
    before_df=df_stamps[df_stamps['fiscal_year']==2019]
    after_df=df_stamps[df_stamps['fiscal_year']==2022]
    before_grouped=before_df.groupby('district')[['documents_registered_cnt','estamps_challans_cnt']].sum()
    after_grouped=after_df.groupby('district')[['documents_registered_cnt','estamps_challans_cnt']].sum()
    comparison=after_grouped-before_grouped
    comparison['estamp_change_percent'] = (comparison['estamps_challans_cnt'] / before_grouped['estamps_challans_cnt']) * 100
    comparison['document_change_percent'] = (comparison['documents_registered_cnt'] / before_grouped['documents_registered_cnt']) * 100
    st.markdown("### 📊 Investment Summary Table")
    st.dataframe(comparison)
    st.markdown("### 🔍 Key Insights from Investment Summary")
    st.markdown("""
      Yes, there is a clear alteration in the pattern of e-Stamp challan and document registration counts after the implementation of the e-Stamp system.

      For example:
                
      Hanumakonda saw a 52,167 increase in e-Stamp challans while document registrations fell by over 12,000 (−20.45%).
                
      Jagtial shows a 30% drop in document registrations, but a +20,000 rise in e-Stamps.
                
      In contrast, Hyderabad is the only major district where both document registrations and e-Stamp challans increased, showing positive alignment and smoother transition.

      """)

    # Plot-3
    st.subheader("Stamp registration revenue generation during the FY 21-22")
    stamp_df_fy2021= df_stamps[df_stamps['fiscal_year']==2021]
    revenue_fy2021=stamp_df_fy2021.groupby('district')['estamps_challans_rev'].sum()
    revenue_fy2021 = revenue_fy2021.reset_index()
    revenue_fy2021['revenue_segment'] = pd.qcut(
        revenue_fy2021['estamps_challans_rev'], 
        q=3, 
        labels=['Low', 'Medium', 'High']
    )
    segment_colors = {
    'Low': '#D62728',     # dark red
    'Medium': '#FF7F0E',  # orange
    'High': '#2CA02C'  }   # dark green

# Add color column
    revenue_fy2021['color'] = revenue_fy2021['revenue_segment'].map(segment_colors)
    fig = px.bar(
    revenue_fy2021,
    x='district',
    y='estamps_challans_rev',
    color='revenue_segment',
    color_discrete_map=segment_colors,
    labels={
        'district': 'District',
        'estamps_challans_rev': 'Total Revenue (₹ Cr)',
        'revenue_segment': 'Revenue Segment'
    },
    title='District Revenue Segments (FY 2021)'
    )
    st.plotly_chart(fig)

with tab2:
    st.header('Transport Department Analysis')
    # Plot - 1
    st.subheader("Monthly Transport Sales by District")
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
    fig = px.line(
        pivot_sales,
        x=pivot_sales.index,
        y=selected_district,
        title=f"Monthly Transport Sales in {selected_district}",
        labels={"x": "Month", "y": "Total Sales"}
    )
    st.plotly_chart(fig,use_container_width=True)
    ## Plot-2
    st.subheader("Monthly Transport Sales by District")
    transport_2022=df_transport[df_transport['fiscal_year']==2022].copy()
    transport_2022_vehicleClass=transport_2022.groupby('district')[['vehicleClass_MotorCycle','vehicleClass_MotorCar','vehicleClass_AutoRickshaw','vehicleClass_Agriculture']].sum().copy()
    districts = transport_2022_vehicleClass.index.tolist()
    selected_district = st.selectbox("Select a district", districts)
    selected_data = transport_2022_vehicleClass.loc[selected_district]

    # Create a bar chart using Plotly
    fig = px.bar(
        x=selected_data.index,
        y=selected_data.values,
        labels={'x': 'Vehicle Class', 'y': 'Number of Vehicles Sold'},
        text=selected_data.values,
        title=f"Vehicle Class Distribution in {selected_district} (2022)",
    )
    fig.update_traces(marker_color='red', width=0.5)
    fig.update_layout(yaxis_title="Vehicles Sold", xaxis_title="Vehicle Class")

    # Display chart
    st.plotly_chart(fig)

    # Show table below if needed
    st.dataframe(selected_data.reset_index(name="Vehicles Sold"))
    st.markdown("### 🔍 Key Insights from Monthly Transport Vehicles Sold")
    st.markdown("""
                --> Motorcycles are most prefered in alomost all districts

    --> Second most prefered can be motorcar or agriculuture depends on preference as for some districts which rely on agriculuture like Jangoan and Jayashankar Bhupalpally and for almost remaining districts motorcar is second most prefered
                """)

    # Plot - 3 
    st.subheader('Top and Bottom 3 Districts by Vehicle Sales Growth (FY22 vs FY21)')
    transport_2022=df_transport[df_transport['fiscal_year']==2022].copy()
    transport_2022_fuel=transport_2022.groupby('district')[['fuel_type_petrol','fuel_type_diesel','fuel_type_electric']].sum()
    transport_2021=df_transport[df_transport['fiscal_year']==2021]
    transport_2021_fuel=transport_2021.groupby('district')[['fuel_type_petrol','fuel_type_diesel','fuel_type_electric']].sum()
    transport_2022_fuel['petrol_growth'] = ((transport_2022_fuel['fuel_type_petrol'] - transport_2021_fuel['fuel_type_petrol']) / transport_2021_fuel['fuel_type_petrol']) * 100
    transport_2022_fuel['diesel_growth'] = ((transport_2022_fuel['fuel_type_diesel'] - transport_2021_fuel['fuel_type_diesel']) / transport_2021_fuel['fuel_type_diesel']) * 100
    transport_2022_fuel['electric_growth'] =((transport_2022_fuel['fuel_type_electric'] - transport_2021_fuel['fuel_type_electric']) / transport_2021_fuel['fuel_type_electric']) * 100
    transport_2022_fuel['total_growth'] = transport_2022_fuel[['petrol_growth', 'diesel_growth', 'electric_growth']].mean(axis=1)
    top3 = transport_2022_fuel.sort_values(by='total_growth', ascending=False).head(5).reset_index()
    bottom3 = transport_2022_fuel.sort_values(by='total_growth', ascending=True).head(5).reset_index()
    top_bottom = pd.concat([top3, bottom3])
    print("Top 5 districts by vehicle sales growth:")
    print(top3[['district', 'total_growth']])

    print("\nBottom 5 districts by vehicle sales growth:")
    print(bottom3[['district', 'total_growth']])
    op_bottom = pd.concat([top3, bottom3])

    # Sort by growth for cleaner layout
    top_bottom = top_bottom.sort_values('total_growth')

    # Plotly bar chart
    fig = px.bar(
        top_bottom,
        x='total_growth',
        y='district',
        color='total_growth',
        color_continuous_scale='RdBu_r',  # Red to Blue reversed (matches coolwarm)
        orientation='h',
        title='Top and Bottom 3 Districts by Vehicle Sales Growth (FY22 vs FY21)',
        labels={'total_growth': 'Growth %', 'district': 'District'}
    )
    st.plotly_chart(fig)

with tab3:
    st.header("TS-iPass Investments Analysis")

    # Year dropdown
    years = df_ipass['fiscal_year'].unique().tolist()
    years.sort(reverse=True)
    selected_year = st.selectbox("Select Fiscal Year", years)

    # Dynamic subheader
    st.subheader(f'Top 5 sectors with the most significant investments in FY{selected_year}')

    # Filter and group
    ipass_selected = df_ipass[df_ipass['fiscal_year'] == selected_year]
    ipass_top_sectors = (
        ipass_selected
        .groupby('sector')['investment in cr']
        .sum()
        .sort_values(ascending=False)
        .head()
        .reset_index()
    )

    # Bar chart
    fig = px.bar(
        ipass_top_sectors,
        x='sector',
        y='investment in cr',
        text='investment in cr',
        color='sector',
        title=f'Top 5 Sectors with Highest Investment in FY {selected_year}',
        labels={'sector': 'Sector', 'investment in cr': 'Investment (₹ Cr)'}
    )
    fig.update_traces(textposition='outside')

    fig.update_layout(
    width=1000,  # Try increasing to 1000 or more if needed
    height=500,  # Increase height for taller bars
    margin=dict(l=40, r=40, t=80, b=80)
)

    # Display chart
    st.plotly_chart(fig)

    ## Plot-2 
    st.subheader("Top Sectors by Total Investment (FY2019–2022)")
    ipass_invest=df_ipass.groupby('sector')['investment in cr'].sum().sort_values(ascending=False).reset_index()
    fig=px.bar(
        ipass_invest,
        x='sector',
        y='investment in cr',
        text='investment in cr',
        color='investment in cr', 
        color_continuous_scale='viridis',
        title='Sectors by Total Investment (FY2019-2022)',
        labels={'investment in cr': 'Investment (₹ Cr)', 'district': 'District'}
        )

    fig.update_layout(
    xaxis_tickangle=60,
    height=800,
    coloraxis_showscale=False
    )

    fig.update_traces(texttemplate='%{text:.2f} Cr', textposition='outside')
    st.plotly_chart(fig)

    # Plot-3
    st.subheader('Top Districts by Total Investment (FY2019–2022)')
    ipass_complete_investment=df_ipass.groupby('district')['investment in cr'].sum().reset_index().sort_values(by='investment in cr',ascending=False)
    fig = px.bar(
    ipass_complete_investment,
    x='district',
    y='investment in cr',
    text='investment in cr',
    color='investment in cr',  # color by value instead of sector
    color_continuous_scale='viridis',
    title='Districts by Total Investment (FY2019–2022)',
    labels={'investment in cr': 'Investment (₹ Cr)', 'district': 'District'}
)

    fig.update_layout(
        xaxis_tickangle=60,
        width=1000,
        height=600,
        coloraxis_showscale=False
    )

    fig.update_traces(texttemplate='%{text:.2f} Cr', textposition='outside')

    st.plotly_chart(fig)

    st.markdown("""
        ### 🧠 Insight: District-Wise Investment Trends

  The bar chart shows that certain districts (like **Rangareddy**,**Sangareddy** or **Medchal**) have attracted disproportionately higher investments.  

This could be due to:

- Proximity to urban hubs and developed infrastructure
- Availability of tech parks, logistics centers, and SEZs
- Government focus on developing Tier-1 and Tier-2 districts under TS-iPASS

This concentration may suggest the need for further policy support in low-investment districts.


""")
    
    ## Plot-4
    years=df_ipass['fiscal_year'].unique().tolist()
    years.sort(reverse=True)
    selected_year=st.selectbox("Enter the Year ",years)
    st.subheader(f'Sectors with Highest Investment in FY {selected_year}')
    ipass_selected=df_ipass[df_ipass['fiscal_year']==selected_year]
    sector_district=ipass_selected.groupby(['sector','district'])['investment in cr'].sum().reset_index()
    sector_growth=sector_district.groupby('sector')['district'].nunique().reset_index()
    sector_growth.columns = ['sector', 'num_districts_with_investment']
    sector_growth = sector_growth.sort_values(by='num_districts_with_investment', ascending=False)
    fig=px.bar(
    sector_growth,
    x='sector',
    y='num_districts_with_investment',
    text='num_districts_with_investment',
    color='sector',
    title=f'Sectors with Highest Investment in FY {selected_year}',
    labels={'sector': 'Sector', 'num_districts_with_investment': 'No.of districts withInvestment '}
    )
    fig.update_layout(
        xaxis_tickangle=90,
        showlegend=False,
        height=800
    )

    st.plotly_chart(fig)

    ## Plot-5

    st.subheader('Monthly Investment Trends by Sector')
    ipass_monthly_investment=df_ipass.groupby(['sector','Mmm'])['investment in cr'].sum().reset_index()
    import pandas as pd

    # Define the correct calendar month order
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Convert your 'Mmm' column to an ordered categorical type
    ipass_monthly_investment['Mmm'] = pd.Categorical(ipass_monthly_investment['Mmm'], categories=month_order, ordered=True)

    # Sort the DataFrame by month
    ipass_monthly_investment =ipass_monthly_investment.sort_values('Mmm')
    
    sectors=ipass_monthly_investment['sector'].unique().tolist()
    selected_sector=st.selectbox("Select a sector to view monthly trends",sectors)

    filtered_df=ipass_monthly_investment[ipass_monthly_investment['sector']==selected_sector]
    

    fig = px.line(
    filtered_df,
    x='Mmm',
    y='investment in cr',
    title='Monthly Investment Trends by Sector',
    markers=True  # optional: adds dots on each line
    )

    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Investment (in Cr)',
        width=1200,
        height=500,
        xaxis=dict(tickangle=-45),
        title_font_size=20,
        legend_title_text='Sector'
    )

    st.plotly_chart(fig)