import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "travelsfear-dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///travelsfear.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    budget = db.Column(db.Float, default=0)
    preferences = db.Column(db.String(300), default="")
    favourites = db.relationship("Favourite", backref="user", lazy=True)

class TouristPlace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(500), default="")

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    cuisine = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, default=0)
    rating = db.Column(db.Float, default=0)
    image = db.Column(db.String(500), default="")

class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey("tourist_place.id"), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey("tourist_place.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_data():
    if TouristPlace.query.count() == 0:
        places = [
            TouristPlace(name="Fort Kochi", location="Kochi", category="Heritage",
                         description="Historic streets, colonial buildings and the famous Chinese fishing nets.",
                         image="/static/images/fortkochi.jpg"),
            TouristPlace(name="Munnar", location="Idukki", category="Nature",
                         description="Hill station known for tea gardens, misty mountains and scenic viewpoints.",
image="/static/images/munnar.jpg"),
            TouristPlace(name="Alappuzha Backwaters", location="Alappuzha", category="Backwaters",
                         description="Relaxing backwater experiences, houseboats and beautiful village scenery.",
                         image="https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=900&q=80"),
            TouristPlace(name="Varkala Cliff", location="Varkala", category="Beach",
                         description="A dramatic coastal cliff overlooking the Arabian Sea with a lively promenade.",
image="/static/images/varkala.jpg"),
            TouristPlace(name="Wayanad", location="Wayanad", category="Adventure",
                         description="Forests, waterfalls, caves and outdoor activities in Kerala's highlands.",
image="/static/images/wayanad.jpg"),
            TouristPlace(name="Athirappilly Waterfalls", location="Thrissur", category="Waterfall",
                         description="One of Kerala's best-known waterfalls surrounded by lush forest.",
image="/static/images/athirappilly.jpg")
        ]
        db.session.add_all(places)

    if Restaurant.query.count() == 0:
        restaurants = [
            Restaurant(name="Kochi Kitchen", location="Fort Kochi", cuisine="Kerala",
                       price=350, rating=4.5,
                       image="https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=80"),
            Restaurant(name="Malabar Spice", location="Kochi", cuisine="Indian",
                       price=450, rating=4.4,
                       image="https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=900&q=80"),
            Restaurant(name="Green Leaf Cafe", location="Munnar", cuisine="Vegetarian",
                       price=300, rating=4.3,
                       image="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80"),
            Restaurant(name="Coastal Bites", location="Varkala", cuisine="Seafood",
                       price=500, rating=4.6,
                       image="https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=900&q=80")
        ]
        db.session.add_all(restaurants)
    db.session.commit()

@app.context_processor
def inject_user():
    return {"current_user": User.query.get(session["user_id"]) if session.get("user_id") else None}

@app.route("/")
def home():
    places = TouristPlace.query.limit(6).all()
    restaurants = Restaurant.query.limit(4).all()
    return render_template("index.html", places=places, restaurants=restaurants)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or not password:
            flash("Please fill all fields.", "danger")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "warning")
            return redirect(url_for("login"))
        user = User(name=name, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Welcome to TravelSfear!", "success")
            return redirect(url_for("home"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/places")
def places():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    query = TouristPlace.query
    if q:
        query = query.filter(
            db.or_(TouristPlace.name.ilike(f"%{q}%"),
                   TouristPlace.location.ilike(f"%{q}%"))
        )
    if category:
        query = query.filter_by(category=category)
    return render_template("places.html", places=query.all(), q=q, category=category)

@app.route("/restaurants")
def restaurants():
    q = request.args.get("q", "").strip()
    cuisine = request.args.get("cuisine", "").strip()
    query = Restaurant.query
    if q:
        query = query.filter(
            db.or_(Restaurant.name.ilike(f"%{q}%"),
                   Restaurant.location.ilike(f"%{q}%"))
        )
    if cuisine:
        query = query.filter_by(cuisine=cuisine)
    return render_template("restaurants.html", restaurants=query.all(), q=q, cuisine=cuisine)

@app.route("/favourite/<int:place_id>", methods=["POST"])
def favourite(place_id):
    if not session.get("user_id"):
        flash("Please login to save favourites.", "warning")
        return redirect(url_for("login"))
    existing = Favourite.query.filter_by(
        user_id=session["user_id"], place_id=place_id
    ).first()
    if existing:
        db.session.delete(existing)
        flash("Removed from favourites.", "info")
    else:
        db.session.add(Favourite(user_id=session["user_id"], place_id=place_id))
        flash("Added to favourites.", "success")
    db.session.commit()
    return redirect(request.referrer or url_for("places"))

@app.route("/favourites")
def favourites():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    items = Favourite.query.filter_by(user_id=session["user_id"]).all()
    place_ids = [x.place_id for x in items]
    saved = TouristPlace.query.filter(TouristPlace.id.in_(place_ids)).all() if place_ids else []
    return render_template("favourites.html", places=saved)

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"reply": "Please type a question."}), 400

    # Demo rule-based assistant. Replace this function with OpenAI/Gemini
    # after adding your API key to .env.
    text = message.lower()
    if "restaurant" in text:
        reply = "Tell me your location, cuisine and budget. Example: vegetarian restaurant under ₹500 near Fort Kochi."
    elif "munnar" in text:
        reply = "Munnar is a hill destination known for tea gardens, viewpoints and cool weather."
    elif "emergency" in text:
        reply = "For emergencies in India, call 112. Ambulance: 108. Fire & Rescue: 101."
    elif "uber" in text or "taxi" in text:
        reply = "You can use the Uber app for rides. A production version can connect an approved ride-booking API."
    elif "weather" in text:
        reply = "Use the Weather page and enter a Kerala city to get live weather when a weather API key is configured."
    else:
        reply = "I can help with Kerala tourist places, restaurants, routes, weather, emergency contacts and travel planning."
    return jsonify({"reply": reply})

@app.route("/weather")
def weather():
    return render_template("weather.html")

@app.route("/api/weather")
def api_weather():
    city = request.args.get("city", "Kochi").strip()
    # Demo fallback. Add OPENWEATHER_API_KEY in .env for live data.
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key:
        return jsonify({
            "city": city,
            "temperature": "--",
            "description": "Add OPENWEATHER_API_KEY to .env for live weather.",
            "demo": True
        })
    import requests
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": key, "units": "metric"},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        return jsonify({
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        })
    except Exception:
        return jsonify({"error": "Could not fetch weather."}), 502

