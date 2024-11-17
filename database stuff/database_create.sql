CREATE DATABASE stockScraper;
use stockScraper;

-- Table Creations
CREATE TABLE stocks(
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(16),
    company_name VARCHAR(50),
    sector VARCHAR(50)
);
CREATE TABLE option_contracts(
    option_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT,
    expiration_date DATE,
    strike_price DECIMAL(10,2),
    option_type CHAR(1),
    contract_symbol VARCHAR(50),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);
CREATE TABLE market_data(
    market_data_id INT AUTO_INCREMENT PRIMARY KEY,
    option_id INT,
    time_stamp DATETIME,
    last_price DECIMAL(10,2),
    bid DECIMAL(10,2),
    ask DECIMAL(10,2),
    volume INT,
    open_interest INT,
    FOREIGN KEY (option_id) REFERENCES option_contracts(option_id)
);
CREATE TABLE trades(
    trade_id INT AUTO_INCREMENT PRIMARY KEY,
    option_id INT,
    trade_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    price DECIMAL(10,2),
    quantity INT,
    trade_type VARCHAR(20),
    FOREIGN KEY (option_id) REFERENCES option_contracts(option_id)
);

-- Index Creations
CREATE INDEX idx_ticker ON stocks(ticker);
CREATE INDEX idx_exp_date ON option_contracts(expiration_date);
CREATE INDEX idx_opt_type ON option_contracts(option_type);
CREATE INDEX idx_trade_type ON trades(trade_type);
CREATE INDEX idx_trade_date ON trades(trade_date);

-- User Creations
CREATE USER 'mark'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'mainScript'@'localhost' IDENTIFIED BY '1234';

-- Granting Privileges to Users
GRANT ALL PRIVILEGES ON stockScraper.* TO 'mark'@'localhost';
GRANT SELECT, INSERT ON stockScraper.* TO 'mainScript'@'localhost';
