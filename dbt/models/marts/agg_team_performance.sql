
WITH team_matches AS (

    SELECT *
    FROM {{ ref('fct_team_matches') }}

),

aggregated AS (

    SELECT
        competition_id,
        season,
        poule_name,
        club_id,
        team_number,

        MAX(team_name) AS team_name,

        COUNT(*) AS scheduled_matches,

        COUNT(*) FILTER (
            WHERE has_score
        ) AS matches_with_scores,

        COUNT(*) FILTER (
            WHERE result_from_score = 'win'
        ) AS wins,

        COUNT(*) FILTER (
            WHERE result_from_score = 'draw'
        ) AS draws,

        COUNT(*) FILTER (
            WHERE result_from_score = 'loss'
        ) AS losses,

        COALESCE(
            SUM(goals_for) FILTER (WHERE has_score),
            0
        ) AS goals_for,

        COALESCE(
            SUM(goals_against) FILTER (WHERE has_score),
            0
        ) AS goals_against

    FROM team_matches

    GROUP BY
        competition_id,
        season,
        poule_name,
        club_id,
        team_number

),

final AS (

    SELECT
        *,

        goals_for - goals_against AS goal_difference,

        wins * 3 + draws AS points_from_scores

    FROM aggregated

)

SELECT *
FROM final
