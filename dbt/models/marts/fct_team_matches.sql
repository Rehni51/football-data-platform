
WITH matches AS (

    SELECT *
    FROM {{ ref('fct_matches') }}

),

team_matches AS (

    -- Point de vue de l'équipe à domicile
    SELECT
        match_id::TEXT || '_home' AS team_match_id,
        match_id,
        competition_id,
        season,
        poule_name,
        match_date,

        home_club_id AS club_id,
        home_team_number AS team_number,
        home_team_name AS team_name,

        away_club_id AS opponent_club_id,
        away_team_name AS opponent_name,

        'home' AS venue,

        home_score AS goals_for,
        away_score AS goals_against,
        has_score,

        CASE
            WHEN NOT has_score THEN NULL
            WHEN home_score > away_score THEN 'win'
            WHEN home_score < away_score THEN 'loss'
            ELSE 'draw'
        END AS result_from_score

    FROM matches

    UNION ALL

    -- Point de vue de l'équipe à l'extérieur
    SELECT
        match_id::TEXT || '_away' AS team_match_id,
        match_id,
        competition_id,
        season,
        poule_name,
        match_date,

        away_club_id AS club_id,
        away_team_number AS team_number,
        away_team_name AS team_name,

        home_club_id AS opponent_club_id,
        home_team_name AS opponent_name,

        'away' AS venue,

        away_score AS goals_for,
        home_score AS goals_against,
        has_score,

        CASE
            WHEN NOT has_score THEN NULL
            WHEN away_score > home_score THEN 'win'
            WHEN away_score < home_score THEN 'loss'
            ELSE 'draw'
        END AS result_from_score

    FROM matches

)

SELECT
    *,
    goals_for - goals_against AS goal_difference
FROM team_matches
