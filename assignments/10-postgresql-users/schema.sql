-- Выполнить в pgAdmin (Query Tool) на базе test, схема public.

CREATE TABLE IF NOT EXISTS users (
  id   SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  age  INT  CHECK (age >= 0)
);