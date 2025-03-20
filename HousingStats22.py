# Libraries

import pandas as pd
import plotly.express as px
import streamlit as st
import openpyxl

# Streamlit set up
st.set_page_config(page_title="Housing statistics 2022", layout = "wide")

# Load data
df_wohnungen = pd.read_excel("data/Data_wohnungen.xlsx")

# Filter by Land and Bund and Stadtkreis/kreisfreie Stadt/Landkreis
df_wohnungen = df_wohnungen[(df_wohnungen["Regionalebene"] == "Land") | (df_wohnungen["Regionalebene"] == "Bund") | (df_wohnungen["Regionalebene"] == "Stadtkreis/kreisfreie Stadt/Landkreis")]

# Rename column
df_wohnungen = df_wohnungen.rename(columns = {
     "Name" : "Region"})



# Sidebar
st.sidebar.header("Housing statistics in Germany based on Zensus 2022")
st.sidebar.markdown("The _Zensus 2022_ provided a comprehensive snapshot of Germany's population, housing situation, and demographic characteristics and was last conducted on May 15, 2022 and published in 2024 by the Federal Statistical Office - Statistisches Bundesamt. It included a building and housing survey, combining register data with sample-based surveys to provide statistical data on dwellings and residential buildings in Germany. For the first time, information on energy sources used for heating was collected. The census results serve as a foundation for political, economic, and social planning processes at the federal, state, and municipal levels. The data used in this Streamlit App is openly accessible [here](https://www.zensus2022.de/DE/Aktuelles/Gebaeude_Wohnungen_VOE.html). Choose a regional level and region to explore housing statistics results, based on a selection of data from the Zensus 2022.")


# Filter data based on selected region level
region_level = ["Bund", "Land", "Stadtkreis/kreisfreie Stadt/Landkreis"]

# Translate region level
region_level_translations = {
    "Bund": "Federal",
    "Land": "State",
    "Stadtkreis/kreisfreie Stadt/Landkreis": "Urban district/independent city/rural district"}

selected_region_level = st.sidebar.selectbox(
    "Choose a region level:", 
    options=region_level, format_func=lambda x: f"{region_level_translations[x]} ({x})")

# Replace "Deutschland" with "Germany"
df_wohnungen["Region"] = df_wohnungen["Region"].replace("Deutschland", "Germany")

# First filter
if selected_region_level:
    df_1 = df_wohnungen[df_wohnungen["Regionalebene"] == selected_region_level]
else:
    df_1 = df_wohnungen


# Filter data based on selected region
region = sorted(df_1["Region"].unique())
selected_region = st.sidebar.selectbox(
    "Choose a region:", region)

# Second filter
if selected_region:
    df_2 = df_1[df_1["Region"] == selected_region]
else:
    df_2 = df_1 

# Set title
st.title(f"Housing statistics for {selected_region} (2022)")


###### CHARTS & METRICS ###### 

# Metrics

stats = df_wohnungen[["Region", "Regionalebene",
        "QMMIETE", "LEQ", "ETQ", "FLAECHE"]]
    
stats = stats[stats["Region"]== selected_region]

col1, col2, col3, col4 = st.columns(4)

col1.metric("∅ Net cold rent per square meter*", f"{stats['QMMIETE'].values[0]:.2f} €/m²")
col2.metric("Vacancy rate*", f"{stats['LEQ'].values[0]:.1f} %")
col3.metric("Ownership rate*", f"{stats['ETQ'].values[0]:.1f} %")
col4.metric("∅ Area per apartment*", f"{stats['FLAECHE'].values[0]:.1f} m²")


# Gebaeudeart

col1, spacer, col2 = st.columns([1, 0.2, 1]) 

