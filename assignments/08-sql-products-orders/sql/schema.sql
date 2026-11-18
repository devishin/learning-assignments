-- Lesson-style shop: products + orders (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    in_stock INTEGER NOT NULL DEFAULT 1,
    CHECK (price >= 0),
    CHECK (in_stock IN (0, 1))
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    customer_note TEXT,
    is_test INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT,
    CHECK (quantity > 0),
    CHECK (is_test IN (0, 1))
);

CREATE INDEX idx_products_category ON products (category);
CREATE INDEX idx_products_sku ON products (sku);
CREATE INDEX idx_orders_product_id ON orders (product_id);
CREATE INDEX idx_orders_order_date ON orders (order_date);