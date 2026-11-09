-- Chaque rencontre doit avoir deux participations :
-- une équipe à domicile et une équipe à l'extérieur.

SELECT
    match_id,

    COUNT(*) AS participation_count,

    COUNT(*) FILTER (
        WHERE venue = 'home'
    ) AS home_count,

    COUNT(*) FILTER (
        WHERE venue = 'away'
    ) AS away_count

FROM {{ ref('fct_team_matches') }}

GROUP BY match_id

HAVING
    COUNT(*) <> 2

    OR COUNT(*) FILTER (
        WHERE venue = 'home'
    ) <> 1

    OR COUNT(*) FILTER (
        WHERE venue = 'away'
    ) <> 1
