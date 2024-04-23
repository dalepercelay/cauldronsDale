CREATE TABLE global_inventory (
    id INT PRIMARY KEY,
    num_red_ml INT NOT NULL,
    num_green_ml INT NOT NULL,
    num_blue_ml INT NOT NULL,
    gold INT NOT NULL
    );

CREATE TABLE potions (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price INT NOT NULL,
    quantity INT NOT NULL,
    potion_type INT[] NOT NULL
    );

CREATE TABLE carts (
    id SERIAL PRIMARY KEY, 
    customer_name TEXT NOT NULL
    );

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    sku TEXT NOT NULL,
    quantity INT NOT NULL,
    cart_id INT NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES potions(sku)
    );