with col1:

    # Subset
    gebaeudeArt = df_wohnungen[['Region', 'Regionalebene',
        'GEBAEUDEART_SYS_1', 'GEBAEUDEART_SYS_11', 'GEBAEUDEART_SYS_111',
        'GEBAEUDEART_SYS_112', 'GEBAEUDEART_SYS_12']]
    
    # Selection
    gebaeudeArt = gebaeudeArt[gebaeudeArt["Region"]== selected_region]

    # Rename columns
    gebaeudeArt = gebaeudeArt.rename(columns = {
            "GEBAEUDEART_SYS_1": "Apartments in buildings with living space", 
            "GEBAEUDEART_SYS_11": "Apartments in residential buildings", 
            "GEBAEUDEART_SYS_111": "Apartments in residential buildings (excluding halls of residence)",
            "GEBAEUDEART_SYS_112": "Apartments in halls of residence", 
            'GEBAEUDEART_SYS_12': "Apartments in other buildings with living space"})

    # Wide to long format
    gebaeudeArt_long = pd.melt(gebaeudeArt, id_vars=["Region"], 
                    value_vars=["Apartments in buildings with living space", "Apartments in residential buildings", 
                                "Apartments in residential buildings (excluding halls of residence)",
                                "Apartments in halls of residence", 
                                "Apartments in other buildings with living space"])

    color_map = {
    "Apartments in buildings with living space": "#a6cee3",
    "Apartments in residential buildings": "#1f78b4",
    "Apartments in residential buildings (excluding halls of residence)": "#b2df8a",
    "Apartments in halls of residence": "#33a02c",
    "Apartments in other buildings with living space": "#fb9a99"
    }

    # Plot
    fig = px.bar(gebaeudeArt_long, x="value", y="Region",
                color="variable", color_discrete_map=color_map,
                title="Number of apartments by building type",
                labels={"value": "Quantity", "variable": "Building type"},
                barmode="group",
                template = "seaborn",
                orientation="h",
                height= 500)

    fig.update_layout(
    xaxis_title="Quantity",
    legend_title="Building type",
    legend=dict(x=0.5, y=-0.3, xanchor="center", yanchor="top"))

    fig.update_traces(hovertemplate="<b>Building type:</b> %{fullData.name}<br><b>Quantity:</b> %{x}<extra></extra>")

    fig.update_yaxes(tickangle=-90)

    st.plotly_chart(fig, use_container_width=True)


# Eigentum

with col2:
    
    # Subset
    eigentum = df_wohnungen[['Region', 'Regionalebene',
        'EIGENTUM__1', 'EIGENTUM__2', 'EIGENTUM__3',
        'EIGENTUM__4', 'EIGENTUM__5', 'EIGENTUM__6', 'EIGENTUM__7', 'EIGENTUM__8']]
    
    # Selection
    eigentum = eigentum[eigentum["Region"]== selected_region]

    # Rename columns
    eigentum = eigentum.rename(columns={
        "EIGENTUM__1": "Community of apartment owners",
        "EIGENTUM__2": "Private individuals",
        "EIGENTUM__3": "Housing company",
        "EIGENTUM__4": "Municipality or municipal housing company",
        "EIGENTUM__5": "Private company",
        "EIGENTUM__6": "Other private-sector company",
        "EIGENTUM__7": "Federal or state",
        "EIGENTUM__8": "Non-profit organization"})

    # Wide to long format
    eigentum_long = pd.melt(eigentum, id_vars=["Region"], 
                    value_vars=list(eigentum.columns[2:]),
                    var_name= "Form of ownership",
                    value_name = "Quantity")

    # Total count
    total_count = eigentum_long["Quantity"].fillna(0).sum()

    # Calculate percentage
    eigentum_long["Percent"] = eigentum_long["Quantity"] / total_count * 100

    color_map = {
        "Community of apartment owners": "#a6cee3",
        "Private individuals": "#1f78b4",
        "Housing company": "#b2df8a",
        "Municipality or municipal housing company": "#33a02c",
        "Private company": "#fb9a99",
        "Other private-sector company": "#e31a1c",
        "Federal or state": "#fdbf6f",
        "Non-profit organization": "#ff7f00"}


    # Plot
    fig = px.pie(eigentum_long, names="Form of ownership", values="Percent",
                color="Form of ownership", color_discrete_map=color_map,
                title="Proportion of apartments (in buildings with living space)<br>by type of ownership",
                labels={"value": "Quantity", "variable": "Form of ownership"},
                template = "seaborn",
                hole=0.3,
                height= 400)

    fig.update_traces(
    textinfo="percent",
    insidetextorientation="radial",
    hovertemplate="<b>%{label}</b><br>Percent: %{percent}<extra></extra>")

    fig.update_layout(
    legend=dict(title=dict(text="Form of ownership"), orientation="h", yanchor="bottom", y=-0.8, xanchor="center", x=0.5),
    margin=dict(b=100),
    height=600)

    st.plotly_chart(fig, use_container_width=False)


# Heiztyp

