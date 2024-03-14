-- https://dba.stackexchange.com/questions/11893/force-drop-db-while-others-may-be-connected
UPDATE pg_database SET datallowconn = 'false' WHERE datname = 'spdb';
UPDATE pg_database SET datallowconn = 'false' WHERE datname = 'hundbidrag';
UPDATE pg_database SET datallowconn = 'false' WHERE datname = 'patches';

SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'spdb';
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'hundbidrag';
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'patches';

DROP DATABASE IF EXISTS spdb;
DROP DATABASE IF EXISTS hundbidrag;
DROP DATABASE IF EXISTS patches;

DROP USER IF EXISTS spdb;
DROP USER IF EXISTS hundbidrag;
DROP USER IF EXISTS patches;
