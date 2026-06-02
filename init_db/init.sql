CREATE TABLE IF NOT EXISTS fraud_scores (
    id SERIAL PRIMARY KEY,
    transaction_id TEXT,
    score FLOAT,
    fraud_flag INTEGER,
    us_state TEXT,
    merch TEXT,
    cat_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);