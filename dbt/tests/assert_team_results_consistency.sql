SELECT
    competition_id,
    season,
    poule_name,
    club_id,
    team_number

FROM {{ ref('agg_team_performance') }}

WHERE matches_with_scores != wins + draws + losses
   OR scheduled_matches < matches_with_scores
   OR points_from_scores != wins * 3 + draws
   OR goal_difference != goals_for - goals_against

