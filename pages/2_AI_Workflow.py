import streamlit as st
import yaml
import os
import base64
import requests
from staticmap import StaticMap

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="AI Environmental Workflow", layout="wide")
st.title("AI Workflow - Environmental Risk Analysis")

# CARREGAR GOVERNAÇÃO
try:
    with open("models.yaml", "r") as file:
        config = yaml.safe_load(file)
    st.sidebar.success("Governance Downloaded!")
except FileNotFoundError:
    st.error("Erro: models.yaml not found")
    st.stop()

# FUNÇÃO: DOWNLOAD ESRI
def download_esri_image(lat, lon, zoom):
    size_str = config.get('image_settings', {}).get('size', '600x600')
    width, height = map(int, size_str.split('x'))
    
    url_template = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    
    mapa = StaticMap(width, height, url_template=url_template)
    image = mapa.render(zoom=zoom, center=[lon, lat])
    
    os.makedirs("images", exist_ok=True)
    file_path = os.path.join("images", "satellite_view.png")
    image.save(file_path)
    return file_path

# FUNÇÃO: COMUNICAÇÃO COM OLLAMA
def query_ollama(prompt, model_name, image_path=None):
    """Send text and/or image to Ollama local server"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    if image_path and os.path.exists(image_path):
        import base64
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
        return "Error: AI took too long to respond. Please ensure Ollama is ready and try again."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Is the Ollama app running?"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
        

# INTERFACE LATERAL (INPUTS)
with st.sidebar:
    st.header("Location Parameters")
    lat_input = st.number_input("Latitude", value=-3.4653, format="%.6f")
    lon_input = st.number_input("Longitude", value=-62.2159, format="%.6f")
    zoom_input = st.number_input("Zoom", value=config['image_settings']['zoom'], min_value=1, max_value=20)

# CONFIGURAÇÃO DA IA
st.subheader("Configuration Analysis")
c1, c2 = st.columns(2)
with c1:
    st.info(f"**Vision Model:** {config['vision_model']['name']}")
with c2:
    st.info(f"**Analysis Model:** {config['text_analysis']['name']}")

# EXECUÇÃO DO WORKFLOW
if st.button("Execute Complete Analysis"):
    with st.status("Processing workflow...") as status:
        
        # PASSO A: Download da Imagem
        status.update(label="downoading satalite images (ESRI)...")
        img_path = download_esri_image(lat_input, lon_input, zoom_input)
        st.image(img_path, caption="Imagem Capturada", use_container_width=True)
        
        # PASSO B: Descrição Visual (Llava)
        status.update(label=f"AI Analysing Image with {config['vision_model']['name']}...")
        descricao = query_ollama(config['vision_model']['prompt'], 
                                config['vision_model']['name'], 
                                img_path)
        
        st.subheader("📝 AI Description")
        st.write(descricao)
        
        # PASSO C: Diagnóstico de Risco (Llama3)
        status.update(label=f"A gerar diagnóstico com {config['text_analysis']['name']}...")
        diagnostico_prompt = f"Description: {descricao}\n\nTask: {config['text_analysis']['prompt']}"
        diagnostico = query_ollama(diagnostico_prompt, config['text_analysis']['name'])
        
        st.subheader("⚖️ Final Diagnosis")
        if "Y" in diagnostico[:10]: 
            st.error(diagnostico)
        else:
            st.success(diagnostico)
            
        status.update(label="Analysis Done!", state="complete")