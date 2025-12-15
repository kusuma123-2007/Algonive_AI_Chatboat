from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

# -----------------------------
# 1. PREDEFINED FAQ RESPONSES
# -----------------------------
FAQ_RESPONSES = {
    "working hours": "Our customer support is available 24/7.",
    "return policy": "You can return any product within 30 days of delivery.",
    "reset password": "To reset your password, go to Settings > Account > Reset Password.",
    "contact": "You can contact us at support@example.com or call +1-234-567-890."
}

# -----------------------------
# 2. MOCK DATABASE / API DATA
# -----------------------------
MOCK_ORDERS = {
    "1234": "Delivered on 25-11-2025",
    "5678": "Out for delivery. Expected today.",
    "9999": "Order confirmed. Preparing for dispatch."
}


# -----------------------------
# 3. SIMPLE NLP: INTENT DETECTION
# -----------------------------
def detect_intent(message: str):
    """
    Very simple rule-based intent detection.
    Returns: intent (str), entities (dict)
    """
    msg = message.lower()

    # Intent: track_order
    if "track" in msg and "order" in msg:
        return "track_order", extract_order_id(msg)

    # Intent: faq (based on keywords)
    faq_keywords = ["working hours", "timings", "return policy", "refund", "reset password", "forgot password", "contact", "email", "phone"]
    for kw in faq_keywords:
        if kw in msg:
            return "faq", {"keyword": kw}

    # Intent: greeting
    if any(word in msg for word in ["hi", "hello", "hey"]):
        return "greeting", {}

    # Fallback
    return "unknown", {}


def extract_order_id(message: str):
    """
    Extracts an order ID from the message (any number in the text).
    """
    numbers = re.findall(r"\d+", message)
    if numbers:
        return {"order_id": numbers[0]}
    return {}


# -----------------------------
# 4. HANDLERS FOR INTENTS
# -----------------------------
def handle_faq(entities):
    keyword = entities.get("keyword", "").lower()

    # Map common phrases to our FAQ keys
    if "timings" in keyword or "working hours" in keyword:
        key = "working hours"
    elif "return policy" in keyword or "refund" in keyword:
        key = "return policy"
    elif "reset password" in keyword or "forgot password" in keyword:
        key = "reset password"
    elif "contact" in keyword or "email" in keyword or "phone" in keyword:
        key = "contact"
    else:
        key = keyword

    answer = FAQ_RESPONSES.get(key)
    if answer:
        return answer
    else:
        return "I'm sorry, I don't have information about that yet."


def handle_track_order(entities):
    order_id = entities.get("order_id")
    if not order_id:
        return "Please provide your order ID to track your order."

    # Simulate API call by looking up in MOCK_ORDERS
    status = MOCK_ORDERS.get(order_id)
    if status:
        return f"Your order {order_id} status: {status}"
    else:
        return f"I could not find any details for order ID {order_id}. Please check the ID and try again."


def handle_greeting():
    return "Hello! 👋 I am your AI support assistant. How can I help you today?"


def handle_ai_fallback(message: str):
    """
    Simple 'AI-like' fallback when no intent matched.
    In a real project, this could call an LLM API.
    """
    return (
        "I'm not entirely sure about that yet 🤔, "
        "but I'll note this question for improvement. "
        "Meanwhile, could you rephrase or ask about orders, returns, or account support?"
    )


# -----------------------------
# 5. MAIN CHAT LOGIC
# -----------------------------
def generate_bot_response(user_message: str) -> str:
    intent, entities = detect_intent(user_message)

    if intent == "faq":
        return handle_faq(entities)
    elif intent == "track_order":
        return handle_track_order(entities)
    elif intent == "greeting":
        return handle_greeting()
    elif intent == "unknown":
        return handle_ai_fallback(user_message)
    else:
        return "Sorry, I couldn't understand that. Can you please rephrase?"


# -----------------------------
# 6. FLASK ROUTES
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return jsonify({"reply": "Please type a message so I can help you."})

    bot_reply = generate_bot_response(user_message)
    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    app.run(debug=True)
