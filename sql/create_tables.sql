CREATE TABLE IF NOT EXISTS sales (
    location_id     INTEGER,
    city            VARCHAR(100),
    state           VARCHAR(100),
    country         VARCHAR(100),
    latitude        FLOAT,
    longitude       FLOAT,
    product_id      VARCHAR(50),
    product_category VARCHAR(100),
    sales_volume    FLOAT,
    sales_revenue   FLOAT,
    date            DATE
);

CREATE TABLE IF NOT EXISTS sales_by_category (
    product_category VARCHAR(100),
    total_revenue    FLOAT,
    total_volume     FLOAT,
    num_transactions INTEGER
);