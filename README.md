# Group_H
## Team Members
70047 Ana Reis - 70047@novasbe.pt
59479 Duarte Maria Carvalho - 59479@novasbe.pt
73174 Kaltoum El Glaoui Hamdellah - 73174@novasbe.pt
52736 Gabriel Vieira - 52736@novasbe.pt

## Installation and Setup

### Requirements
- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running

### Steps
1. Clone the repository:
```bash
git clone https://github.com/AnaReis12345/Group_H.git
cd Group_H
```
2. Install dependencies:
```bash
conda install -c conda-forge geopandas
/opt/anaconda3/bin/pip install streamlit staticmap pandas pyyaml requests
```
3. Pull the required AI models:
```bash
ollama pull llava
ollama pull llama3
```
4. Run the app:
```bash
streamlit run main.py
```


## SDGs — How This Project Contributes

This project directly supports three of the United Nations Sustainable Development Goals:

**SDG 15 — Life on Land:** The core purpose of this tool is to monitor and identify threats to terrestrial ecosystems. By analysing satellite imagery with AI, the app can detect deforestation, illegal logging, and land degradation in real time, helping conservation efforts target the most at-risk areas.

**SDG 13 — Climate Action:** Deforestation is one of the leading causes of greenhouse gas emissions. By identifying areas of forest loss early, this tool supports climate monitoring efforts and can help organisations take action before damage becomes irreversible.

**SDG 17 — Partnerships for the Goals:** This project is built entirely on free and open-source tools — Python, Streamlit, Ollama, and public satellite imagery. This means it can be freely adopted and adapted by NGOs, governments, and researchers around the world, lowering the barrier to environmental monitoring.


## Examples of Environmental Danger Detection

### Example 1 — Deforested Amazon, Brazil (-9.1654, -62.8543)
![Example 1](images/example1.png)
The AI identified a large cleared patch with visible stumps and reddish-brown burned areas, contrasting sharply with the surrounding dense forest. Signs of illegal logging activity were detected, flagging the area as **AT RISK** due to significant environmental damage, potential wildfires, loss of biodiversity, and increased greenhouse gas emissions.

### Example 2 — Rondônia, Brazil (-11.0000, -62.0000)
![Example 2](images/example2.png)
The AI detected a large patch of bare earth surrounded by green vegetation, suggesting active deforestation or recent land use change. Darker patches within the greener areas indicated possible illegal logging. The area was flagged as **AT RISK** due to threats to biodiversity, soil erosion, and land degradation.

### Example 3 — Madre de Dios, Peru (-12.5000, -70.0000)
![Example 3](images/example3.png)
The AI identified significant forest clearing in the middle section of the image, with large areas replaced by non-forest cover suggesting agricultural use or infrastructure development. Forest fragmentation and systematic clearing patterns were detected, flagging the area as **AT RISK** due to habitat loss, increased risk of soil erosion,and negative impacts on local ecosystems and biodiversity.