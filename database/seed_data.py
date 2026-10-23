"""Synthetic sample-data generator.

The Cricbuzz API gives current-state data, not a bulk history of every innings,
so the performance tables (innings, batting, bowling, fielding) that the 25 SQL
questions need are generated here. Player names are fictional; venue names and
approximate capacities are real. The generator is deterministic for a given
seed, so results are reproducible.
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

TEAMS = [
    (1, "India", "India"), (2, "Australia", "Australia"), (3, "England", "England"),
    (4, "Pakistan", "Pakistan"), (5, "South Africa", "South Africa"),
    (6, "New Zealand", "New Zealand"), (7, "Sri Lanka", "Sri Lanka"),
    (8, "West Indies", "West Indies"),
]

# (id, name, city, country, approximate capacity)
VENUES = [
    (1, "Narendra Modi Stadium", "Ahmedabad", "India", 132000),
    (2, "Eden Gardens", "Kolkata", "India", 66000),
    (3, "Wankhede Stadium", "Mumbai", "India", 33000),
    (4, "Melbourne Cricket Ground", "Melbourne", "Australia", 100024),
    (5, "Sydney Cricket Ground", "Sydney", "Australia", 48000),
    (6, "Lord's", "London", "England", 31100),
    (7, "The Oval", "London", "England", 27500),
    (8, "Gaddafi Stadium", "Lahore", "Pakistan", 34000),
    (9, "National Stadium", "Karachi", "Pakistan", 34228),
    (10, "Newlands", "Cape Town", "South Africa", 25000),
    (11, "Wanderers Stadium", "Johannesburg", "South Africa", 34000),
    (12, "Eden Park", "Auckland", "New Zealand", 50000),
    (13, "R. Premadasa Stadium", "Colombo", "Sri Lanka", 35000),
    (14, "Kensington Oval", "Bridgetown", "West Indies", 28000),
    (15, "Dubai International Stadium", "Dubai", "UAE", 25000),
    (16, "Sheikh Zayed Stadium", "Abu Dhabi", "UAE", 20000),
]

NAMES = {
    1: (["Aarav", "Vihaan", "Rohan", "Kabir", "Ishaan", "Arjun", "Dev", "Neel"],
        ["Verma", "Nair", "Rao", "Mehta", "Kulkarni", "Chauhan", "Bhatt", "Iyer"]),
    2: (["Jack", "Liam", "Cooper", "Mitchell", "Harry", "Lachlan", "Brodie", "Ryan"],
        ["Holloway", "Pritchard", "Fenwick", "Calder", "Tennant", "Whitlock", "Marsden", "Hargrave"]),
    3: (["Oliver", "George", "Harvey", "Archie", "Callum", "Toby", "Edward", "Fraser"],
        ["Ashworth", "Pemberton", "Radcliffe", "Thornley", "Wetherby", "Kingsley", "Aldridge", "Cartwright"]),
    4: (["Imran", "Faisal", "Zubair", "Hamza", "Salman", "Tariq", "Bilal", "Adnan"],
        ["Raza", "Qureshi", "Mirza", "Chaudhry", "Siddiqui", "Hashmi", "Lodhi", "Baig"]),
    5: (["Thabo", "Pieter", "Johan", "Sipho", "Dewald", "Kagiso", "Ruan", "Wian"],
        ["Mokoena", "Van Rooyen", "Botha", "Ndlovu", "Steyl", "Maseko", "Pretorius", "Venter"]),
    6: (["Finn", "Hamish", "Tane", "Kieran", "Rhys", "Nikau", "Callan", "Ewan"],
        ["Marlow", "Tapsell", "Whitaker", "Ngata", "Prendergast", "Hollis", "Brennan", "Kereama"]),
    7: (["Kasun", "Dilan", "Nuwan", "Chamika", "Lahiru", "Pasan", "Sachith", "Ravindu"],
        ["Perera", "Gunasekara", "Wickrama", "Jayasekara", "Madushan", "Dissanayake", "Ranatunge", "Bandara"]),
    8: (["Jerome", "Shamar", "Kemar", "Devon", "Akeem", "Raymon", "Keon", "Dwayne"],
        ["Bascombe", "Holford", "Greaves", "Lashley", "Thorne", "Sealy", "Cottrell", "Joseph"]),
}

ROLE_PLAN = ["Batsman"] * 4 + ["Wicket-keeper"] + ["All-rounder"] * 3 + ["Bowler"] * 6
BAT_STYLES = ["Right-hand bat", "Left-hand bat"]
BOWL_STYLES = ["Right-arm fast", "Right-arm medium", "Left-arm fast",
               "Right-arm offbreak", "Left-arm orthodox", "Legbreak"]

FORMAT_RULES: dict[str, dict[str, Any]] = {
    "T20I": {"overs": 20, "mean_factor": 0.62, "base_sr": 135, "bowler_overs": 4,
             "out_prob": 0.85, "weight": 0.40, "gap": 4},
    "ODI": {"overs": 50, "mean_factor": 1.0, "base_sr": 88, "bowler_overs": 10,
            "out_prob": 0.85, "weight": 0.35, "gap": 4},
    "Test": {"overs": None, "mean_factor": 1.0, "base_sr": 52, "bowler_overs": None,
             "out_prob": 0.92, "weight": 0.25, "gap": 7},
}
ORDINALS = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}
HISTORY_START = date(2020, 1, 1)


def _build_players(rng: random.Random) -> tuple[list[dict], dict[int, dict]]:
    """Create 14 players per team plus hidden skill metadata used by the simulator."""
    players: list[dict] = []
    meta: dict[int, dict] = {}
    player_id = 1001
    skill_by_role = {"Batsman": (38, 5), "Wicket-keeper": (31, 4),
                     "All-rounder": (27, 4), "Bowler": (9, 2.5)}
    for team_id, _name, _country in TEAMS:
        firsts, lasts = NAMES[team_id]
        combos = [(f, l) for f in firsts for l in lasts]
        rng.shuffle(combos)
        for idx, role in enumerate(ROLE_PLAN):
            first, last = combos[idx]
            mean, sd = skill_by_role[role]
            bowls = role in ("Bowler", "All-rounder")
            players.append({
                "player_id": player_id,
                "full_name": f"{first} {last}",
                "team_id": team_id,
                "playing_role": role,
                "batting_style": rng.choice(BAT_STYLES),
                "bowling_style": rng.choice(BOWL_STYLES) if bowls else None,
                "date_of_birth": date(rng.randint(1986, 2003), rng.randint(1, 12),
                                      rng.randint(1, 28)).isoformat(),
            })
            meta[player_id] = {
                "team_id": team_id, "role": role,
                "skill": max(3.0, rng.gauss(mean, sd)),
                "trend": rng.uniform(-0.35, 0.35),
                "bowl_factor": rng.uniform(0.8, 1.2),
                "wicket_weight": rng.uniform(0.6, 1.6) * (0.6 if role == "All-rounder" else 1.0),
            }
            player_id += 1
    return players, meta


def _career_stats(rng: random.Random, players: list[dict]) -> list[dict]:
    """Generate plausible career totals per player per format."""
    rows: list[dict] = []
    fmt_cfg = {
        "Test": dict(matches=(20, 110), avg=(1.0, 1.0), sr=(45, 60), hs=(100, 335),
                     wk=3.2, bavg=(24, 34), econ=(2.6, 3.6)),
        "ODI": dict(matches=(40, 250), avg=(0.9, 1.0), sr=(75, 100), hs=(90, 264),
                    wk=1.6, bavg=(26, 38), econ=(4.3, 5.7)),
        "T20I": dict(matches=(25, 140), avg=(0.6, 0.7), sr=(115, 150), hs=(60, 172),
                     wk=1.1, bavg=(20, 30), econ=(6.8, 8.8)),
    }
    avg_by_role = {"Batsman": (35, 55), "Wicket-keeper": (30, 42),
                   "All-rounder": (25, 38), "Bowler": (8, 20)}
    for p in players:
        role = p["playing_role"]
        formats = list(fmt_cfg)
        if rng.random() < 0.25:
            formats.remove(rng.choice(formats))
        for fmt in formats:
            cfg = fmt_cfg[fmt]
            matches = rng.randint(*cfg["matches"])
            innings = int(matches * rng.uniform(0.82, 0.95))
            base = rng.uniform(*avg_by_role[role])
            bat_avg = round(base * rng.uniform(*cfg["avg"]), 2)
            runs = int(innings * bat_avg * 0.92)
            strength = bat_avg / 40
            centuries = int(innings * 0.06 * strength * (0.6 if fmt == "T20I" else 1))
            fifties = int(innings * 0.15 * strength)
            highest = int(rng.uniform(*cfg["hs"]) * min(1.0, 0.45 + strength / 1.4))
            highest = min(highest, max(runs, 1))
            if role == "Bowler":
                wickets = int(matches * cfg["wk"] * rng.uniform(0.6, 1.4))
            elif role == "All-rounder":
                wickets = int(matches * cfg["wk"] * 0.55 * rng.uniform(0.6, 1.4))
            else:
                wickets = rng.randint(0, 5)
            has_bowling = wickets > 0
            rows.append({
                "player_id": p["player_id"], "match_format": fmt,
                "matches_played": matches, "innings_batted": innings,
                "total_runs": runs, "highest_score": highest,
                "batting_avg": bat_avg, "strike_rate": round(rng.uniform(*cfg["sr"]), 2),
                "centuries": centuries, "fifties": fifties, "total_wickets": wickets,
                "bowling_avg": round(rng.uniform(*cfg["bavg"]), 2) if has_bowling else None,
                "economy_rate": round(rng.uniform(*cfg["econ"]), 2) if has_bowling else None,
            })
    return rows


def _overs_text(balls: int) -> float:
    """Convert a ball count to cricket overs notation (e.g. 112 balls -> 18.4)."""
    return float(f"{balls // 6}.{balls % 6}")


def _batting_rows(rng, xi, fmt, match_date, meta):
    """Simulate one batting innings for a playing XI (list of player ids)."""
    rules = FORMAT_RULES[fmt]
    years = (match_date - HISTORY_START).days / 365.25 - 3.4
    rows = []
    for pos, pid in enumerate(xi, start=1):
        m = meta[pid]
        mean = m["skill"] * rules["mean_factor"] * max(0.4, 1 + m["trend"] * years / 3.4)
        runs = int(min(rng.expovariate(1 / max(mean, 1)), 335 if fmt == "Test" else 200))
        sr = rules["base_sr"] * rng.uniform(0.8, 1.25)
        balls = max(1, round(runs / (sr / 100))) if runs > 0 else rng.randint(1, 9)
        rows.append({"player_id": pid, "position": pos, "runs": runs, "balls": balls,
                     "is_out": rng.random() < rules["out_prob"]})
    if rules["overs"]:  # limited overs: respect the ball limit
        cap, total = rules["overs"] * 6, sum(r["balls"] for r in rows)
        if total > cap:
            k = cap / total
            for r in rows:
                r["runs"], r["balls"] = int(r["runs"] * k), max(1, int(r["balls"] * k))
    for r in rows:
        fours = int(r["runs"] * rng.uniform(0.2, 0.5) / 4)
        sixes = int((r["runs"] - fours * 4) * rng.uniform(0, 0.3) / 6)
        r.update(fours=fours, sixes=sixes, strike_rate=round(100 * r["runs"] / r["balls"], 2))
    _limit_wickets(rows, 10)
    return rows


def _limit_wickets(rows: list[dict], max_wickets: int) -> None:
    """Flip batters to 'not out' until at most ``max_wickets`` have fallen."""
    for r in reversed(rows):
        if sum(x["is_out"] for x in rows) <= max_wickets:
            break
        r["is_out"] = False


def _bowling_rows(rng, bowl_xi, fmt, total_runs, wickets, meta):
    """Distribute an innings' runs and wickets among five bowlers."""
    candidates = [p for p in bowl_xi if meta[p]["role"] in ("Bowler", "All-rounder")]
    chosen = rng.sample(candidates, 5)
    rules = FORMAT_RULES[fmt]
    overs = {p: (rng.randint(10, 30) if fmt == "Test" else rules["bowler_overs"]) for p in chosen}
    taken = {p: 0 for p in chosen}
    for _ in range(wickets):
        taken[rng.choices(chosen, weights=[meta[p]["wicket_weight"] for p in chosen])[0]] += 1
    weights = [overs[p] * meta[p]["bowl_factor"] * rng.uniform(0.8, 1.2) for p in chosen]
    conceded = [int(total_runs * w / sum(weights)) for w in weights]
    conceded[0] += total_runs - sum(conceded)
    return [
        {"player_id": p, "overs": float(overs[p]), "maidens": rng.randint(0, max(0, overs[p] // 6)),
         "runs": conceded[i], "wickets": taken[p], "economy": round(conceded[i] / overs[p], 2)}
        for i, p in enumerate(chosen)
    ]


def _match_plans(rng: random.Random, today: date, target: int) -> list[dict]:
    """Plan series (dates, teams, format) so matches look like real tours."""
    plans: list[dict] = [
        {"start": today - timedelta(days=25), "fmt": "T20I", "n": 5, "upcoming": False},
        {"start": today - timedelta(days=12), "fmt": "ODI", "n": 3, "upcoming": False},
        {"start": today + timedelta(days=3), "fmt": "T20I", "n": 3, "upcoming": True},
    ]
    formats, weights = list(FORMAT_RULES), [FORMAT_RULES[f]["weight"] for f in FORMAT_RULES]
    count = 8
    span = (today - timedelta(days=60) - HISTORY_START).days
    while count < target:
        fmt = rng.choices(formats, weights)[0]
        n = rng.randint(3, 5)
        plans.append({"start": HISTORY_START + timedelta(days=rng.randint(0, span)),
                      "fmt": fmt, "n": n, "upcoming": False})
        count += n
    plans.sort(key=lambda p: p["start"])
    return plans


def generate(seed: int = 42, today: date | None = None, match_target: int = 640) -> dict[str, list[dict]]:
    """Build every table's rows. Returns ``{table_name: [row_dict, ...]}``."""
    rng = random.Random(seed)
    today = today or date.today()
    players, meta = _build_players(rng)
    team_name = {t[0]: t[1] for t in TEAMS}
    team_country = {t[0]: t[2] for t in TEAMS}
    rosters: dict[int, dict[str, list[int]]] = {t[0]: {} for t in TEAMS}
    for p in players:
        rosters[p["team_id"]].setdefault(p["playing_role"], []).append(p["player_id"])
    home_venues = {t[0]: [v[0] for v in VENUES if v[3] == t[2]] for t in TEAMS}
    uae_venues = [v[0] for v in VENUES if v[3] == "UAE"]

    out: dict[str, list[dict]] = {k: [] for k in (
        "teams", "venues", "players", "series", "matches", "innings", "match_players",
        "batting_performances", "bowling_performances", "fielding_performances",
        "player_career_stats")}
    out["teams"] = [{"team_id": i, "team_name": n, "country": c, "team_type": "international"}
                    for i, n, c in TEAMS]
    out["venues"] = [{"venue_id": i, "venue_name": n, "city": c, "country": k, "capacity": cap}
                     for i, n, c, k, cap in VENUES]
    out["players"] = players
    out["player_career_stats"] = _career_stats(rng, players)

    ids = dict(series=1, match=1, innings=1, batting=1, bowling=1, fielding=1)

    def pick_xi(team_id: int) -> list[int]:
        r = rosters[team_id]
        bats = rng.sample(r["Batsman"], 3)
        rng.shuffle(bats)
        return bats + r["Wicket-keeper"] + rng.sample(r["All-rounder"], 2) + rng.sample(r["Bowler"], 5)

    def add_innings(match_id, no, bat_team, bowl_team, bat_rows, bowl_rows_, total, wickets, overs_val):
        iid = ids["innings"]
        ids["innings"] += 1
        out["innings"].append({"innings_id": iid, "match_id": match_id, "innings_no": no,
                               "batting_team_id": bat_team, "bowling_team_id": bowl_team,
                               "total_runs": total, "wickets_lost": wickets, "overs": overs_val})
        for r in bat_rows:
            out["batting_performances"].append({
                "batting_id": ids["batting"], "innings_id": iid, "player_id": r["player_id"],
                "batting_position": r["position"], "runs": r["runs"], "balls_faced": r["balls"],
                "fours": r["fours"], "sixes": r["sixes"], "strike_rate": r["strike_rate"],
                "is_out": r["is_out"]})
            ids["batting"] += 1
        for r in bowl_rows_:
            out["bowling_performances"].append({
                "bowling_id": ids["bowling"], "innings_id": iid, "player_id": r["player_id"],
                "overs": r["overs"], "maidens": r["maidens"], "runs_conceded": r["runs"],
                "wickets": r["wickets"], "economy_rate": r["economy"]})
            ids["bowling"] += 1

    for plan in _match_plans(rng, today, match_target):
        fmt, rules = plan["fmt"], FORMAT_RULES[plan["fmt"]]
        team_a, team_b = rng.sample([t[0] for t in TEAMS], 2)
        neutral = rng.random() < 0.12
        host = team_a if rng.random() < 0.5 else team_b
        venues = uae_venues if neutral else home_venues[host]
        t1, t2 = (team_a, team_b) if neutral else (host, team_b if host == team_a else team_a)
        series_id = ids["series"]
        ids["series"] += 1
        dates = [plan["start"] + timedelta(days=i * rules["gap"]) for i in range(plan["n"])]
        out["series"].append({
            "series_id": series_id,
            "series_name": f"{team_name[t1]} v {team_name[t2]} {fmt} Series {plan['start'].year}",
            "host_country": "UAE" if neutral else team_country[host], "match_type": fmt,
            "start_date": dates[0].isoformat(), "end_date": dates[-1].isoformat(),
            "total_matches_planned": plan["n"]})

        for i, match_date in enumerate(dates, start=1):
            match_id = ids["match"]
            ids["match"] += 1
            venue_id = rng.choice(venues)
            row = {"match_id": match_id, "series_id": series_id,
                   "match_desc": f"{team_name[t1]} vs {team_name[t2]}, {ORDINALS[i]} {fmt}",
                   "match_format": fmt, "team1_id": t1, "team2_id": t2, "venue_id": venue_id,
                   "match_date": match_date.isoformat(), "toss_winner_id": None,
                   "toss_decision": None, "winner_id": None, "victory_margin": None,
                   "victory_type": None, "status": "Upcoming" if plan["upcoming"] else "Completed"}
            out["matches"].append(row)
            if plan["upcoming"]:
                continue

            xi = {t1: pick_xi(t1), t2: pick_xi(t2)}
            for team_id, squad in xi.items():
                for pid in squad:
                    out["match_players"].append({"match_id": match_id, "player_id": pid, "team_id": team_id})
            toss_winner = rng.choice([t1, t2])
            decision = "bowl" if rng.random() < 0.55 else "bat"
            first = toss_winner if decision == "bat" else (t2 if toss_winner == t1 else t1)
            second = t2 if first == t1 else t1
            row.update(toss_winner_id=toss_winner, toss_decision=decision)
            sequence = [first, second] if fmt != "Test" else [first, second, first, second]
            bats = [_batting_rows(rng, xi[team], fmt, match_date, meta) for team in sequence]
            extras = [rng.randint(2, 14) for _ in sequence]
            totals = [sum(r["runs"] for r in rows) + e for rows, e in zip(bats, extras)]

            if fmt == "Test":
                agg_first, agg_second = totals[0] + totals[2], totals[1] + totals[3]
                if agg_second <= agg_first:
                    winner = first
                    margin, vtype = agg_first - agg_second, "runs"
                    if margin == 0:
                        winner, margin = second, None
                if agg_second > agg_first or margin is None:
                    winner, vtype = second, "wickets"
                    _limit_wickets(bats[3], rng.randint(2, 9))
                    margin = 10 - sum(r["is_out"] for r in bats[3])
            else:
                if totals[1] <= totals[0]:
                    if totals[1] == totals[0]:
                        totals[1] += 1
                if totals[1] > totals[0]:
                    winner, vtype = second, "wickets"
                    _limit_wickets(bats[1], rng.randint(2, 9))
                    margin = 10 - sum(r["is_out"] for r in bats[1])
                else:
                    winner, vtype, margin = first, "runs", totals[0] - totals[1]
            row.update(winner_id=winner, victory_margin=margin, victory_type=vtype)

            fielding: dict[int, list[int]] = {}
            for no, (team, rows, total) in enumerate(zip(sequence, bats, totals), start=1):
                opp = t2 if team == t1 else t1
                wickets = sum(r["is_out"] for r in rows)
                bowl = _bowling_rows(rng, xi[opp], fmt, total, wickets, meta)
                innings_overs = (rules["overs"] if rules["overs"]
                                 else float(sum(b["overs"] for b in bowl)))
                add_innings(match_id, no, team, opp, rows, bowl, total, wickets, float(innings_overs))
                keeper = rosters[opp]["Wicket-keeper"][0]
                for r in rows:
                    if not r["is_out"]:
                        continue
                    roll = rng.random()
                    if roll < 0.55:
                        who = rng.choice(xi[opp] + [keeper])
                        fielding.setdefault(who, [0, 0])[0] += 1
                    elif roll < 0.62:
                        fielding.setdefault(keeper, [0, 0])[1] += 1
            for pid, (catches, stumpings) in fielding.items():
                out["fielding_performances"].append({
                    "fielding_id": ids["fielding"], "match_id": match_id, "player_id": pid,
                    "catches": catches, "stumpings": stumpings})
                ids["fielding"] += 1
    return out
