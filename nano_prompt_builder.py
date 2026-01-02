import streamlit as st
import json
import datetime
from PIL import Image

# --- CONFIGURATION & DATA LISTS ---

# UPDATED: Added GQ/Luxury options
STYLES = [
    "GQ Magazine Editorial", "Inc.Magazine Cover page""Luxury Fashion", "High-End Portrait", # New
    "Photorealistic", "Anime/Manga", "Cyberpunk", "Oil Painting", 
    "Watercolor", "3D Render (Octane)", "Line Art", 
    "Brutalist Architecture", "Ukiyo-e", "Bauhaus", 
    "Lovecraftian Horror", "Solarpunk", "Vaporwave", "Baroque", 
    "Pointillism", "Low Poly", "Claymation", "Glitch Art"
]

# UPDATED: Added Elegant/Polished options
MOODS = [
    "Polished", "Elegant", "Vibrant", "Professional", # New
    "Happy", "Sad", "Angry", "Ethereal", "Melancholic", "Cynical", 
    "Stoic", "Whimsical", "Foreboding", "Euphoric", "Dysphoric", 
    "Nostalgic", "Zen", "Chaotic", "Ennui", "Gritty", "Sterile", "Opulent"
]

# UPDATED: Added Glossy/Studio options
LIGHTING = [
    "Cinematic Studio Lighting", "Glossy Highlights", "Softbox", # New
    "Sunny", "Volumetric (God Rays)", "Bioluminescence", 
    "Rim Lighting", "Rembrandt Lighting", "Chiaroscuro", "Neon", 
    "Cherenkov Radiation", "Candlelight", "Cinematic Teal/Orange", 
    "Caustics", "Global Illumination", "Hard Shadows"
]

# UPDATED: Added Cover-ready options
CAMERA_ANGLES = [
    "Centered (Cover-Ready)", "Negative Space Framing", # New
    "Eye Level", "Wide Angle", "Dutch Angle", "Macro", "Telephoto", 
    "Bird's Eye View", "Worm's Eye View", "Orthographic", 
    "Fish-eye Lens", "Bokeh", "Isometric"
]

# NEW LIST: Backgrounds
BACKGROUNDS = [
    "Clean Minimal", "Solid Color", "Studio Grey", "Gradient", 
    "Abstract Texture", "Bokeh City", "Nature", "Office Interior"
]

SAMPLERS = [
    "Euler a", "Euler", "DPM++ 2M Karras", "DPM++ SDE Karras", "DDIM", "UniPC"
]

# --- APP LAYOUT ---

st.set_page_config(page_title="Nano Banana Pro: GQ Edition", layout="wide")

st.title("🍌 Nano Banana Pro: Luxury/GQ Edition")
st.markdown("Generate high-end editorial prompts with precise control.")

# Create tabs
tab1, tab2, tab3 = st.tabs(["1. Composition & Subject", "2. Style & Atmosphere", "3. Tech & Output"])

# --- TAB 1: COMPOSITION & SUBJECT ---
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Subject Details")
        subject = st.text_input("Who is the subject?", placeholder="e.g., A man in his 30s")
        clothing = st.text_input("Clothing / Outfit", placeholder="e.g., Dark collared polo shirt")
        
        # Free Description
        free_desc = st.text_area("Additional Details (Free Text)", height=100, 
                                 placeholder="e.g., Retouch skin naturally with ultra-detailed textures. Remove chair.")

    with col2:
        st.subheader("Scene Composition")
        
        # Background Selection
        bg_select = st.selectbox("Background", ["Select from list..."] + BACKGROUNDS)
        bg_manual = st.text_input("...or Custom Background", placeholder="e.g., Luxury penthouse interior")
        final_bg = bg_manual if bg_manual else (bg_select if bg_select != "Select from list..." else "")

        # Camera
        cam_select = st.selectbox("Framing / Camera", ["Select from list..."] + CAMERA_ANGLES)
        cam_manual = st.text_input("...or Custom Camera", placeholder="e.g., Low angle")
        final_cam = cam_manual if cam_manual else (cam_select if cam_select != "Select from list..." else "")

