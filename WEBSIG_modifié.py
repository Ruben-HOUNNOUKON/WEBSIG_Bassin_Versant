import streamlit as st
import leafmap.foliumap as leafmap # Gardé pour le design Folium
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DU SERVEUR DE RASTER ---
# On s'assure que le prefix est bien là AVANT tout chargement

st.set_page_config(
    page_title="WebSIG Premium | Bassin Versant",
    page_icon="📡",
    layout="wide"
)

# --- 2. DESIGN "HAUTE COUTURE" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&family=Roboto:wght@300;400&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    h1, h2, h3 { font-family: 'Montserrat', sans-serif; font-weight: 800; color: #0d1b2a; }
    .main { background-color: #f0f2f5; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-top: 5px solid #00b4d8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/geography.png", width=80)
    st.title("🛠️ Configuration")
    st.markdown("---")
    basemap_choice = st.selectbox(
        "Style de cartographie", 
        ["OpenStreetMap", "HYBRID", "TERRAIN"]
    )
    alpha_hill = st.slider("Ombrage du relief (Hillshade)", 0.0, 1.0, 0.35)
    alpha_dem = st.slider("Gradient d'altitude (Dem)", 0.0, 1.0, 0.45)

# --- EN-TÊTE ---
st.title("📡 PLATEFORME DÉCISIONNELLE HYDRO-DATA")
st.markdown("##### *Analyse morphométrique et modélisation du bassin versant*")

k1, k2, k3, k4 = st.columns(4)
k1.metric("SUPERFICIE", "10 445 km²")
k2.metric("PÉRIMÈTRE", "530,2 km")
k3.metric("ORDRE STRAHLER", "5")
k4.metric("PRECISION", "30m")

st.markdown("---")

col_map, col_stats = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ Exploration Spatiale")
    
    # --- LA CORRECTION TECHNIQUE ICI ---
    # On initialise la carte
    m = leafmap.Map(center=[9.7, 1.9], zoom=10)
    m.add_basemap(basemap_choice)

    # Ajout des Rasters avec gestion d'erreurs pour éviter le crash
    try:
        if os.path.exists("Hillshade.tif"):
            m.add_raster("Hillshade.tif", layer_name="Ombrage (Hillshade)", opacity=alpha_hill)
        
        if os.path.exists("Dem.tif"):
            m.add_raster("Dem.tif", palette="terrain", layer_name="Altitude (DEM)", opacity=alpha_dem)
    except Exception as e:
        st.error(f"Note : Le serveur de relief est en cours de chargement... ({e})")

    # --- VECTEURS ---
    if os.path.exists("Reseau_hydrographique.geojson"):
        m.add_geojson("Reseau_hydrographique.geojson", layer_name="Hydrographie", 
                      style={'color': '#0077b6', 'weight': 2.5})
    
    if os.path.exists("Bassin.geojson"):
        m.add_geojson("Bassin.geojson", layer_name="Limite", 
                      style={'color': '#1d3557', 'fillOpacity': 0, 'weight': 3, 'dashArray': '8, 8'})

    # Affichage final[cite: 2]
    m.to_streamlit(height=600)

with col_stats:
    st.subheader("📊 Analytics")
    data_strahler = {'Ordre': ['1', '2', '3', '4', '5'], 'Densité': [55, 25, 12, 5, 3]}
    fig_bar = px.bar(data_strahler, x='Ordre', y='Densité', color='Densité', color_continuous_scale='Blues')
    fig_bar.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True)

st.success("💻 Développé par Ruben HOUNNOUKON")
