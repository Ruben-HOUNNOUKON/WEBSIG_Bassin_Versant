import streamlit as st
import leafmap.foliumap as leafmap
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# 1. Configuration
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

# ==============================================================================
# 🔧 CONFIGURATION DES URLS DISTANTES
# ------------------------------------------------------------------------------
# ÉTAPE 1 : Remplace les ID ci-dessous par les vrais ID de tes fichiers Google Drive
#
# Comment trouver l'ID ?
#   → Ouvre ton fichier sur Google Drive
#   → Clic droit → "Obtenir le lien" → "Tout le monde avec le lien" (Lecteur)
#   → L'URL ressemble à : https://drive.google.com/file/d/XXXXXXXXXXXXXXXXXXXXX/view
#   → Copie uniquement la partie XXXXXXXXXXXXXXXXXXXXX
#
# IMPORTANT : Tes fichiers doivent être au format COG (.tif converti, voir instructions)
# ==============================================================================

HILLSHADE_GDRIVE_ID = "HTjXuk3gJ5D1-gJBngbPp2-J5j1G18RG"   # ← colle l'ID ici
DEM_GDRIVE_ID       = "FF7pFf8Kzbx46JxJVN3z3zfxSrER0a8V"          # ← colle l'ID ici

# Construction automatique des URLs (ne pas modifier cette ligne)
HILLSHADE_URL = f"https://drive.google.com/uc?export=download&id={HILLSHADE_GDRIVE_ID}"
DEM_URL       = f"https://drive.google.com/uc?export=download&id={DEM_GDRIVE_ID}"

# ==============================================================================

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

    # --- RENDU RASTER HILLSHADE (URL distante Google Drive) ---
    # ✅ Remplace l'ancien bloc : if os.path.exists("Hillshade.tif")
    try:
        m.add_raster(HILLSHADE_URL, layer_name="Ombrage (Hillshade)", opacity=alpha_hill)
    except Exception as e:
        st.warning(f"⚠️ Hillshade non chargé : {e}")

    # --- RENDU RASTER DEM (URL distante Google Drive) ---
    # ✅ Remplace l'ancien bloc : if os.path.exists("Dem.tif")
    try:
        m.add_raster(DEM_URL, palette=palette_bv, vmin=150, vmax=600,
                     layer_name="Altitude (DEM)", opacity=alpha_dem)
        m.add_colorbar(colors=palette_bv, vmin=150, vmax=600, label="Altitude (m)")
    except Exception as e:
        st.warning(f"⚠️ DEM non chargé : {e}")

    # --- SYMBOLOGIE DES RIVIÈRES (inchangé — GeoJSON reste dans le repo GitHub) ---
    def style_rivieres(feature):
        ordre = feature['properties'].get('ordre', feature['properties'].get('ORDRE', 1))
        return {'color': '#0077b6', 'weight': (ordre * 1.5), 'opacity': 0.8}

    if os.path.exists("Reseau_hydrographique.geojson"):
        m.add_geojson("Reseau_hydrographique.geojson", layer_name="Hydrographie", style_callback=style_rivieres)

    # --- SYMBOLOGIE EXUTOIRE (inchangé) ---
    if os.path.exists("Exutoire.geojson"):
        try:
            with open("Exutoire.geojson") as f:
                gj = json.load(f)
                coords = gj['features'][0]['geometry']['coordinates']
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
            m.add_geojson("Exutoire.geojson", layer_name="Exutoire")

    # --- LIMITE DU BASSIN (inchangé) ---
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
    fig_bar.update_layout(
        showlegend=False,
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'type': 'category'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_pie = go.Figure(data=[go.Pie(
        labels=['Bassin', 'Zones Inondables', 'Zones Stables'],
        values=[10445, 1200, 9245], hole=.6
    )])
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
