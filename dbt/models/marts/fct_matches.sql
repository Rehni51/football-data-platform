WITH matches AS (

    SELECT
        match_id,
        competition_id,
        season,
        poule_name,
        match_date,

        home_club_id,
        home_team_number,
        home_team_name,

        away_club_id,
        away_team_number,
        away_team_name,

        home_score,
        away_score,

        source_updated_at,
        ingested_at

    FROM {{ ref('stg_fff_matches') }}

),

enriched AS (

    SELECT
        *,

        -- Les deux scores sont-ils renseignés ?
        (
            home_score IS NOT NULL
            AND away_score IS NOT NULL
        ) AS has_score,

        -- Résultat déterminé à partir des scores
        CASE
            WHEN home_score IS NULL
              OR away_score IS NULL THEN NULL

            WHEN home_score > away_score
                THEN 'home_win'

            WHEN home_score < away_score
                THEN 'away_win'

            ELSE 'draw'
        END AS score_outcome,

        -- Nombre total de buts
        CASE
            WHEN home_score IS NOT NULL
             AND away_score IS NOT NULL
            THEN home_score + away_score
            ELSE NULL
        END AS total_goals,

        -- Différence de buts du point de vue du domicile
        CASE
            WHEN home_score IS NOT NULL
             AND away_score IS NOT NULL
            THEN home_score - away_score
            ELSE NULL
        END AS home_goal_difference

    FROM matches

)

SELECT *
FROM enriched
