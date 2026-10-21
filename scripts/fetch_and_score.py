import argparse, csv, json, math, time
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
ORIGIN_NAME = "Lyon"
ORIGIN_LAT, ORIGIN_LON = 45.7640, 4.8357
EMISSIONS_FACTOR_KG_PER_KM = 0.15  # Hypothese pedagogique du TP, non validee pour un bilan reel

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

def fetch_weather_batch(lats, lons, retries=4, backoff=5):
    """One request for every destination at once, instead of one connection per
    capital. This isn't just fewer lines -- it fixes a real failure mode: 26
    separate TLS handshakes from a shared GitHub Actions runner IP is 26 separate
    chances for a connection to hang or get throttled, and in testing it reliably
    failed partway through (a handful of capitals fetched fine, then the rest
    started timing out on every retry). One request means one connection, and it
    is also roughly 100x faster in practice (all 26 forecasts typically arrive in
    well under a second)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": ",".join(str(v) for v in lats),
        "longitude": ",".join(str(v) for v in lons),
        "daily": "temperature_2m_max,precipitation_sum,sunshine_duration",
        "timezone": "auto", "forecast_days": 7,
    }
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            with urlopen(url + "?" + urlencode(params), timeout=45) as response:
                data = json.load(response)
            return data if isinstance(data, list) else [data]
        except (URLError, TimeoutError, OSError, ValueError) as e:
            last_error = e
            print(f"  batch weather fetch attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(backoff * attempt)
    raise RuntimeError(f"Open-Meteo unreachable after {retries} attempts") from last_error

def normalize(values, invert=False):
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.5 for _ in values]
    scaled = [(v - lo) / (hi - lo) for v in values]
    return [1 - s for s in scaled] if invert else scaled

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", choices=["Lyon", "Paris"], default=ORIGIN_NAME)
    parser.add_argument("--output", default="docs/data/rankings.json")
    args = parser.parse_args()
    origin_lat, origin_lon = (48.8566, 2.3522) if args.origin == "Paris" else (ORIGIN_LAT, ORIGIN_LON)
    with open(ROOT / "data/capitals.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    dest_rows = [row for row in rows if row["capital"] != args.origin]
    lats = [float(row["lat"]) for row in dest_rows]
    lons = [float(row["lon"]) for row in dest_rows]

    print(f"Fetching weather for {len(dest_rows)} capitals in a single batched request...")
    weather = fetch_weather_batch(lats, lons)
    if len(weather) != len(dest_rows):
        raise RuntimeError(
            f"Open-Meteo returned {len(weather)} results for {len(dest_rows)} "
            "requested locations -- refusing to guess the pairing."
        )
    print(f"Received {len(weather)} results")

    destinations = []
    for row, lat, lon, wx in zip(dest_rows, lats, lons, weather):
        distance_km = haversine_km(origin_lat, origin_lon, lat, lon)
        daily = wx["daily"]
        dates = daily.get("time", [])
        if len(dates) != 7:
            raise ValueError(f"Expected seven forecast days for {row['capital']}")
        for key in ("temperature_2m_max", "precipitation_sum", "sunshine_duration"):
            values = daily.get(key, [])
            if len(values) != 7 or any(not isinstance(v, (float, int)) or not math.isfinite(v) for v in values):
                raise ValueError(f"Incomplete weather data: {row['capital']} / {key}")
        if any(v < 0 for key in ("precipitation_sum", "sunshine_duration") for v in daily[key]):
            raise ValueError("Negative rain or sunshine")
        avg_temp = sum(daily["temperature_2m_max"]) / len(daily["temperature_2m_max"])
        total_precip = sum(daily["precipitation_sum"])
        avg_sunshine = sum(daily["sunshine_duration"]) / len(daily["sunshine_duration"])
        destinations.append({
            "country": row["country"], "capital": row["capital"],
            "forecast_start": dates[0], "forecast_end": dates[-1],
            "lat": lat, "lon": lon,
            "distance_km": round(distance_km, 1),
            "co2_kg_roundtrip": round(2 * distance_km * EMISSIONS_FACTOR_KG_PER_KM, 1),
            "avg_max_temp": round(avg_temp, 1),
            "total_precip_mm": round(total_precip, 1),
            "avg_sunshine_s": round(avg_sunshine, 0),
        })

    temp_scores = normalize([d["avg_max_temp"] for d in destinations])
    sun_scores = normalize([d["avg_sunshine_s"] for d in destinations])
    rain_scores = normalize([d["total_precip_mm"] for d in destinations], invert=True)
    co2_scores = normalize([d["co2_kg_roundtrip"] for d in destinations], invert=True)

    for d, t, s, rn, c in zip(destinations, temp_scores, sun_scores, rain_scores, co2_scores):
        d["weather_score"] = round((t + s + rn) / 3, 3)
        d["co2_score"] = round(c, 3)
        d["final_score"] = round((d["weather_score"] + d["co2_score"]) / 2, 3)

    destinations.sort(key=lambda d: d["final_score"], reverse=True)

    output = {
        "origin": {"name": args.origin, "lat": origin_lat, "lon": origin_lon},
        "weather_source": "https://open-meteo.com/",
        "forecast_definition": "Seven days starting on collection day, local destination time",
        "weights": {"weather": 0.5, "co2": 0.5},
        "emissions_factor_status": "Teaching assumption from TD1, not independently validated",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "emissions_factor_kg_per_km": EMISSIONS_FACTOR_KG_PER_KM,
        "destinations": destinations,
    }
    path = ROOT / args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)
    print(f"Wrote {len(destinations)} destinations to {path}; winner: {destinations[0]['capital']}")

if __name__ == "__main__":
    main()
