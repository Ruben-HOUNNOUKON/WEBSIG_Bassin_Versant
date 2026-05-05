import streamlit as st
import leafmap.foliumap as leafmap

# Configuration de l'interface
st.set_page_config(layout="wide", page_title="WebSIG Bassin Versant | Ruben H.")

st.sidebar.title("🛠️ Paramètres d'affichage")
st.sidebar.markdown("Personnalisez votre vue du bassin versant.")

# Titre principal
st.title("🌊 WebSIG Dynamique : Analyse du Bassin Versant")
st.markdown("""
Ce portail interactif présente la convergence de la **Topographie**, des **SIG** et du **Développement Web**.
Explorez le relief, le réseau hydrographique et les données d'altitude en temps réel.
""")

# --- CONFIGURATION DE LA CARTE ---
m = leafmap.Map(center=[9.7, 1.9], zoom=10) # Ajuste les coordonnées si besoin

# 1. Ajout des fonds de carte
m.add_basemap("HYBRID") # Satellite + Routes
m.add_basemap("TERRAIN")

# 2. Ajout du Hillshade (L'ombrage pour le relief)
# On le met en fond pour donner de la texture
m.add_raster("Hillshade.tif", layer_name="Ombrage (Hillshade)", opacity=0.5)

# 3. Ajout du DEM (MNT) avec un curseur de transparence dans la barre latérale
alpha = st.sidebar.slider("Transparence du MNT (Altitude)", 0.0, 1.0, 0.6)
m.add_raster("Dem.tif", palette="terrain", layer_name="Altitude (DEM)", opacity=alpha)

# 4. Ajout des vecteurs (GeoJSON) avec style pro
style_bassin = {'color': '#000000', 'fillOpacity': 0, 'weight': 3}
m.add_geojson("Bassin.geojson", layer_name="Limite du Bassin", style=style_bassin)

m.add_geojson("Reseau_hydrographique.geojson", layer_name="Réseau Hydrographique", info_mode="on_click")

# 5. Ajout de l'Exutoire avec une icône spéciale
m.add_geojson("Exutoire.geojson", layer_name="Exutoire")

# Affichage de la carte dans Streamlit
m.to_streamlit(height=700)

# --- SECTION ANALYSE (Sous la carte) ---
st.header("📊 Synthèse Morphométrique")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Superficie", "10 445 km²")
with col2:
    st.metric("Périmètre", "530,2 km")
with col3:
    st.metric("Ordre max", "5 (Strahler)")

st.success("Application développée par Ruben HOUNNOUKON - Ingénierie & Géodata")
