CREATE TABLE global_inventory (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    num_red_ml INT NOT NULL,
    num_green_ml INT NOT NULL,
    num_blue_ml INT NOT NULL,
    gold INT NOT NULL,
    description TEXT
);

CREATE TABLE potions (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price INT NOT NULL,
    potion_type INT[] NOT NULL
);

CREATE TABLE potion_transactions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

CREATE TABLE ledger_entries (
    id SERIAL PRIMARY KEY,
    sku TEXT NOT NULL,
    quantity INT NOT NULL,
    transaction INT NOT NULL,
    FOREIGN KEY (sku) REFERENCES potions(sku),
    FOREIGN KEY (transaction) REFERENCES potion_transactions(id)
);

CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL
);

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INT NOT NULL,
    sku TEXT NOT NULL,
    quantity INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES potions(sku)
);