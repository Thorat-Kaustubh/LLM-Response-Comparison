<!-- PROJECT HEADER -->
<div align="center">

# 🔍 **LLM Response Comparison Dashboard**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR_STREAMLIT_APP_URL_HERE)
[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/YOUR_USERNAME)

_A visual and analytical dashboard to compare responses from generative AI models under two prompt configurations._

</div>

---

## 🌈 **Overview**

The **LLM Response Comparison Dashboard** provides a simple and powerful way to **visually compare, analyze, and quantify** how a generative model (Google’s `gemini-2.5-flash-preview-09-2025`) behaves under:

1. **User Prompt Only**
2. **System Prompt + User Prompt**

It’s built for **AI researchers, NLP developers, and prompt engineers** who want to measure — not guess — how prompts influence model performance.

<p align="center">
  <img src="image1.jpg"  width="600"><br><br>
  <img src="image2.jpg" width="600">
</p>

---

## ⚡ **Core Features**

✨ **Side-by-Side Comparison**  
> Instantly see differences between plain user prompts and engineered (system + user) prompts.  

📊 **Automated Metrics**  
> Compare **token count**, **character length**, and **finish reason** automatically.  

🧠 **Smart Insights**  
> Generates a plain-English verdict on which response is more detailed, concise, or token-efficient.  

🧩 **Clean Architecture**  
> Decoupled backend (`app_backend.py`) for logic and frontend (`app_frontend.py`) for UI.  

🔍 **Raw API Viewer**  
> Inspect raw JSON responses from the API for debugging and transparency.

---

## 💡 **Why This Project?**

Prompt engineering is powerful — but often **hard to prove**.

This project provides a visual and analytical way to:
- ✅ **Quantify** the impact of a system prompt  
- 🔍 **Debug** prompt behavior for tone, structure, and coherence  
- 📈 **Demonstrate** measurable improvements to teams or clients  

> _“If you can measure it, you can improve it.”_ — Peter Drucker

---

## 🧠 **Tech Stack**

| Layer | Technology |
|--------|-------------|
| **Frontend** | [Streamlit](https://streamlit.io/) |
| **Backend** | [Python](https://www.python.org/) |
| **Model** | `gemini-2.5-flash-preview-09-2025` |
| **API Calls** | `requests` |
| **Data Handling** | `pandas` |
| **Visualization** | Streamlit components & Markdown UI |

---

## ⚙️ **Setup & Installation**

### 🪄 Step 1 — Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME


### 🧩 Step 2 — Install Dependencies
pip install -r requirements.txt

###🔑 Step 3 — Configure API Key
Create .streamlit/secrets.toml and add your Gemini API key:

# .streamlit/secrets.toml
GEMINI_API_KEY = "YOUR_API_KEY_GOES_HERE"

###▶️ Step 4 — Run the App
streamlit run app_frontend.py

Then open your browser and visit 👉 http://localhost:8501

## 🎯 **How to Use**

Follow these simple steps to interact with the **LLM Response Comparison Dashboard**:

1. **🧠 Enter User Prompt**  
     Type your main query for the LLM.  
    _Example:_  
  Explain quantum entanglement.


2. **🎓 Enter System Prompt**  
    Provide contextual or role-based instructions for the model.  
    _Example:_  
    You are a physics professor. Explain simply.


3. **⚡ Click “Compare Responses”**  
The app will generate and display both responses — one for the user prompt alone and one for the system + user prompt combination.

4. **📊 Analyze Results**  
- View both responses **side-by-side** for easy comparison  
- Review **token count**, **character length**, and **finish reason**  
- Read **automated insights** that summarize which version is more detailed, concise, or efficient  

---

## 🏷️ **License**

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for complete details.

> © 2025 **Kaustubh Thorat** — All rights reserved.
