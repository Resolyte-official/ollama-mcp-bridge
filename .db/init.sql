CREATE ROLE mcpserver
    WITH CREATEDB 
    LOGIN 
    PASSWORD 'open-db';

CREATE DATABASE "school-db" 
    OWNER mcpserver 
    ENCODING 'UTF8';