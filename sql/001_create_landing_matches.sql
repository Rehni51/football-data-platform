-- Création d'un schéma dédié aux données ingérées
CREATE SCHEMA IF NOT EXISTS landing;

-- Table de réception des rencontres FFF
CREATE TABLE IF NOT EXISTS landing.matches (

    match_id BIGINT PRIMARY KEY,

    payload JSONB NOT NULL,

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT matches_payload_object
        CHECK (jsonb_typeof(payload) = 'object')
);
