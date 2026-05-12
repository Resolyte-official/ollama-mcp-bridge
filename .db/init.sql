CREATE ROLE mcpserver
    WITH CREATEDB 
    LOGIN 
    PASSWORD 'open-db';

CREATE DATABASE "school-db" 
    OWNER mcpserver 
    ENCODING 'UTF8';

\c "school-db"

CREATE EXTENSION IF NOT EXISTS vector;