import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from chatbot_config import SYSTEM_PROMPT, MODEL_NAME

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured in the environment.")

client = genai.Client(api_key=api_key)


def is_water_management_question(message: str) -> bool:
    """Lightweight topic gate before sending a request to the LLM."""
    keywords = {
        "water", "watershed", "irrigation", "rainwater", "groundwater",
        "surface water", "water quality", "water conservation", "water resource",
        "water resources", "water supply", "water treatment", "wastewater",
        "sewage", "drainage", "reservoir", "dam", "river", "lake", "aquifer",
        "hydrology", "hydraulic", "flood", "drought", "recharge", "desalination",
        "leakage", "water demand", "water distribution", "stormwater",
        "greywater", "rainwater harvesting", "water pollution", "water scarcity",
        "water management"
    }
    text = message.lower().strip()
    return any(keyword in text for keyword in keywords)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a question."}), 400

    if len(message) > 4000:
        return jsonify({"error": "Please keep your question under 4000 characters."}), 400

    if not is_water_management_question(message):
        return jsonify({
            "reply": (
                "I’m WaterWise AI, a study chatbot focused only on Water Management. "
                "Please ask a question related to water resources, conservation, "
                "irrigation, hydrology, water quality, wastewater, flooding, "
                "groundwater, or another Water Management topic."
            )
        })

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.2,
                "max_output_tokens": 1200,
            },
        )

        reply = (response.text or "").strip()

        if not reply:
            reply = "I couldn't generate an answer. Please try your Water Management question again."

        return jsonify({"reply": reply})

    except Exception:
        return jsonify({
            "error": "The AI service could not process your request right now. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
