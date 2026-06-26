# 🔥 Roast My Room

Upload a photo of your room and let AI judge your life choices.

## Live Demo
👉 [Try it here](https://ayushzoro0092-roast-my-room.hf.space)

## What it does
- Detects objects in your room using YOLOv8
- Analyzes mess level, clutter, lighting using OpenCV
- Generates a savage roast using Google Gemini AI
- Gives your room a score across Hygiene, Social Life, Life Choices and Chaos
- Shareable roast text to send to friends

## Tech Stack
- YOLOv8 (Ultralytics) — object detection
- OpenCV — room analysis
- Google Gemini API — roast generation
- Streamlit — web UI
- Docker — containerization
- Hugging Face Spaces — deployment

## Run locally
```bash
git clone https://github.com/ZoroAyush/roast-my-room
cd roast-my-room
pip install -r requirements.txt
streamlit run app.py
```