with col1:

    # Subset
    heizTyp = df_wohnungen[['Region', 'Regionalebene','HEIZTYP__1', 'HEIZTYP__2', 
                            'HEIZTYP__3', 'HEIZTYP__4', 'HEIZTYP__5', 'HEIZTYP__6']]
    
    # Selection
    heizTyp = heizTyp[heizTyp["Region"]== selected_region]

    # Rename columns
    heizTyp = heizTyp.rename(columns={
        "HEIZTYP__1": "District heating",
        "HEIZTYP__2": "Single-storey heating system",
        "HEIZTYP__3": "Block heating",
        "HEIZTYP__4": "Central heating",
        "HEIZTYP__5": "Single or multi-room stoves (also night storage heaters)",
        "HEIZTYP__6": "No heating in the building or in the apartments"})

    # Wide to long format
    heizTyp_long = pd.melt(heizTyp, id_vars=["Region"], 
                    value_vars=list(heizTyp.columns[2:]))


    color_map = {
    "District heating": "#a6cee3",
    "Single-storey heating system": "#1f78b4",
    "Block heating": "#b2df8a",
    "Central heating": "#33a02c",
    "Single or multi-room stoves (also night storage heaters)": "#fb9a99",
    "No heating in the building or in the apartments": "#e31a1c"}


    # Plot
    fig = px.bar(heizTyp_long, x="value", y="Region",
                color="variable", color_discrete_map=color_map,
                title="Number of apartments (in buildings with living space)<br>by heating type",
                labels={"value": "Quantity", "variable": "Heating type"},
                barmode="group",
                template = "seaborn",
                orientation="h",
                height= 600)

    fig.update_layout(
    xaxis_title="Quantity",
    legend_title="Heating type",
    legend=dict(x=0.5, y=-0.2, xanchor="center", yanchor="top"))

    fig.update_traces(hovertemplate="<b>Heating type:</b> %{fullData.name}<br><b>Quantity:</b> %{x}<extra></extra>")

    fig.update_yaxes(tickangle=-90)
    st.plotly_chart(fig, use_container_width=True)


# Energieträger

with col2:

    st.write(' ')
    st.write(' ')
    # Subset
    energie = df_wohnungen[['Region', 'Regionalebene',
        'ENERGIETRAEGER__1', 'ENERGIETRAEGER__2', 'ENERGIETRAEGER__3',
       'ENERGIETRAEGER__4', 'ENERGIETRAEGER__5', 'ENERGIETRAEGER__6',
       'ENERGIETRAEGER__7', 'NERGIETRAEGER__8', 'ENERGIETRAEGER__9']]
    
    # Selection
    energie = energie[energie["Region"]== selected_region]

    # Rename columns
    energie = energie.rename(columns={
        "ENERGIETRAEGER__1": "Gas",
        "ENERGIETRAEGER__2": "Heating oil",
        "ENERGIETRAEGER__3": "Wood, wood pellets",
        "ENERGIETRAEGER__4": "Biomass (excluding wood), biogas",
        "ENERGIETRAEGER__5": "Solar/geothermal energy, heat pumps",
        "ENERGIETRAEGER__6": "Electricity (without heat pumps)",
        "ENERGIETRAEGER__7": "Energy source coal",
        "NERGIETRAEGER__8": "District heating (various energy sources)",
        "ENERGIETRAEGER__9": "No energy source (no heating)"})

    # Wide to long format
    energie_long = pd.melt(energie, id_vars=["Region"], 
                    value_vars=list(energie.columns[2:]),
                    var_name= "Energy source",
                    value_name = "Quantity")

    # Total count
    energie_long["Quantity"] = pd.to_numeric(energie_long["Quantity"], errors="coerce")
    total_count = energie_long["Quantity"].fillna(0).sum()

    # Calculate percentage
    energie_long["Percent"] = energie_long["Quantity"] / total_count * 100

    color_map = {
        "Gas": "#a6cee3",
        "Heating oil": "#1f78b4",
        "Wood, wood pellets": "#b2df8a",
        "Biomass (excluding wood), biogas": "#33a02c",
        "Solar/geothermal energy, heat pumps": "#fb9a99",
        "Electricity (without heat pumps)": "#e31a1c",
        "Energy source coal": "#fdbf6f",
        "District heating (various energy sources)": "#ff7f00",
        "No energy source (no heating)": "#cab2d6"}


    # Plot
    fig = px.treemap(
    energie_long,
    path=["Energy source"], 
    values="Percent", 
    color="Energy source",
    color_discrete_map=color_map,
    title="Proportion of apartments (in buildings with living space)<br>by energy source",
    labels={"Percent": "Percent"},
    template="seaborn")

    fig.update_traces(hovertemplate="<b>%{label}</b><br>Percent: %{value:.2f}%<extra></extra>")

    fig.update_layout(
        margin={"t": 40, "b": 40, "l": 0, "r": 0},
        coloraxis_colorbar=dict(title="Energy source"))

    st.plotly_chart(fig, use_container_width=True)



