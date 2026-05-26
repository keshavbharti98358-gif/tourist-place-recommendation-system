from csv import DictReader
from html import escape
from pathlib import Path
from random import sample

from flask import Response, Flask, jsonify, render_template, request


app = Flask(__name__)
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "places.csv"

TYPE_THEMES = {
    "Beach": ("#0ea5e9", "#facc15", "BEACH"),
    "Hill Station": ("#2563eb", "#dbeafe", "HILLS"),
    "Historical": ("#b45309", "#fde68a", "HERITAGE"),
    "Nature": ("#15803d", "#bbf7d0", "NATURE"),
    "Adventure": ("#7c2d12", "#fed7aa", "ADVENTURE"),
    "Religious": ("#6d28d9", "#ede9fe", "SPIRITUAL"),
}

IMAGE_BY_TYPE = {
    "Beach": "images/beach.svg",
    "Hill Station": "images/hills.svg",
    "Adventure": "images/hills.svg",
    "Historical": "images/heritage.svg",
    "Religious": "images/heritage.svg",
    "Nature": "images/nature.svg",
}

CARD_THEME_BY_TYPE = {
    "Beach": "theme-beach",
    "Hill Station": "theme-hills",
    "Adventure": "theme-adventure",
    "Historical": "theme-heritage",
    "Religious": "theme-spiritual",
    "Nature": "theme-nature",
}

PLACE_EXTRAS = {
    "Goa": {
        "rating": 4.7,
        "popularity": 98,
        "attractions": ["Baga Beach", "Fort Aguada", "Dudhsagar Falls"],
        "hotels": ["Sea Breeze Resort", "Casa Beachfront", "Goa Heritage Inn"],
    },
    "Manali": {
        "rating": 4.6,
        "popularity": 94,
        "attractions": ["Solang Valley", "Hadimba Temple", "Rohtang Pass"],
        "hotels": ["Snow Peak Retreat", "Valley View Lodge", "Himalayan Nest"],
    },
    "Kerala": {
        "rating": 4.8,
        "popularity": 96,
        "attractions": ["Alleppey Backwaters", "Munnar Tea Gardens", "Kumarakom"],
        "hotels": ["Backwater Bay Resort", "Green Leaf Stay", "Coconut Grove Hotel"],
    },
    "Andaman": {
        "rating": 4.9,
        "popularity": 91,
        "attractions": ["Radhanagar Beach", "Cellular Jail", "Neil Island"],
        "hotels": ["Island Coral Resort", "Blue Lagoon Stay", "Harbor View Hotel"],
    },
}

BUDGET_RANK = {"Low": 1, "Medium": 2, "High": 3}

FILTER_OPTIONS = {
    "budget": ["Low", "Medium", "High"],
    "climate": ["Hot", "Cold", "Moderate"],
    "type": ["Beach", "Hill Station", "Historical", "Nature", "Adventure", "Religious"],
    "season": ["Summer", "Winter", "Monsoon"],
    "activity": ["Relaxation", "Adventure", "Culture", "Nature", "Spiritual"],
    "sort": [
        ("best_match", "Best Match"),
        ("lowest_budget", "Lowest Budget"),
        ("popular", "Most Popular"),
        ("climate", "Best Climate Match"),
    ],
}


def image_for_place(place):
    slug = place["place"].lower().replace(" ", "-")
    destination_image = BASE_DIR / "static" / "images" / "destinations" / f"{slug}.jpg"
    if destination_image.exists():
        return f"images/destinations/{slug}.jpg"
    return IMAGE_BY_TYPE.get(place["type"], "images/nature.svg")


def load_places():
    """Read tourist places from the CSV database."""
    with DATA_FILE.open("r", encoding="utf-8", newline="") as file:
        places = []
        for place in DictReader(file):
            place = enrich_place(dict(place))
            places.append(place)
        return places


def enrich_place(place):
    extras = PLACE_EXTRAS.get(place["place"], {})
    place["image_file"] = image_for_place(place)
    place["card_theme"] = CARD_THEME_BY_TYPE.get(place["type"], "theme-nature")
    place["rating"] = extras.get("rating", 4.3)
    place["popularity"] = extras.get("popularity", 80)
    place["attractions"] = extras.get(
        "attractions",
        [f"{place['place']} viewpoint", "Local market", "City heritage walk"],
    )
    place["hotels"] = extras.get(
        "hotels",
        [f"{place['place']} Comfort Stay", "Travelers Inn", "Central Residency"],
    )
    place["budget_rank"] = BUDGET_RANK.get(place["budget"], 2)
    return place


