import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
from google import genai
from dotenv import load_dotenv
import os
import random

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="Roast My Room 🔥", page_icon="🔥", layout="centered")

st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 1rem 2rem 1rem; max-width: 600px; }
    h1 { text-align: center; font-size: 2.2rem !important; margin-bottom: 0 !important; }
    .subtitle { text-align: center; color: #666; font-size: 0.95rem; margin-bottom: 1.5rem; }
    .roast-box {
        background: #1a0000;
        border: 1px solid #ff4444;
        border-radius: 14px;
        padding: 18px 20px;
        font-size: 1.05rem;
        color: #ff6b6b;
        line-height: 1.7;
        margin: 8px 0 16px 0;
    }
    .score-row { display: flex; gap: 8px; margin: 12px 0; }
    .score-card {
        flex: 1;
        background: #111;
        border: 1px solid #222;
        border-radius: 10px;
        padding: 12px 6px;
        text-align: center;
    }
    .score-num { font-size: 1.5rem; font-weight: 700; line-height: 1; }
    .score-label { font-size: 0.65rem; color: #666; margin-top: 4px; }
    .section-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 20px 0 8px 0;
    }
    .objects-text { font-size: 0.9rem; color: #aaa; margin-bottom: 4px; }
    img { border-radius: 10px; }
    .footer { text-align: center; color: #333; font-size: 0.75rem; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

model = YOLO("yolov8s.pt")

ROASTER_PERSONALITIES = [
    "a terminally online 4chan user typing at 3am who hasn't touched grass in months",
    "a disappointed Indian parent who expected better from you",
    "a savage Gen Z therapist who gave up being professional",
    "a brutally honest interior designer having a mental breakdown",
    "a disappointed older sibling who has seen too much",
]

def analyze_room(img_array):
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size

    floor = img_array[int(img_array.shape[0]*0.6):, :]
    floor_std = np.std(cv2.cvtColor(floor, cv2.COLOR_RGB2GRAY))

    hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    high_sat_ratio = np.sum(hsv[:,:,1] > 100) / hsv[:,:,1].size
    brightness = np.mean(gray)

    details = []
    if edge_density > 0.15: details.append("extreme mess everywhere")
    elif edge_density > 0.08: details.append("noticeable clutter")
    else: details.append("suspiciously empty")

    if floor_std > 60: details.append("stuff thrown all over the floor")
    elif floor_std > 35: details.append("some things on the floor")

    if high_sat_ratio > 0.3: details.append("colorful chaos everywhere")
    elif high_sat_ratio < 0.1: details.append("depressingly dull colors")

    if brightness < 80: details.append("dark like a crime scene")
    elif brightness > 180: details.append("blinding bright lighting")
    else: details.append("mid lighting")

    return details, brightness, edge_density, floor_std

def calculate_scores(objects, edge_density, floor_std):
    total = sum(objects.values())
    mess = min(10, int(edge_density * 60))
    hygiene = min(10, max(1, 10 - mess - (2 if floor_std > 60 else 0)))
    social = max(1, 6 - sum(1 for o in ["bed","couch","chair","laptop","tv"] if o in objects))
    life = min(10, max(1, 10 - (total // 2) - (3 if floor_std > 60 else 0)))
    chaos = min(10, max(1, int(edge_density * 50) + (3 if floor_std > 60 else 0)))
    return {"🧹 Hygiene": hygiene, "👥 Social Life": social, "🎯 Life Choices": life, "🌪️ Chaos": chaos}

def get_roast(objects, img_array, intensity):
    object_list = ", ".join([f"{count}x {name}" for name, count in objects.items()]) if objects else "almost nothing"
    total_objects = sum(objects.values())
    details, brightness, edge_density, floor_std = analyze_room(img_array)

    if intensity == "Mild 🌶":
        tone = "light and funny like a friend roasting you"
        length = "1 short punchy sentence"
    elif intensity == "Spicy 🌶🌶":
        tone = "brutal, short punchy sentences, no big words"
        length = "2 short sentences"
    else:
        tone = "unhinged internet troll at 3am, chaotic, no big words, typed in rage"
        length = "2-3 short punchy sentences each hitting harder"

    prompt = f"""You are {random.choice(ROASTER_PERSONALITIES)}.
Roast this person's room hard.

Room: {object_list}
Vibe: {", ".join(details)}

Tone: {tone}
Length: {length}

Copy this exact style:
"bro really said 3 backpacks and nowhere to go this man is ready to run from his problems and never does"
"two beds one person bro is rotating sleeping spots like he's hiding from debt"
"clothes on the floor aren't laundry they're a timeline of every time you gave up"
"no way you wake up in this room and think today will be different"
"bro said let me own 6 books and call it a personality"

Rules:
- simple short words only
- specific to the objects found
- no big vocabulary
- no words like illuminated manifestation perpetually underbelly
- end with a gut punch
- sound human not AI

Just the roast. Go."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text, brightness, edge_density, floor_std

def share_text(roast, scores):
    worst = min(scores, key=scores.get)
    return f'🔥 AI roasted my room and I\'m not okay\n\n"{roast}"\n\n{worst}: {scores[worst]}/10 💀\n\nhttps://huggingface.co/spaces/AyushZoro0092/roast-my-room'

# --- UI ---

st.title("🔥 Roast My Room")
st.markdown('<p class="subtitle">Upload your room. Get destroyed.</p>', unsafe_allow_html=True)

uploaded = st.file_uploader("Upload your room photo", type=["jpg", "jpeg", "png"])

intensity = st.select_slider(
    "Intensity",
    options=["Mild 🌶", "Spicy 🌶🌶", "Nuclear 🌶🌶🌶"],
    value="Spicy 🌶🌶"
)

if uploaded:
    image = Image.open(uploaded)
    img_array = np.array(image)

    with st.spinner("Scanning..."):
        results = model(img_array, conf=0.20, iou=0.5)

    class_counts = {}
    for box in results[0].boxes:
        label = model.names[int(box.cls[0])]
        class_counts[label] = class_counts.get(label, 0) + 1

    annotated = results[0].plot()

    col1, col2 = st.columns(2)
    with col1:
        st.image(image, use_container_width=True, caption="Your Room")
    with col2:
        st.image(annotated, channels="BGR", use_container_width=True, caption="What AI sees")

    if class_counts:
        obj_text = ", ".join([f"{c}x {n}" for n, c in class_counts.items()])
        st.markdown(f'<p class="objects-text">Detected: {obj_text}</p>', unsafe_allow_html=True)

    st.markdown('<p class="section-title">🔥 Your Roast</p>', unsafe_allow_html=True)
    with st.spinner("Cooking..."):
        roast, brightness, edge_density, floor_std = get_roast(class_counts, img_array, intensity)

    st.markdown(f'<div class="roast-box">{roast}</div>', unsafe_allow_html=True)

    scores = calculate_scores(class_counts, edge_density, floor_std)
    st.markdown('<p class="section-title">📊 Room Score</p>', unsafe_allow_html=True)

    score_html = '<div class="score-row">'
    for label, score in scores.items():
        color = "#ff4444" if score <= 3 else "#ffaa00" if score <= 6 else "#44ff44"
        score_html += f'''
        <div class="score-card">
            <div class="score-num" style="color:{color}">{score}/10</div>
            <div class="score-label">{label}</div>
        </div>'''
    score_html += '</div>'
    st.markdown(score_html, unsafe_allow_html=True)

    st.markdown('<p class="section-title">📤 Share</p>', unsafe_allow_html=True)
    st.code(share_text(roast, scores), language=None)

    st.markdown('<p class="footer">Roast My Room — because someone had to say it 🔥</p>', unsafe_allow_html=True)