# Nutzung

with col1:
    
    # Subset
    nutzung = df_wohnungen[['Region', 'Regionalebene',
        'NUTZUNG__01', 'NUTZUNG__02', 'NUTZUNG__03', 'NUTZUNG__04']]
    
    # Selection
    nutzung = nutzung[nutzung["Region"]== selected_region]

    # Rename columns
    nutzung = nutzung.rename(columns = {
            "NUTZUNG__01": "Apartments occupied by the owner",
            "NUTZUNG__02": "Rented apartments",
            "NUTZUNG__03": "Privately used vacation or leisure apartments",
            "NUTZUNG__04": "Vacant apartments"})

    # Wide to long format
    nutzung_long = pd.melt(nutzung, 
                           id_vars=["Region"], 
                            value_vars=list(nutzung.columns[2:]))

    color_map = {
    "Apartments occupied by the owner": "#a6cee3",
    "Rented apartments": "#1f78b4",
    "Privately used vacation or leisure apartments": "#b2df8a",
    "Vacant apartments": "#33a02c"}


    # Plot
    fig = px.bar(nutzung_long, x="value", y="Region",
                color="variable", color_discrete_map=color_map,
                title="Number of apartments (in buildings with living space)<br>by use",
                labels={"value": "Quantity", "variable": "Use"},
                barmode="group",
                template = "seaborn",
                orientation="h")

    fig.update_layout(
    xaxis_title="Quantity",
    legend_title="Use",
    legend=dict(x=0.5, y=-0.2, xanchor="center", yanchor="top"))

    fig.update_traces(hovertemplate="<b>Use:</b> %{fullData.name}<br><b>Quantity:</b> %{x}<extra></extra>")

    fig.update_yaxes(tickangle=-90)

    st.plotly_chart(fig, use_container_width=True)


# Miete

with col2:

    # Subset
    miete = df_wohnungen[['Region', 'Regionalebene',
                          'MIETE_EURM2_2__01', 'MIETE_EURM2_2__02', 'MIETE_EURM2_2__03',
                          'MIETE_EURM2_2__04', 'MIETE_EURM2_2__05', 'MIETE_EURM2_2__06',
                          'MIETE_EURM2_2__07', 'MIETE_EURM2_2__08', 'MIETE_EURM2_2__09',
                          'MIETE_EURM2_2__10']]
    
    # Selection
    miete = miete[miete["Region"]== selected_region]

    # Rename columns
    miete= miete.rename(columns={
        "MIETE_EURM2_2__01": "under 4€/m²",
        "MIETE_EURM2_2__02": "between 4€/m² and under 6€/m²",
        "MIETE_EURM2_2__03": "between 6€/m² and under 8€/m²",
        "MIETE_EURM2_2__04": "between 8€/m² and under 10€/m²",
        "MIETE_EURM2_2__05": "between 10€/m² and under 12€/m²",
        "MIETE_EURM2_2__06": "between 12€/m² and under 14€/m²",
        "MIETE_EURM2_2__07": "between 14€/m² and under 16€/m²",
        "MIETE_EURM2_2__08": "between 16€/m² and under 18€/m²",
        "MIETE_EURM2_2__09": "between 18€/m² and under 20€/m²",
        "MIETE_EURM2_2__10": "20€/m² and more"})

    # Wide to long format
    miete_long = pd.melt(miete, id_vars=["Region"], 
                    value_vars=list(miete.columns[2:]),
                    var_name= "Net cold rent",
                    value_name = "Quantity")

    # Total count
    miete_long["Quantity"] = pd.to_numeric(miete_long["Quantity"], errors="coerce")
    total_count = miete_long["Quantity"].fillna(0).sum()


    # Calculate percentage
    miete_long["Percent"] = miete_long["Quantity"] / total_count * 100

    color_map = {
        "under 4€/m²": "#a6cee3",
        "between 4€/m² and under 6€/m²": "#1f78b4",
        "between 6€/m² and under 8€/m²": "#b2df8a",
        "between 8€/m² and under 10€/m²": "#33a02c",
        "between 10€/m² and under 12€/m²": "#fb9a99",
        "between 12€/m² and under 14€/m²": "#e31a1c",
        "between 14€/m² and under 16€/m²": "#fdbf6f",
        "between 16€/m² and under 18€/m²": "#ff7f00",
        "between 18€/m² and under 20€/m²": "#cab2d6",
        "20€/m² and more": "#6a3d9a"}


    # Plot
    fig = px.treemap(
    miete_long,
    path=["Net cold rent"], 
    values="Percent",
    color="Net cold rent",
    color_discrete_map=color_map,
    title="Proportion of apartments (in buildings with living space)<br>by net cold rent",
    labels={"Percent": "Percent"},
    template="seaborn")

    fig.update_traces(hovertemplate="<b>%{label}</b><br>Percent: %{value:.2f}%<extra></extra>")

    fig.update_layout(
        margin={"t": 40, "b": 40, "l": 0, "r": 0},
        coloraxis_colorbar=dict(title="Net cold rent"))

    st.plotly_chart(fig, use_container_width=True)



