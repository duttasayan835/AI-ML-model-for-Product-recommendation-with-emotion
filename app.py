from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import cv2
from fer import FER
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# CSV file to store emotions
csv_file = 'face_emotions.csv'

# Ensure CSV file exists and has headers if it's empty
if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
    df = pd.DataFrame(columns=["Timestamp", "Emotion"])
    df.to_csv(csv_file, index=False)

# Product recommendations with placeholder image and links
emotion_to_products = {
    "happy": [
        {"name": "Minute Maid Fruit Juice", "image": "/static/images/juice.jpg", "link": "#"},
        {"name": "Chocolate", "image": "/static/images/chocolate.jpg", "link": "#"},
        {"name": "Hoodies", "image": "/static/images/hoodies.jpeg", "link": "#"},
        {"name": "Dress", "image": "/static/images/dress.jpeg", "link": "#"},
        {"name": "Clothing", "image": "/static/images/clothing.jpeg", "link": "#"}
    ],
    "sad": [
        {"name": "Comfort Blanket", "image": "/static/images/blanket.jpg", "link": "#"},
        {"name": "Warm Tea", "image": "/static/images/tea.jpg", "link": "#"},
        {"name": "Inspirational Books", "image": "/static/images/books.jpg", "link": "#"}
    ],
    "angry": [
        {"name": "Stress Ball", "image": "/static/images/stress_ball.jpg", "link": "#"},
        {"name": "Calming Tea", "image": "/static/images/calming_tea.jpg", "link": "#"},
        {"name": "Meditation Books", "image": "/static/images/meditation_books.jpg", "link": "#"},
        {"name": "Water Bottle", "image": "/static/images/water_bottle.jpg", "link": "#"}
    ],
    "surprise": [
        {"name": "Soft Toys", "image": "/static/images/soft_toys.jpg", "link": "#"},
        {"name": "Mobile", "image": "/static/images/mobile.jpg", "link": "#"},
        {"name": "Adventure Gear", "image": "/static/images/adventure_gear.jpg", "link": "#"},
        {"name": "Surprise Box", "image": "/static/images/surprise_box.jpg", "link": "#"},
        {"name": "Handbags", "image": "/static/images/handbags.jpg", "link": "#"}
    ],
    "neutral": [
        {"name": "Earrings", "image": "/static/images/earrings.jpg", "link": "#"},
        {"name": "Watch", "image": "/static/images/watch.jpg", "link": "#"},
        {"name": "Healthy Snacks", "image": "/static/images/healthy_snacks.jpg", "link": "#"},
        {"name": "Soundbox", "image": "/static/images/soundbox.jpg", "link": "#"}
    ],
    "fear": [
        {"name": "Pepper Spray", "image": "/static/images/pepper_spray.jpg", "link": "#"},
        {"name": "Safety Kit", "image": "/static/images/safety_kit.jpg", "link": "#"},
        {"name": "Taser", "image": "/static/images/taser.jpg", "link": "#"},
        {"name": "Comfort Food", "image": "/static/images/comfort_food.jpg", "link": "#"},
        {"name": "Stress Relief Kit", "image": "/static/images/stress_relief_kit.jpg", "link": "#"}
    ],
    "disgust": [
        {"name": "Tissue Paper", "image": "/static/images/tissue_paper.jpg", "link": "#"},
        {"name": "Room Freshener", "image": "/static/images/room_freshener.jpg", "link": "#"},
        {"name": "Cleanser", "image": "/static/images/cleanser.jpg", "link": "#"},
        {"name": "Aromatherapy", "image": "/static/images/aromatherapy.jpg", "link": "#"}
    ]
}

def detect_emotion(frame):
    emotion = "Unknown"
    products = []
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detector = FER()
        emotions = detector.detect_emotions(rgb_frame)

        if not emotions:
            print("No emotions detected in the frame")
            return emotion, products

        # Get the most confident emotion
        dominant_emotion = emotions[0]['emotions']
        print("Detected Emotions with Confidence:", dominant_emotion)  # Debug print

        # Define thresholds for better differentiation
        thresholds = {
            'happy': 0.3,
            'angry': 0.3,
            'sad': 0.3,
            'disgust': 0.3,
            'surprise': 0.3,
            'fear': 0.3,
            'neutral': 0.3
        }

        # Extract the emotion with the highest confidence
        emotion = max(dominant_emotion, key=dominant_emotion.get)
        confidence = dominant_emotion[emotion]

        # Apply emotion-specific thresholds
        if confidence > thresholds.get(emotion, 0.3):  # Default threshold is 0.3
            products = emotion_to_products.get(emotion, [{"name": "No products available", "image": "", "link": ""}])
        else:
            emotion = "Low Confidence"  # Label for low confidence detection
    except Exception as e:
        print(f"Error analyzing frame: {e}")
    return emotion, products

@app.route('/detect_emotion', methods=['POST'])
def detect_emotion_route():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file found"}), 400

        file = request.files['image'].read()
        np_img = np.frombuffer(file, np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        emotion, products = detect_emotion(frame)
        if emotion == "Unknown" or emotion == "Low Confidence":
            return jsonify({"error": "No dominant emotion detected or low confidence"}), 400

        df = pd.read_csv(csv_file)

        new_row = pd.DataFrame({
            "Timestamp": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            "Emotion": [emotion]
        })

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(csv_file, index=False)

        return jsonify({"emotion": emotion, "products": products})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_emotions', methods=['GET'])
def get_emotions():
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        df = pd.read_csv(csv_file)
        return df.to_json(orient='records')
    else:
        return jsonify({"message": "No data available"}), 404

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
