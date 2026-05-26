# Tourist Place Recommendation System

AI mini project using:

- Frontend: HTML + CSS
- Backend: Python Flask
- Database: CSV
- Logic: Python IF-ELSE expert rules

## Run

If Python is not installed on your computer, install it first from:

```text
https://www.python.org/downloads/
```

Then open this project folder in the terminal and run:

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Test Inputs

| Climate | Budget | Type | Season | Activity | Expected |
|---|---|---|---|---|---|
| Cold | Medium | Hill Station | Winter | Adventure | Manali |
| Hot | Medium | Beach | Winter | Relaxation | Goa |
| Hot | Low | Historical | Winter | Culture | Jaipur |
| Moderate | Low | Religious | Winter | Spiritual | Varanasi |
| Moderate | Medium | Adventure | Summer | Adventure | Rishikesh |

## Database Fields

The `places.csv` file stores:

- Place name
- Climate
- Budget
- Place type
- Best season
- Main activity
- Usual cost range
- Visitor feedback
- Image URL
- Short description

The cost ranges are approximate project values for demonstration. Real travel cost can change based on city of departure, hotel type, transport, food, season, and number of days.

## Images

The webpage uses cropped local images from the Incredible India collage. They are stored in:

```text
static/images/destinations/
```

Each place has its own small JPG image, for example:

```text
static/images/destinations/goa.jpg
static/images/destinations/manali.jpg
static/images/destinations/jaipur.jpg
```
