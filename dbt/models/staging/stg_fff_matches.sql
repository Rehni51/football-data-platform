WITH source AS (

    SELECT
        match_id,
        payload,
        ingested_at

    FROM {{ source('fff', 'matches') }}

),

renamed AS (

    SELECT

        -- Identifiant de la rencontre
        match_id,

        -- Compétition et saison
        (payload->>'competition_id')::BIGINT AS competition_id,
        (payload->>'season')::INTEGER AS season,
        payload->>'poule' AS poule_name,

        -- Date du match
        LEFT(payload->>'date', 10)::DATE AS match_date,

        -- Équipe à domicile
        (payload->>'home_club_id')::BIGINT AS home_club_id,
        (payload->>'home_team_number')::INTEGER AS home_team_number,
        payload->>'home_team' AS home_team_name,

        -- Équipe à l'extérieur
        (payload->>'away_club_id')::BIGINT AS away_club_id,
        (payload->>'away_team_number')::INTEGER AS away_team_number,
        payload->>'away_team' AS away_team_name,

        -- Résultats
        (payload->>'home_score')::INTEGER AS home_score,
        (payload->>'away_score')::INTEGER AS away_score,

        -- Dates de suivi
        (payload->>'updated_at')::TIMESTAMPTZ AS source_updated_at,
        ingested_at

    FROM source

)

SELECT *
FROM renamed