# Wohnfläche
 
with col1:
    # Subset
    wohnFlaeche = df_wohnungen[['Region', 'Regionalebene',
        'WOHNFLAECHE_20S__01', 'WOHNFLAECHE_20S__02',
        'WOHNFLAECHE_20S__03', 'WOHNFLAECHE_20S__04', 'WOHNFLAECHE_20S__05',
        'WOHNFLAECHE_20S__06', 'WOHNFLAECHE_20S__07', 'WOHNFLAECHE_20S__08',
        'WOHNFLAECHE_20S__09', 'WOHNFLAECHE_20S__10']]
    
    # Selection
    wohnFlaeche = wohnFlaeche[wohnFlaeche["Region"]== selected_region]

    # Rename columns
    wohnFlaeche = wohnFlaeche.rename(columns = {
            "WOHNFLAECHE_20S__01": "under 40m²",
            "WOHNFLAECHE_20S__02": "40m² to 59m²",
            "WOHNFLAECHE_20S__03": "60m² to 79m²",
            "WOHNFLAECHE_20S__04": "80m² to 99m²",
            "WOHNFLAECHE_20S__05": "100m² to 119m²",
            "WOHNFLAECHE_20S__06": "120m² to 139m²",
            "WOHNFLAECHE_20S__07": "140m² to 159m²",
            "WOHNFLAECHE_20S__08": "160m² to 179m²",
            "WOHNFLAECHE_20S__09": "180m² to 199m²",
            "WOHNFLAECHE_20S__10": "200m² and more"})

    # Wide to long format
    wohnFlaeche_long = pd.melt(wohnFlaeche, id_vars=["Region"], 
                    value_vars=["under 40m²", 
                                "40m² to 59m²",
                                "60m² to 79m²", 
                                "80m² to 99m²",
                                "100m² to 119m²",
                                "120m² to 139m²",
                                "140m² to 159m²",
                                "160m² to 179m²",
                                "180m² to 199m²",
                                "200m² and more"])

    color_map = {
    "under 40m²": "#a6cee3",
    "40m² to 59m²": "#1f78b4",
    "60m² to 79m²": "#b2df8a",
    "80m² to 99m²": "#33a02c",
    "100m² to 119m²": "#fb9a99",
    "120m² to 139m²": "#e31a1c",
    "140m² to 159m²": "#fdbf6f",
    "160m² to 179m²": "#ff7f00",
    "180m² to 199m²": "#cab2d6",
    "200m² and more": "#6a3d9a"}


    # Plot
    fig = px.bar(wohnFlaeche_long, x="value", y="Region",
                color="variable", color_discrete_map=color_map,
                title="Number of apartments (in buildings with living space)<br>by living area",
                labels={"value": "Quantity", "variable": "Living area"},
                barmode="group",
                template = "seaborn",
                orientation="h",
                height= 600)

    fig.update_layout(
    xaxis_title="Quantity",
    legend_title="Living area",
    legend=dict(x=0.5, y=-0.3, xanchor="center", yanchor="top", orientation= "h"))

    fig.update_traces(hovertemplate="<b>Living area:</b> %{fullData.name}<br><b>Quantity:</b> %{x}<extra></extra>")

    fig.update_yaxes(tickangle=-90)
    st.plotly_chart(fig, use_container_width=True)


