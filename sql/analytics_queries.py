"""The 25 SQL practice questions (plus 22b) as a registry.

Dialect notes (written for SQLite, the default database):
  * ``date('now', '-30 days')`` / ``strftime`` are SQLite date functions.
    MySQL: ``CURDATE() - INTERVAL 30 DAY`` / ``YEAR()``.
    PostgreSQL: ``CURRENT_DATE - INTERVAL '30 days'`` / ``EXTRACT(YEAR FROM ...)``.
  * Standard deviation uses ``SQRT(AVG(x*x) - AVG(x)*AVG(x))`` (population SD);
    on MySQL/PostgreSQL use ``STDDEV_POP(x)``.
  * ``MIN(a, b)`` / ``MAX(a, b)`` with two arguments is SQLite; use
    ``LEAST`` / ``GREATEST`` elsewhere.
"""
from __future__ import annotations

QUERIES: list[dict] = [
    # ------------------------------------------------------------------ BEGINNER
    {"id": "Q1", "level": "Beginner", "title": "Players who represent India",
     "description": "Full name, playing role, batting style and bowling style of every Indian player.",
     "sql": """
SELECT p.full_name, p.playing_role, p.batting_style, p.bowling_style
FROM players p
JOIN teams t ON t.team_id = p.team_id
WHERE t.team_name = 'India'
ORDER BY p.full_name;"""},
    {"id": "Q2", "level": "Beginner", "title": "Matches played in the last 30 days",
     "description": "Description, both teams, venue with city and date; most recent first.",
     "sql": """
SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
       v.venue_name || ', ' || v.city AS venue, m.match_date
FROM matches m
JOIN teams t1 ON t1.team_id = m.team1_id
JOIN teams t2 ON t2.team_id = m.team2_id
LEFT JOIN venues v ON v.venue_id = m.venue_id
WHERE m.match_date >= date('now', '-30 days')
  AND m.match_date <= date('now')
ORDER BY m.match_date DESC;"""},
    {"id": "Q3", "level": "Beginner", "title": "Top 10 ODI run scorers",
     "description": "Player, total runs, batting average and centuries; highest scorer first.",
     "sql": """
SELECT p.full_name, c.total_runs, c.batting_avg, c.centuries
FROM player_career_stats c
JOIN players p ON p.player_id = c.player_id
WHERE c.match_format = 'ODI'
ORDER BY c.total_runs DESC
LIMIT 10;"""},
    {"id": "Q4", "level": "Beginner", "title": "Venues with capacity above 50,000",
     "description": "Venue, city, country and capacity; largest first.",
     "sql": """
SELECT venue_name, city, country, capacity
FROM venues
WHERE capacity > 50000
ORDER BY capacity DESC;"""},
    {"id": "Q5", "level": "Beginner", "title": "Matches won by each team",
     "description": "Total wins per team, most wins first.",
     "sql": """
SELECT t.team_name, COUNT(*) AS total_wins
FROM matches m
JOIN teams t ON t.team_id = m.winner_id
WHERE m.status = 'Completed'
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC;"""},
    {"id": "Q6", "level": "Beginner", "title": "Players per playing role",
     "description": "Count of players in each role.",
     "sql": """
SELECT playing_role, COUNT(*) AS player_count
FROM players
GROUP BY playing_role
ORDER BY player_count DESC;"""},
    {"id": "Q7", "level": "Beginner", "title": "Highest individual score per format",
     "description": "Highest score recorded in Test, ODI and T20I.",
     "sql": """
SELECT match_format, MAX(highest_score) AS highest_score
FROM player_career_stats
GROUP BY match_format
ORDER BY highest_score DESC;"""},
    {"id": "Q8", "level": "Beginner", "title": "Series that started in 2024",
     "description": "Series name, host country, match type, start date and planned matches.",
     "sql": """
SELECT series_name, host_country, match_type, start_date, total_matches_planned
FROM series
WHERE start_date >= '2024-01-01' AND start_date < '2025-01-01'
ORDER BY start_date;"""},
    # -------------------------------------------------------------- INTERMEDIATE
    {"id": "Q9", "level": "Intermediate", "title": "All-rounders with 1000+ runs and 50+ wickets",
     "description": "Per format: all-rounders above both thresholds.",
     "sql": """
SELECT p.full_name, c.total_runs, c.total_wickets, c.match_format
FROM player_career_stats c
JOIN players p ON p.player_id = c.player_id
WHERE p.playing_role = 'All-rounder'
  AND c.total_runs > 1000
  AND c.total_wickets > 50
ORDER BY c.total_runs DESC;"""},
    {"id": "Q10", "level": "Intermediate", "title": "Last 20 completed matches",
     "description": "Teams, winner, margin, victory type and venue; most recent first.",
     "sql": """
SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
       w.team_name AS winning_team, m.victory_margin, m.victory_type, v.venue_name
FROM matches m
JOIN teams t1 ON t1.team_id = m.team1_id
JOIN teams t2 ON t2.team_id = m.team2_id
LEFT JOIN teams w ON w.team_id = m.winner_id
LEFT JOIN venues v ON v.venue_id = m.venue_id
WHERE m.status = 'Completed'
ORDER BY m.match_date DESC, m.match_id DESC
LIMIT 20;"""},
    {"id": "Q11", "level": "Intermediate", "title": "Player performance across formats",
     "description": "For players with 2+ formats: runs per format and weighted overall batting average.",
     "sql": """
SELECT p.full_name,
       SUM(CASE WHEN c.match_format = 'Test' THEN c.total_runs END) AS test_runs,
       SUM(CASE WHEN c.match_format = 'ODI'  THEN c.total_runs END) AS odi_runs,
       SUM(CASE WHEN c.match_format = 'T20I' THEN c.total_runs END) AS t20i_runs,
       ROUND(SUM(c.batting_avg * c.innings_batted) * 1.0
             / NULLIF(SUM(c.innings_batted), 0), 2) AS overall_batting_avg
FROM player_career_stats c
JOIN players p ON p.player_id = c.player_id
WHERE c.matches_played > 0
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT c.match_format) >= 2
ORDER BY overall_batting_avg DESC;"""},
    {"id": "Q12", "level": "Intermediate", "title": "Home vs away performance",
     "description": "A match is 'home' when the venue country equals the team's country.",
     "sql": """
WITH team_matches AS (
    SELECT m.match_id, m.team1_id AS team_id, m.winner_id, v.country AS venue_country
    FROM matches m JOIN venues v ON v.venue_id = m.venue_id
    WHERE m.status = 'Completed'
    UNION ALL
    SELECT m.match_id, m.team2_id, m.winner_id, v.country
    FROM matches m JOIN venues v ON v.venue_id = m.venue_id
    WHERE m.status = 'Completed'
)
SELECT t.team_name,
       SUM(CASE WHEN tm.venue_country = t.country THEN 1 ELSE 0 END) AS home_matches,
       SUM(CASE WHEN tm.venue_country = t.country AND tm.winner_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
       SUM(CASE WHEN tm.venue_country <> t.country THEN 1 ELSE 0 END) AS away_matches,
       SUM(CASE WHEN tm.venue_country <> t.country AND tm.winner_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
FROM team_matches tm
JOIN teams t ON t.team_id = tm.team_id
WHERE t.team_type = 'international'
GROUP BY t.team_id, t.team_name
ORDER BY home_wins DESC;"""},
    {"id": "Q13", "level": "Intermediate", "title": "Consecutive batsmen with 100+ combined runs",
     "description": "Adjacent batting positions whose runs add up to 100 or more in one innings "
                    "(sum of the two individual scores, an approximation of a partnership).",
     "sql": """
SELECT p1.full_name AS batsman_1, p2.full_name AS batsman_2,
       b1.runs + b2.runs AS combined_runs,
       m.match_desc || ' (innings ' || i.innings_no || ')' AS innings
FROM batting_performances b1
JOIN batting_performances b2
  ON b2.innings_id = b1.innings_id AND b2.batting_position = b1.batting_position + 1
JOIN players p1 ON p1.player_id = b1.player_id
JOIN players p2 ON p2.player_id = b2.player_id
JOIN innings i ON i.innings_id = b1.innings_id
JOIN matches m ON m.match_id = i.match_id
WHERE b1.runs + b2.runs >= 100
ORDER BY combined_runs DESC;"""},
    {"id": "Q14", "level": "Intermediate", "title": "Bowling performance by venue",
     "description": "Bowlers with 3+ matches at a venue (innings of 4+ overs only): avg economy, wickets, matches.",
     "sql": """
SELECT p.full_name, v.venue_name,
       ROUND(AVG(bp.economy_rate), 2) AS avg_economy,
       SUM(bp.wickets) AS total_wickets,
       COUNT(DISTINCT m.match_id) AS matches_played
FROM bowling_performances bp
JOIN innings i ON i.innings_id = bp.innings_id
JOIN matches m ON m.match_id = i.match_id
JOIN venues v ON v.venue_id = m.venue_id
JOIN players p ON p.player_id = bp.player_id
WHERE bp.overs >= 4
GROUP BY p.player_id, p.full_name, v.venue_id, v.venue_name
HAVING COUNT(DISTINCT m.match_id) >= 3
ORDER BY avg_economy ASC;"""},
    {"id": "Q15", "level": "Intermediate", "title": "Performance in close matches",
     "description": "Close = won by < 50 runs or < 5 wickets. Avg runs, close matches played, and wins when batting.",
     "sql": """
SELECT p.full_name,
       ROUND(AVG(b.runs), 2) AS avg_runs,
       COUNT(DISTINCT m.match_id) AS close_matches_played,
       COUNT(DISTINCT CASE WHEN m.winner_id = i.batting_team_id THEN m.match_id END) AS close_matches_won
FROM batting_performances b
JOIN innings i ON i.innings_id = b.innings_id
JOIN matches m ON m.match_id = i.match_id
JOIN players p ON p.player_id = b.player_id
WHERE m.status = 'Completed'
  AND ((m.victory_type = 'runs' AND m.victory_margin < 50)
    OR (m.victory_type = 'wickets' AND m.victory_margin < 5))
GROUP BY p.player_id, p.full_name
ORDER BY avg_runs DESC;"""},
    {"id": "Q16", "level": "Intermediate", "title": "Batting performance by year (since 2020)",
     "description": "Avg runs per match and avg strike rate per player per year; 5+ matches in the year.",
     "sql": """
SELECT p.full_name, strftime('%Y', m.match_date) AS year,
       COUNT(DISTINCT m.match_id) AS matches,
       ROUND(SUM(b.runs) * 1.0 / COUNT(DISTINCT m.match_id), 2) AS avg_runs_per_match,
       ROUND(AVG(b.strike_rate), 2) AS avg_strike_rate
FROM batting_performances b
JOIN innings i ON i.innings_id = b.innings_id
JOIN matches m ON m.match_id = i.match_id
JOIN players p ON p.player_id = b.player_id
WHERE m.match_date >= '2020-01-01'
GROUP BY p.player_id, p.full_name, strftime('%Y', m.match_date)
HAVING COUNT(DISTINCT m.match_id) >= 5
ORDER BY p.full_name, year;"""},
    # ------------------------------------------------------------------ ADVANCED
    {"id": "Q17", "level": "Advanced", "title": "Does winning the toss help?",
     "description": "% of matches won by the toss winner, split by toss decision (plus overall).",
     "sql": """
SELECT toss_decision, COUNT(*) AS total_matches,
       SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) AS won_after_toss,
       ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_pct
FROM matches
WHERE status = 'Completed' AND winner_id IS NOT NULL AND toss_winner_id IS NOT NULL
GROUP BY toss_decision
UNION ALL
SELECT 'overall', COUNT(*),
       SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END),
       ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM matches
WHERE status = 'Completed' AND winner_id IS NOT NULL AND toss_winner_id IS NOT NULL;"""},
    {"id": "Q18", "level": "Advanced", "title": "Most economical limited-overs bowlers",
     "description": "ODI + T20I; 10+ matches and 2+ overs per match on average.",
     "sql": """
SELECT p.full_name,
       ROUND(SUM(bp.runs_conceded) * 1.0 / SUM(bp.overs), 2) AS economy_rate,
       SUM(bp.wickets) AS total_wickets,
       COUNT(DISTINCT m.match_id) AS matches_bowled
FROM bowling_performances bp
JOIN innings i ON i.innings_id = bp.innings_id
JOIN matches m ON m.match_id = i.match_id
JOIN players p ON p.player_id = bp.player_id
WHERE m.match_format IN ('ODI', 'T20I')
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT m.match_id) >= 10
   AND SUM(bp.overs) * 1.0 / COUNT(DISTINCT m.match_id) >= 2
ORDER BY economy_rate ASC;"""},
    {"id": "Q19", "level": "Advanced", "title": "Most consistent batsmen",
     "description": "Avg runs and standard deviation; innings with 10+ balls faced, since 2022 "
                    "(min. 10 such innings). Lower SD = more consistent.",
     "sql": """
SELECT p.full_name, COUNT(*) AS innings,
       ROUND(AVG(b.runs), 2) AS avg_runs,
       ROUND(SQRT(AVG(b.runs * b.runs * 1.0) - AVG(b.runs * 1.0) * AVG(b.runs * 1.0)), 2) AS std_dev_runs
FROM batting_performances b
JOIN innings i ON i.innings_id = b.innings_id
JOIN matches m ON m.match_id = i.match_id
JOIN players p ON p.player_id = b.player_id
WHERE b.balls_faced >= 10 AND m.match_date >= '2022-01-01'
GROUP BY p.player_id, p.full_name
HAVING COUNT(*) >= 10
ORDER BY std_dev_runs ASC;"""},
    {"id": "Q20", "level": "Advanced", "title": "Matches and batting average by format",
     "description": "Matches and batting average in Test/ODI/T20I for players with 20+ matches in total.",
     "sql": """
SELECT p.full_name,
       SUM(CASE WHEN c.match_format = 'Test' THEN c.matches_played ELSE 0 END) AS test_matches,
       SUM(CASE WHEN c.match_format = 'ODI'  THEN c.matches_played ELSE 0 END) AS odi_matches,
       SUM(CASE WHEN c.match_format = 'T20I' THEN c.matches_played ELSE 0 END) AS t20i_matches,
       MAX(CASE WHEN c.match_format = 'Test' THEN c.batting_avg END) AS test_avg,
       MAX(CASE WHEN c.match_format = 'ODI'  THEN c.batting_avg END) AS odi_avg,
       MAX(CASE WHEN c.match_format = 'T20I' THEN c.batting_avg END) AS t20i_avg
FROM player_career_stats c
JOIN players p ON p.player_id = c.player_id
GROUP BY p.player_id, p.full_name
HAVING SUM(c.matches_played) >= 20
ORDER BY p.full_name;"""},
    {"id": "Q21", "level": "Advanced", "title": "Weighted player ranking (top 10 per format)",
     "description": "Batting + bowling + fielding points using the formula in the brief. "
                    "Missing bowling average defaults to 50 and economy to 6 (zero bowling points).",
     "sql": """
WITH fielding AS (
    SELECT fp.player_id, m.match_format,
           SUM(fp.catches) AS catches, SUM(fp.stumpings) AS stumpings
    FROM fielding_performances fp
    JOIN matches m ON m.match_id = fp.match_id
    GROUP BY fp.player_id, m.match_format
),
scored AS (
    SELECT c.player_id, c.match_format,
           (c.total_runs * 0.01) + (COALESCE(c.batting_avg, 0) * 0.5)
             + (COALESCE(c.strike_rate, 0) * 0.3) AS batting_points,
           (c.total_wickets * 2) + ((50 - COALESCE(c.bowling_avg, 50)) * 0.5)
             + ((6 - COALESCE(c.economy_rate, 6)) * 2) AS bowling_points,
           (COALESCE(f.catches, 0) * 3) + (COALESCE(f.stumpings, 0) * 5) AS fielding_points
    FROM player_career_stats c
    LEFT JOIN fielding f ON f.player_id = c.player_id AND f.match_format = c.match_format
),
ranked AS (
    SELECT s.*, batting_points + bowling_points + fielding_points AS total_points,
           RANK() OVER (PARTITION BY match_format
                        ORDER BY batting_points + bowling_points + fielding_points DESC) AS format_rank
    FROM scored s
)
SELECT r.match_format, r.format_rank, p.full_name,
       ROUND(r.batting_points, 2) AS batting_points,
       ROUND(r.bowling_points, 2) AS bowling_points,
       r.fielding_points, ROUND(r.total_points, 2) AS total_points
FROM ranked r
JOIN players p ON p.player_id = r.player_id
WHERE r.format_rank <= 10
ORDER BY r.match_format, r.format_rank;"""},
    {"id": "Q22", "level": "Advanced", "title": "Head-to-head analysis (last 3 years)",
     "description": "Team pairs with 5+ matches in the last 3 years: wins, avg margins, win percentage.",
     "sql": """
WITH recent AS (
    SELECT m.match_id, m.winner_id, m.victory_type, m.victory_margin,
           MIN(m.team1_id, m.team2_id) AS team_a, MAX(m.team1_id, m.team2_id) AS team_b
    FROM matches m
    WHERE m.status = 'Completed' AND m.winner_id IS NOT NULL
      AND m.match_date >= date('now', '-3 years')
),
pairs AS (
    SELECT team_a, team_b, COUNT(*) AS total_matches,
           SUM(CASE WHEN winner_id = team_a THEN 1 ELSE 0 END) AS wins_a,
           SUM(CASE WHEN winner_id = team_b THEN 1 ELSE 0 END) AS wins_b,
           AVG(CASE WHEN winner_id = team_a AND victory_type = 'runs' THEN victory_margin END) AS a_avg_runs_margin,
           AVG(CASE WHEN winner_id = team_a AND victory_type = 'wickets' THEN victory_margin END) AS a_avg_wkts_margin,
           AVG(CASE WHEN winner_id = team_b AND victory_type = 'runs' THEN victory_margin END) AS b_avg_runs_margin,
           AVG(CASE WHEN winner_id = team_b AND victory_type = 'wickets' THEN victory_margin END) AS b_avg_wkts_margin
    FROM recent
    GROUP BY team_a, team_b
    HAVING COUNT(*) >= 5
)
SELECT ta.team_name AS team_a, tb.team_name AS team_b, pr.total_matches,
       pr.wins_a, pr.wins_b,
       ROUND(100.0 * pr.wins_a / pr.total_matches, 1) AS team_a_win_pct,
       ROUND(100.0 * pr.wins_b / pr.total_matches, 1) AS team_b_win_pct,
       ROUND(pr.a_avg_runs_margin, 1) AS a_avg_runs_margin, ROUND(pr.a_avg_wkts_margin, 1) AS a_avg_wkts_margin,
       ROUND(pr.b_avg_runs_margin, 1) AS b_avg_runs_margin, ROUND(pr.b_avg_wkts_margin, 1) AS b_avg_wkts_margin
FROM pairs pr
JOIN teams ta ON ta.team_id = pr.team_a
JOIN teams tb ON tb.team_id = pr.team_b
ORDER BY pr.total_matches DESC, ta.team_name;"""},
    {"id": "Q22b", "level": "Advanced", "title": "Head-to-head: batting first vs bowling first by venue",
     "description": "Second half of Q22: for the same team pairs, results by venue depending on who batted first.",
     "sql": """
WITH recent AS (
    SELECT m.match_id, m.venue_id, m.winner_id,
           MIN(m.team1_id, m.team2_id) AS team_a, MAX(m.team1_id, m.team2_id) AS team_b
    FROM matches m
    WHERE m.status = 'Completed' AND m.winner_id IS NOT NULL
      AND m.match_date >= date('now', '-3 years')
),
eligible AS (
    SELECT team_a, team_b FROM recent GROUP BY team_a, team_b HAVING COUNT(*) >= 5
)
SELECT ta.team_name AS team_a, tb.team_name AS team_b, v.venue_name,
       COUNT(*) AS matches,
       SUM(CASE WHEN r.winner_id = i.batting_team_id THEN 1 ELSE 0 END) AS won_batting_first,
       SUM(CASE WHEN r.winner_id <> i.batting_team_id THEN 1 ELSE 0 END) AS won_bowling_first,
       ROUND(100.0 * SUM(CASE WHEN r.winner_id = i.batting_team_id THEN 1 ELSE 0 END) / COUNT(*), 1) AS batting_first_win_pct
FROM recent r
JOIN eligible e ON e.team_a = r.team_a AND e.team_b = r.team_b
JOIN innings i ON i.match_id = r.match_id AND i.innings_no = 1
JOIN venues v ON v.venue_id = r.venue_id
JOIN teams ta ON ta.team_id = r.team_a
JOIN teams tb ON tb.team_id = r.team_b
GROUP BY r.team_a, r.team_b, v.venue_id, ta.team_name, tb.team_name, v.venue_name
ORDER BY ta.team_name, tb.team_name, matches DESC;"""},
    {"id": "Q23", "level": "Advanced", "title": "Recent player form and momentum",
     "description": "Last 10 innings: avg runs (last 5 vs last 10), strike-rate trend, 50+ scores, "
                    "consistency, and a form category.",
     "sql": """
WITH ranked AS (
    SELECT b.player_id, b.runs, b.strike_rate,
           ROW_NUMBER() OVER (PARTITION BY b.player_id
                              ORDER BY m.match_date DESC, b.batting_id DESC) AS rn
    FROM batting_performances b
    JOIN innings i ON i.innings_id = b.innings_id
    JOIN matches m ON m.match_id = i.match_id
    WHERE m.status = 'Completed'
),
agg AS (
    SELECT player_id,
           AVG(CASE WHEN rn <= 5 THEN runs END) AS avg_last5,
           AVG(runs) AS avg_last10,
           AVG(CASE WHEN rn <= 5 THEN strike_rate END) AS sr_last5,
           AVG(CASE WHEN rn > 5 THEN strike_rate END) AS sr_prev5,
           SUM(CASE WHEN runs > 50 THEN 1 ELSE 0 END) AS scores_above_50,
           SQRT(AVG(runs * runs * 1.0) - AVG(runs * 1.0) * AVG(runs * 1.0)) AS std_dev
    FROM ranked
    WHERE rn <= 10
    GROUP BY player_id
    HAVING COUNT(*) = 10
)
SELECT p.full_name,
       ROUND(a.avg_last5, 2) AS avg_last5, ROUND(a.avg_last10, 2) AS avg_last10,
       ROUND(a.sr_last5, 2) AS sr_last5, ROUND(a.sr_prev5, 2) AS sr_prev5,
       ROUND(a.sr_last5 - a.sr_prev5, 2) AS sr_trend,
       a.scores_above_50, ROUND(a.std_dev, 2) AS std_dev,
       ROUND(a.avg_last10 / NULLIF(a.std_dev, 0), 2) AS consistency_score,
       CASE WHEN a.avg_last5 >= 40 AND a.scores_above_50 >= 3 THEN 'Excellent Form'
            WHEN a.avg_last5 >= 28 AND a.scores_above_50 >= 1 THEN 'Good Form'
            WHEN a.avg_last5 >= 15 THEN 'Average Form'
            ELSE 'Poor Form' END AS form_category
FROM agg a
JOIN players p ON p.player_id = a.player_id
ORDER BY a.avg_last5 DESC;"""},
    {"id": "Q24", "level": "Advanced", "title": "Best batting partnerships",
     "description": "Consecutive-position pairs with 5+ partnerships: avg, 50+ count, highest, success rate, rank. "
                    "Partnership runs = sum of the two scores (approximation).",
     "sql": """
WITH partnerships AS (
    SELECT b1.player_id AS player_1, b2.player_id AS player_2, b1.runs + b2.runs AS runs
    FROM batting_performances b1
    JOIN batting_performances b2
      ON b2.innings_id = b1.innings_id AND b2.batting_position = b1.batting_position + 1
),
summary AS (
    SELECT player_1, player_2, COUNT(*) AS partnerships,
           ROUND(AVG(runs), 2) AS avg_runs,
           SUM(CASE WHEN runs > 50 THEN 1 ELSE 0 END) AS over_50,
           MAX(runs) AS highest,
           ROUND(100.0 * SUM(CASE WHEN runs > 50 THEN 1 ELSE 0 END) / COUNT(*), 1) AS success_rate_pct
    FROM partnerships
    GROUP BY player_1, player_2
    HAVING COUNT(*) >= 5
)
SELECT RANK() OVER (ORDER BY s.success_rate_pct DESC, s.avg_runs DESC) AS rank,
       p1.full_name AS batsman_1, p2.full_name AS batsman_2,
       s.partnerships, s.avg_runs, s.over_50, s.highest, s.success_rate_pct
FROM summary s
JOIN players p1 ON p1.player_id = s.player_1
JOIN players p2 ON p2.player_id = s.player_2
ORDER BY rank
LIMIT 50;"""},
    {"id": "Q25", "level": "Advanced", "title": "Career trajectory (quarterly time series)",
     "description": "Quarterly avg runs/strike rate (3+ matches per quarter, 6+ quarters), quarter-on-quarter "
                    "change (+/-5%), and a career-phase label comparing the first and last 3 quarters (+/-10%).",
     "sql": """
WITH quarterly AS (
    SELECT b.player_id,
           strftime('%Y', m.match_date) || '-Q' ||
             ((CAST(strftime('%m', m.match_date) AS INTEGER) + 2) / 3) AS quarter,
           COUNT(DISTINCT m.match_id) AS matches,
           AVG(b.runs) AS avg_runs, AVG(b.strike_rate) AS avg_sr
    FROM batting_performances b
    JOIN innings i ON i.innings_id = b.innings_id
    JOIN matches m ON m.match_id = i.match_id
    WHERE m.status = 'Completed'
    GROUP BY b.player_id, strftime('%Y', m.match_date),
             ((CAST(strftime('%m', m.match_date) AS INTEGER) + 2) / 3)
    HAVING COUNT(DISTINCT m.match_id) >= 3
),
windowed AS (
    SELECT q.*,
           LAG(avg_runs) OVER (PARTITION BY player_id ORDER BY quarter) AS prev_runs,
           ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY quarter) AS rn,
           COUNT(*) OVER (PARTITION BY player_id) AS quarter_count
    FROM quarterly q
),
per_player AS (
    SELECT player_id, MAX(quarter_count) AS quarters,
           ROUND(AVG(avg_runs), 2) AS overall_avg_runs,
           ROUND(AVG(avg_sr), 2) AS overall_avg_sr,
           SUM(CASE WHEN prev_runs IS NOT NULL AND avg_runs > prev_runs * 1.05 THEN 1 ELSE 0 END) AS improving_quarters,
           SUM(CASE WHEN prev_runs IS NOT NULL AND avg_runs < prev_runs * 0.95 THEN 1 ELSE 0 END) AS declining_quarters,
           SUM(CASE WHEN prev_runs IS NOT NULL AND avg_runs BETWEEN prev_runs * 0.95 AND prev_runs * 1.05 THEN 1 ELSE 0 END) AS stable_quarters,
           AVG(CASE WHEN rn <= 3 THEN avg_runs END) AS early_avg,
           AVG(CASE WHEN rn > quarter_count - 3 THEN avg_runs END) AS recent_avg
    FROM windowed
    GROUP BY player_id
    HAVING MAX(quarter_count) >= 6
)
SELECT p.full_name, pp.quarters, pp.overall_avg_runs, pp.overall_avg_sr,
       pp.improving_quarters, pp.declining_quarters, pp.stable_quarters,
       ROUND(pp.early_avg, 2) AS early_avg_runs, ROUND(pp.recent_avg, 2) AS recent_avg_runs,
       CASE WHEN pp.recent_avg > pp.early_avg * 1.10 THEN 'Career Ascending'
            WHEN pp.recent_avg < pp.early_avg * 0.90 THEN 'Career Declining'
            ELSE 'Career Stable' END AS career_phase
FROM per_player pp
JOIN players p ON p.player_id = pp.player_id
ORDER BY pp.recent_avg - pp.early_avg DESC;"""},
]

for _q in QUERIES:
    _q["sql"] = _q["sql"].strip()


def get_query(query_id: str) -> dict:
    """Return the query dict for ``query_id`` (e.g. ``'Q7'``)."""
    for query in QUERIES:
        if query["id"] == query_id:
            return query
    raise KeyError(f"Unknown query id: {query_id}")