@app.route("/emergency")
def emergency():
    contacts = [
        ("National Emergency", "112"),
        ("Police", "100"),
        ("Ambulance", "108"),
        ("Fire & Rescue", "101"),
        ("Women Helpline", "181")
    ]
    return render_template("emergency.html", contacts=contacts)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        user.name = request.form.get("name", user.name)
        user.budget = float(request.form.get("budget") or 0)
        user.preferences = request.form.get("preferences", "")
        db.session.commit()
        flash("Profile updated.", "success")
    return render_template("profile.html", user=user)

# JSON API endpoints for frontend/mobile-app integration
@app.route("/api/places")
def api_places():
    return jsonify([{
        "id": p.id, "name": p.name, "location": p.location,
        "category": p.category, "description": p.description, "image": p.image
    } for p in TouristPlace.query.all()])

@app.route("/api/restaurants")
def api_restaurants():
    return jsonify([{
        "id": r.id, "name": r.name, "location": r.location,
        "cuisine": r.cuisine, "price": r.price, "rating": r.rating, "image": r.image
    } for r in Restaurant.query.all()])

@app.route("/api/emergency")
def api_emergency():
    return jsonify([
        {"service": "National Emergency", "number": "112"},
        {"service": "Police", "number": "100"},
        {"service": "Ambulance", "number": "108"},
        {"service": "Fire & Rescue", "number": "101"},
        {"service": "Women Helpline", "number": "181"}
    ])

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    app.run(debug=True)