def apply_expert_rules(user_input, place):
    """Return a matching score and explanation for one tourist place."""
    score = 0
    reasons = []

    if place["climate"] == user_input["climate"]:
        score += 1
        reasons.append("climate matches")

    if place["budget"] == user_input["budget"]:
        score += 1
        reasons.append("budget matches")

    if place["type"] == user_input["type"]:
        score += 1
        reasons.append("place type matches")

    if place["season"] == user_input["season"]:
        score += 1
        reasons.append("season matches")

    if place["activity"] == user_input["activity"]:
        score += 1
        reasons.append("activity matches")

    # Extra expert rules make the system feel more like a real rule engine.
    if user_input["type"] == "Hill Station" and user_input["climate"] == "Cold" and place["type"] == "Hill Station":
        score += 2
        reasons.append("expert rule: cold hill-station preference")

    if user_input["type"] == "Beach" and user_input["activity"] == "Relaxation" and place["type"] == "Beach":
        score += 2
        reasons.append("expert rule: beach relaxation preference")

    if user_input["type"] == "Historical" and user_input["activity"] == "Culture" and place["type"] == "Historical":
        score += 2
        reasons.append("expert rule: historical culture preference")

    if user_input["activity"] == "Adventure" and place["activity"] == "Adventure":
        score += 2
        reasons.append("expert rule: adventure activity preference")

    if user_input["type"] == "Religious" and user_input["activity"] == "Spiritual" and place["type"] == "Religious":
        score += 2
        reasons.append("expert rule: spiritual travel preference")

    return score, reasons


def recommend_places(user_input):
    recommendations = []

    for place in load_places():
        score, reasons = apply_expert_rules(user_input, place)
        if score > 0:
            match_percent = min(98, 55 + (score * 6))
            recommendations.append(
                {
                    "place": place,
                    "score": score,
                    "match_percent": match_percent,
                    "reasons": reasons,
                }
            )

    sort_recommendations(recommendations, user_input.get("sort", "best_match"), user_input)
    return recommendations[:5]


def sort_recommendations(recommendations, sort_by, user_input):
    if sort_by == "lowest_budget":
        recommendations.sort(key=lambda item: (item["place"]["budget_rank"], -item["match_percent"]))
    elif sort_by == "popular":
        recommendations.sort(key=lambda item: (item["place"]["popularity"], item["match_percent"]), reverse=True)
    elif sort_by == "climate":
        recommendations.sort(
            key=lambda item: (
                item["place"]["climate"] == user_input["climate"],
                item["match_percent"],
                item["place"]["popularity"],
            ),
            reverse=True,
        )
    else:
        recommendations.sort(
            key=lambda item: (
                item["score"],
                item["place"]["type"] == user_input["type"],
                item["place"]["activity"] == user_input["activity"],
                item["place"]["budget"] == user_input["budget"],
            ),
            reverse=True,
        )


def find_place(place_name):
    for place in load_places():
        if place["place"].lower() == place_name.lower():
            return place
    return None


@app.route("/")
def home():
    places = load_places()
    featured_places = sample(places, min(4, len(places)))
    return render_template("index.html", places=places, featured_places=featured_places)


@app.route("/place-image/<place_name>")
def place_image(place_name):
    place = find_place(place_name)
    place_type = place["type"] if place else "Tourism"
    title = place["place"] if place else place_name
    primary, secondary, label = TYPE_THEMES.get(place_type, ("#2563eb", "#dbeafe", "TRAVEL"))

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="520" viewBox="0 0 800 520">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="{primary}"/>
      <stop offset="100%" stop-color="{secondary}"/>
    </linearGradient>
  </defs>
  <rect width="800" height="520" fill="url(#bg)"/>
  <circle cx="650" cy="105" r="70" fill="rgba(255,255,255,0.45)"/>
  <path d="M0 390 C150 320 250 350 380 295 C520 235 650 310 800 235 L800 520 L0 520 Z" fill="rgba(255,255,255,0.35)"/>
  <path d="M0 430 C180 370 330 420 470 350 C610 285 700 360 800 315 L800 520 L0 520 Z" fill="rgba(255,255,255,0.55)"/>
  <rect x="46" y="46" width="708" height="428" rx="24" fill="rgba(255,255,255,0.14)" stroke="rgba(255,255,255,0.45)" stroke-width="2"/>
  <text x="70" y="115" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#ffffff" letter-spacing="4">{escape(label)}</text>
  <text x="70" y="255" font-family="Arial, sans-serif" font-size="72" font-weight="700" fill="#ffffff">{escape(title)}</text>
  <text x="74" y="315" font-family="Arial, sans-serif" font-size="30" fill="rgba(255,255,255,0.92)">{escape(place_type)} Destination</text>
</svg>
"""
    return Response(svg, mimetype="image/svg+xml")


@app.route("/recommend", methods=["POST"])
def recommend():
    user_input = {
        "budget": request.form["budget"],
        "climate": request.form["climate"],
        "type": request.form["type"],
        "season": request.form["season"],
        "activity": request.form["activity"],
        "sort": request.form.get("sort", "best_match"),
    }
    recommendations = recommend_places(user_input)
    return render_template(
        "result.html",
        user_input=user_input,
        recommendations=recommendations,
        filter_options=FILTER_OPTIONS,
    )


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json(silent=True) or request.form
    user_input = {
        "budget": data.get("budget", "Medium"),
        "climate": data.get("climate", "Moderate"),
        "type": data.get("type", "Beach"),
        "season": data.get("season", "Winter"),
        "activity": data.get("activity", "Relaxation"),
        "sort": data.get("sort", "best_match"),
    }
    return jsonify(
        {
            "user_input": user_input,
            "recommendations": recommend_places(user_input),
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
