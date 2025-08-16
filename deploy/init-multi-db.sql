-- Creates per-tenant databases on first container init
-- Runs only once by postgres:16 entrypoint when data dir is empty.
CREATE DATABASE avp_default;
CREATE DATABASE avp_sonerdicanav;
CREATE DATABASE avp_emirkevserav;
