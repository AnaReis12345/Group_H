import streamlit as st
import yaml
import os
import base64
import requests
import pandas as pd
from datetime import datetime
from staticmap import StaticMap

# PAGE CONFIGURATION
st.set_page_config(page_title="AI Environmental Workflow", layout="wide")
st.title("AI Workflow - Environmental Risk Analysis")

# LOAD models.yaml
try:
    with open("models.yaml", "r") as file:
        config = yaml.safe_load(file)
    st.sidebar.success("Governance Downloaded!")
except FileNotFoundError:
    st.error("Error: models.yaml not found")
    st.stop()

# DATABASE PATH
DB_PATH = os.path.join("database", "images.csv")

# ─────────────────────────────────────────────
# FUNCTION: Load the database (or create empty one)
# ─────────────────────────────────────────────
def load_database() -> pd.DataFrame:
    """Load existing CSV database, or return empty DataFrame if it doesn't exist."""
    columns = [
        "timestamp", "latitude", "longitude", "zoom",
        "image_description", "image_prompt", "image_model",
        "text_description", "text_prompt", "text_model", "danger"
    ]
    if os.path.exists(DB_PATH):
        return pd.read_csv(DB_PATH)
    else:
        return pd.DataFrame(columns=columns)

# ─────────────────────────────────────────────
# FUNCTION: Save a new row to the database
# ─────────────────────────────────────────────
def save_to_database(lat, lon, zoom, image_desc, text_desc, danger_flag):
    """Append a new analysis result to the CSV database."""
    os.makedirs("database", exist_ok=True)

    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "latitude": lat,
        "longitude": lon,
        "zoom": zoom,
        "image_description": image_desc,
        "image_prompt": config['vision_model']['prompt'],
        "image_model": config['vision_model']['name'],
        "text_description": text_desc,
        "text_prompt": config['text_analysis']['prompt'],
        "text_model": config['text_analysis']['name'],
        "danger": "Y" if danger_flag else "N"
    }

    df = load_database()
    new_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DB_PATH, index=False)

# ─────────────────────────────────────────────
# FUNCTION: Check if location already exists in database
# ─────────────────────────────────────────────
def find_existing_result(lat, lon, zoom) -> pd.Series | None:
    """Check if we already analysed this exact location. If yes, return that row."""
    df = load_database()
    match = df[
        (df["latitude"] == lat) &
        (df["longitude"] == lon) &
        (df["zoom"] == zoom)
    ]
    if not match.empty:
        return match.iloc[-1]  # return the most recent match
    return None

# ─────────────────────────────────────────────
# FUNCTION: Download satellite image from ESRI
# ─────────────────────────────────────────────
def download_esri_image(lat, lon, zoom):
    size_str = config.get('image_settings', {}).get('size', '600x600')
    width, height = map(int, size_str.split('x'))
    url_template = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    mapa = StaticMap(width, height, url_template=url_template)
    image = mapa.render(zoom=zoom, center=[lon, lat])
    os.makedirs("images", exist_ok=True)
    file_path = os.path.join("images", f"satellite_{lat}_{lon}_{zoom}.png")
    image.save(file_path)
    return file_path

# ─────────────────────────────────────────────
# FUNCTION: Talk to Ollama AI
# ─────────────────────────────────────────────
def query_ollama(prompt, model_name, image_path=None):
    """Send text and/or image to Ollama local server."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode('utf-8')
            payload["images"] = [img_b64]
    try:
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code == 200:
            return response.json().get("response", "No response from AI.")
        else:
            return f"Error: Ollama returned status code {response.status_code}"
    except requests.exceptions.Timeout:
        return "Error: AI took too long to respond."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Is the Ollama app running?"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# ─────────────────────────────────────────────
# SIDEBAR INPUTS
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("Location Parameters")
    lat_input = st.number_input("Latitude", value=-3.4653, format="%.6f")
    lon_input = st.number_input("Longitude", value=-62.2159, format="%.6f")
    zoom_input = st.number_input("Zoom", value=config['image_settings']['zoom'], min_value=1, max_value=20)

# MODEL INFO
st.subheader("Configuration Analysis")
c1, c2 = st.columns(2)
with c1:
    st.info(f"**Vision Model:** {config['vision_model']['name']}")
with c2:
    st.info(f"**Analysis Model:** {config['text_analysis']['name']}")

# ─────────────────────────────────────────────
# MAIN BUTTON: Run the full pipeline
# ─────────────────────────────────────────────
if st.button("Execute Complete Analysis"):

    # STEP 0: Check if we already did this location
    existing = find_existing_result(lat_input, lon_input, zoom_input)

    if existing is not None:
        # ── Show cached result instead of re-running ──
        st.info("✅ This location was already analysed. Showing saved result.")

        saved_image_path = os.path.join("images", f"satellite_{lat_input}_{lon_input}_{zoom_input}.png")
        if os.path.exists(saved_image_path):
            st.image(saved_image_path, caption="Saved Satellite Image", use_container_width=True)

        st.subheader("📝 AI Description (saved)")
        st.write(existing["image_description"])

        st.subheader("⚖️ Final Diagnosis (saved)")
        if existing["danger"] == "Y":
            st.error(f"🚨 AT RISK — {existing['text_description']}")
        else:
            st.success(f"✅ SAFE — {existing['text_description']}")

    else:
        # ── Run the full pipeline ──
        with st.status("Processing workflow...") as status:

            # STEP A: Download satellite image
            status.update(label="Downloading satellite image (ESRI)...")
            img_path = download_esri_image(lat_input, lon_input, zoom_input)
            st.image(img_path, caption="Captured Image", use_container_width=True)

            # STEP B: AI describes the image
            status.update(label=f"AI analysing image with {config['vision_model']['name']}...")
            descricao = query_ollama(
                config['vision_model']['prompt'],
                config['vision_model']['name'],
                img_path
            )
            st.subheader("📝 AI Description")
            st.write(descricao)

            # STEP C: AI judges if area is at risk
            status.update(label=f"Generating diagnosis with {config['text_analysis']['name']}...")
            diagnostico_prompt = f"Description: {descricao}\n\nTask: {config['text_analysis']['prompt']}"
            diagnostico = query_ollama(diagnostico_prompt, config['text_analysis']['name'])

            st.subheader("⚖️ Final Diagnosis")
            danger_flag = "Y" in diagnostico[:10]
            if danger_flag:
                st.error(f"🚨 AT RISK — {diagnostico}")
            else:
                st.success(f"✅ SAFE — {diagnostico}")

            # STEP D: Save result to database
            status.update(label="Saving result to database...")
            save_to_database(
                lat=lat_input,
                lon=lon_input,
                zoom=zoom_input,
                image_desc=descricao,
                text_desc=diagnostico,
                danger_flag=danger_flag
            )

            status.update(label="Analysis Done!", state="complete")

# ─────────────────────────────────────────────
# SHOW DATABASE AT THE BOTTOM
# ─────────────────────────────────────────────
st.divider()
st.subheader("🗄️ Analysis History (database/images.csv)")
df_display = load_database()
if df_display.empty:
    st.info("No analyses run yet.")
else:
    st.dataframe(df_display, use_container_width=True)