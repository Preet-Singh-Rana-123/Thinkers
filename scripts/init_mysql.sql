-- MySQL Initialization Script for Thinkers Platform
-- Grants required read-only privileges for Prometheus mysqld_exporter

CREATE USER IF NOT EXISTS 'exporter'@'%' IDENTIFIED BY 'exporter_password_2026' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'%';
FLUSH PRIVILEGES;