# --- TAB 2: STYLE & ATMOSPHERE ---
with tab2:
    col_style1, col_style2 = st.columns(2)
    
    with col_style1:
        st.subheader("Visual Style")
        # Style Selection
        style_select = st.selectbox("Artistic Style", ["Select from list..."] + STYLES)
        style_manual = st.text_input("...or Custom Style", placeholder="e.g., Vogue Magazine")
        final_style = style_manual if style_manual else (style_select if style_select != "Select from list..." else "")

        # Mood Selection
        mood_select = st.multiselect("Mood & Atmosphere", MOODS)
        mood_manual = st.text_input("Add Custom Moods", placeholder="e.g., Muted color grading, Wealthy")
        
        final_moods = mood_select.copy()
        if mood_manual:
            final_moods.extend([m.strip() for m in mood_manual.split(",")])

    with col_style2:
        st.subheader("Lighting")
        light_select = st.selectbox("Lighting Setup", ["Select from list..."] + LIGHTING)
        light_manual = st.text_input("...or Custom Lighting", placeholder="e.g., Ring light")
        final_light = light_manual if light_manual else (light_select if light_select != "Select from list..." else "")

# --- TAB 3: TECH & OUTPUT ---
with tab3:
    col_tech1, col_tech2 = st.columns([1, 1])
    
    with col_tech1:
        st.subheader("Reference Image (Img2Img)")
        uploaded_file = st.file_uploader("Upload Starting Image", type=['png', 'jpg', 'jpeg'])
        
        img_strength = 0.75
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Reference Image", width=300)
            img_strength = st.slider("Denoising Strength (Influence)", 0.0, 1.0, 0.65, 
                                     help="Lower = closer to original image. Higher = more creative freedom.")
        else:
            st.info("No image uploaded. Workflow will be Text-to-Image.")

    with col_tech2:
        st.subheader("Generation Parameters")
        sampler = st.selectbox("Sampler", SAMPLERS, index=2)
        steps = st.slider("Sampling Steps", 10, 150, 40) # Increased default for high quality
        cfg = st.slider("CFG Scale", 1.0, 30.0, 7.0)
        seed = st.number_input("Seed (-1 for random)", value=-1)
        
        st.markdown("---")
        width = st.number_input("Width", value=1024, step=64)
        height = st.number_input("Height", value=1024, step=64)

    # Negative Prompt
    st.subheader("Exclusions")
    # Added your specific exclusions as default
    default_neg = "blurry, low quality, distorted face, text, logos, watermarks, extra limbs, artifacts, overexposed, poorly lit, cartoonish"
    neg_custom = st.text_area("Negative Prompt", value=default_neg)

# --- LOGIC TO BUILD PROMPT ---

# Construct prompt parts
mood_str = ", ".join(final_moods)

prompt_parts = []

# 1. Subject & Clothing
if subject: 
    full_subject = subject
    if clothing:
        full_subject += f" wearing {clothing}"
    prompt_parts.append(full_subject)

# 2. Main Style
if final_style: prompt_parts.append(f"{final_style} style")

# 3. Background & Environment
if final_bg: prompt_parts.append(f"{final_bg} background")

# 4. Details
if free_desc: prompt_parts.append(free_desc)
if mood_str: prompt_parts.append(mood_str)
if final_light: prompt_parts.append(final_light)
if final_cam: prompt_parts.append(final_cam)

# 5. Quality Boosters (Hardcoded as per your request)
prompt_parts.append("8k ultra-realistic quality, crisp, cover-ready")

final_positive_prompt = ", ".join(prompt_parts)

# Construct JSON
json_output = {
  "nano_banana_pro_request": {
    "meta_information": {
      "project_name": f"GQ_Batch_{datetime.date.today()}",
      "workflow_type": "Image-to-Image" if uploaded_file else "Text-to-Image"
    },
    "1_creative_vision": {
      "subject": subject,
      "clothing": clothing,
      "style": final_style,
      "background": final_bg,
      "moods": final_moods, 
      "lighting": final_light,
      "camera": final_cam
    },
    "2_prompt_engineering": {
      "final_positive_prompt": final_positive_prompt,
      "final_negative_prompt": neg_custom,
    },
    "3_generation_parameters": {
      "resolution": f"{width}x{height}",
      "sampler": sampler,
      "steps": steps,
      "cfg_scale": cfg,
      "seed": seed
    },
    "4_input_image": {
      "enabled": True if uploaded_file else False,
      "filename": uploaded_file.name if uploaded_file else None,
      "denoising_strength": img_strength if uploaded_file else None
    }
  }
}

# --- TAB 3: OUTPUT ---
with tab3:
    st.success("GQ Spec Generated!")
    
    st.subheader("📝 Final Prompt String")
    st.code(final_positive_prompt, language="text")
    
    st.subheader("🚫 Negative Prompt")
    st.code(neg_custom, language="text")
    
    st.subheader("💾 Full JSON Specification")
    st.json(json_output)
    
    # Download Button
    json_string = json.dumps(json_output, indent=2)
    st.download_button(
        label="Download JSON Spec",
        data=json_string,
        file_name="gq_editorial_spec.json",
        mime="application/json"
    )