# Raumzahl

with col2:
    # Subset
    raumZahl = df_wohnungen[['Region', 'Regionalebene',
        'RAUMANZAHL__01', 'RAUMANZAHL__02', 'RAUMANZAHL__03', 'RAUMANZAHL__04', 
        'RAUMANZAHL__05', 'RAUMANZAHL__06', 'RAUMANZAHL__07']]
    
    # Selection
    raumZahl = raumZahl[raumZahl["Region"]== selected_region]

    # Rename columns
    raumZahl = raumZahl.rename(columns={
        "RAUMANZAHL__01": "1 Room",
        "RAUMANZAHL__02": "2 Rooms",
        "RAUMANZAHL__03": "3 Rooms",
        "RAUMANZAHL__04": "4 Rooms",
        "RAUMANZAHL__05": "5 Rooms",
        "RAUMANZAHL__06": "6 Rooms",
        "RAUMANZAHL__07": "7 or more rooms"})

    # Wide to long format
    raumZahl_long = pd.melt(raumZahl, id_vars=["Region"], 
                    value_vars=list(raumZahl.columns[2:]),
                    var_name= "Living area",
                    value_name = "Quantity")

    # Total count
    total_count = raumZahl_long["Quantity"].fillna(0).sum()

    # Calculate percentage
    raumZahl_long["Percent"] = raumZahl_long["Quantity"] / total_count * 100

    color_map = {
        "1 Room": "#a6cee3",
        "2 Rooms": "#1f78b4",
        "3 Rooms": "#b2df8a",
        "4 Rooms": "#33a02c",
        "5 Rooms": "#fb9a99",
        "6 Rooms": "#e31a1c",
        "7 or more Rooms": "#fdbf6f"}


    # Plot
    wohnraum_order = ["1 Room", "2 Rooms", "3 Rooms", "4 Rooms", 
                      "5 Rooms", "6 Rooms", "7 or more Rooms"]

    fig = px.pie(raumZahl_long, names="Living area", values="Percent",
                color="Living area", color_discrete_map=color_map,
                title="Proportion of apartments (in buildings with living space)<br>by number of rooms",
                labels={"value": "Quantity", "variable": "Living area"},
                template = "seaborn",
                hole=0.3,
                category_orders={"Living area": wohnraum_order})

    fig.update_traces(
    textinfo="percent",
    insidetextorientation="radial",
    hovertemplate="<b>%{label}</b><br>Percent: %{percent}<extra></extra>")

    fig.update_layout(
    legend=dict(title=dict(text="Number of rooms"), orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5),
    margin=dict(b=100),
    height=600)

    st.plotly_chart(fig, use_container_width=False)


st.write(' ')
st.markdown('<p style="font-size: 11px;"><b>*Net cold rent per square meter:</b> The average net cold rent/sqm is the ratio between the sum of the square meter rent of the apartments and the sum of the apartments. The calculation is made for rented apartments in residential buildings (excluding halls of residence). Apartments not rented out are excluded from the calculation.</p>', unsafe_allow_html=True)

st.markdown('<p style="font-size: 11px;"><b>*Vacancy rate:</b> The vacancy rate represents the share of vacant apartments in all occupied and vacant apartments. Not taken into account: Vacation and leisure apartments as well as commercially used apartments. The calculation is made for apartments in residential buildings (excluding halls of residence).</p>', unsafe_allow_html= True)

st.markdown('<p style="font-size: 11px;"><b>*Ownership rate:</b> The ownership rate represents the proportion of owner-occupied apartments in relation to all occupied apartments. Not taken into account: Vacant apartments, vacation and leisure apartments and commercially used apartments. The calculation is made for apartments in residential buildings (excluding halls of residence).</p>', unsafe_allow_html= True)

st.markdown('<p style="font-size: 11px;"><b>*Area per apartment:</b> The average apartment size in m² is the ratio between the total area in m² and the total number of apartments. Commercially used apartments are not included. The calculation is made for apartments in residential buildings (excluding halls of residence).</p>', unsafe_allow_html=True)

