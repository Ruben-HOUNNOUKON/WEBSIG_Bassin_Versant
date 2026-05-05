import streamlit as st
import leafmap.foliumap as leafmap
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# Cette condition vérifie si on est sur le Web ou en Local
if 'STREAMLIT_RUNTIME__IS_RELEASE' in os.environ:
    # On est sur le Web (GitHub/Streamlit Cloud) -> On met le proxy
    os.environ['LOCALTILESERVER_CLIENT_PREFIX'] = 'proxy/8501'
else:
    # On est en local sur ton PC -> On ne met rien
    if 'LOCALTILESERVER_CLIENT_PREFIX' in os.environ:
        del os.environ['LOCALTILESERVER_CLIENT_PREFIX']

# 1. Configuration (Design conservé)
st.set_page_config(
    page_title="WebSIG Premium | Bassin Versant",
    page_icon="📡",
    layout="wide"
)

# 2. Design CSS (Strictement inchangé)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Roboto:wght@300;400&display=swap');
    html, body, [class*="css"]  { font-family: 'Roboto', sans-serif; }
    h1, h2, h3 { font-family: 'Montserrat', sans-serif; font-weight: 800; color: #0d1b2a; }
    .main { background-color: #f0f2f5; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; padding: 15px; border-radius: 15px; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-top: 5px solid #00b4d8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/geography.png", width=80)
    st.title("🛠️ Configuration")
    st.markdown("---")
    basemap_choice = st.selectbox("Style de cartographie", ["Mapbox Satellite", "Mapbox Light", "Stadia.AlidadeSmooth", "OpenStreetMap"])
    alpha_hill = st.slider("Ombrage du relief (Hillshade)", 0.0, 1.0, 0.65)
    alpha_dem = st.slider("Gradient d'altitude (Dem)", 0.0, 1.0, 0.65)
    st.divider()
    st.caption("Solution WebSIG développée par Ruben HOUNNOUKON.")

# --- EN-TÊTE ---
st.title("📡 PLATEFORME DÉCISIONNELLE HYDRO-DATA")
st.markdown("##### *Analyse morphométrique et modélisation du bassin versant de 10 445 km²*")

# Ligne de KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("SUPERFICIE", "10 445 km²", "SUPERFICIE:10445 km²")
k2.metric("PÉRIMÈTRE", "530,2 km", "PÉRIMÈTRE : 530,2 km")
k3.metric("ORDRE STRAHLER", "5", "ORDRE DU RESEAU : 5")
k4.metric("PRECISION MNT", "30m", "SRTM : 30m")

st.markdown("---")

# --- SECTION CARTOGRAPHIE ---
col_map, col_stats = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ Exploration Spatiale")
    
    m = leafmap.Map(center=[9.68, 2.05], zoom=10) 
    m.add_basemap(basemap_choice)

    # --- DEFINITION DE LA PALETTE COMMUNE ---
    # Couleurs : Bleu (bas), Vert, Jaune, Marron (haut)
    palette_bv = ['#3333ff', '#32CD32', '#FFFF00', '#8B4513']

    # --- RENDU RASTER ---
    if os.path.exists("Hillshade.tif"):
        m.add_raster("Hillshade.tif", layer_name="Ombrage (Hillshade)", opacity=alpha_hill)

    if os.path.exists("Dem.tif"):
        # Application de la palette identique au raster et à la légende
        m.add_raster("Dem.tif", palette=palette_bv, vmin=150, vmax=600, layer_name="Altitude (DEM)", opacity=alpha_dem)
        m.add_colorbar(colors=palette_bv, vmin=150, vmax=600, label="Altitude (m)")
        
    # --- SYMBOLOGIE DES RIVIÈRES ---
    def style_rivieres(feature):
        ordre = feature['properties'].get('ordre', feature['properties'].get('ORDRE', 1))
        return {'color': '#0077b6', 'weight': (ordre * 1.5), 'opacity': 0.8}

    if os.path.exists("Reseau_hydrographique.geojson"):
        m.add_geojson("Reseau_hydrographique.geojson", layer_name="Hydrographie", style_callback=style_rivieres)
    
    # --- SYMBOLOGIE EXUTOIRE (CERCLE ORANGE À CONTOUR NOIR) ---
    if os.path.exists("Exutoire.geojson"):
        try:
            with open("Exutoire.geojson") as f:
                gj = json.load(f)
                # On récupère les coordonnées du premier point
                coords = gj['features'][0]['geometry']['coordinates']
                # Ajout direct en tant que cercle pour éviter l'icône bleue
                m.add_circle_marker(
                    location=[coords[1], coords[0]], 
                    radius=10, 
                    color="black", 
                    fill_color="#ff6600", 
                    fill_opacity=1, 
                    weight=3, 
                    layer_name="Exutoire"
                )
        except Exception:
            # Fallback si le fichier est vide ou mal formé
            m.add_geojson("Exutoire.geojson", layer_name="Exutoire")
    
    if os.path.exists("Bassin.geojson"):
        m.add_geojson("Bassin.geojson", layer_name="Limite", 
                      style={'color': '#1d3557', 'fillOpacity': 0, 'weight': 3, 'dashArray': '8, 8'})

    m.to_streamlit(height=600)

with col_stats:
    st.subheader("📊 Analytics")
    data_strahler = {'Ordre': ['1', '2', '3', '4', '5'], 'Densité': [55, 25, 12, 5, 3]}
    fig_bar = px.bar(data_strahler, x='Ordre', y='Densité', 
                     title="Répartition du Réseau (%)", 
                     color='Densité', color_continuous_scale='Blues')
    
    # MODIFICATION ICI : On force l'affichage de toutes les étiquettes
    fig_bar.update_layout(
        showlegend=False, 
        height=300, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'type': 'category'} # Force l'affichage de 1, 2, 3, 4, 5
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_pie = go.Figure(data=[go.Pie(labels=['Bassin', 'Zones Inondables', 'Zones Stables'], values=[10445, 1200, 9245], hole=.6)])
    fig_pie.update_layout(title="Occupation du Sol (Estimé)", height=300, showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
f_col1, f_col2 = st.columns([2, 1])
with f_col1:
    st.markdown("### 🎯 Valeur Ajoutée")
    st.write("""
    Cette interface transforme des données brutes en **insights exploitables**. 
    La superposition du **Dem** et du **Hillshade** permet une analyse fine de la topographie, 
    essentielle pour la planification des ouvrages hydrauliques.
    """)
with f_col2:
    st.success("💻 Développé par **Ruben HOUNNOUKON**\n\nIngénierie & Géodata")
