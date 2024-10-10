USE rawdata;

CREATE TABLE IF NOT EXISTS data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid VARCHAR(255) NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Revoke all privileges from write-user
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'write-user'@'%';

-- Grant specific privileges to write-user
GRANT SELECT, INSERT, UPDATE, DELETE ON rawdata.data TO 'write-user'@'%';

-- Create and grant privileges to read user
CREATE USER IF NOT EXISTS 'read-user'@'%' IDENTIFIED BY 'read-pass';
GRANT SELECT ON rawdata.data TO 'read-user'@'%';

FLUSH PRIVILEGES;