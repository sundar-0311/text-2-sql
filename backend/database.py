from sqlalchemy import create_engine, text
DATABASE_URL = "sqlite:///./store.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL,
                stock INTEGER
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_name TEXT,
                amount REAL,
                status TEXT DEFAULT 'pending',
                ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))

        # ONLY INSERT SAMPLE DATA IF THE TABLES ARE EMPTY
        if conn.execute(text("SELECT COUNT(*) FROM users")).scalar() == 0:
            conn.execute(text("""
                INSERT INTO users (name, email, age) VALUES
                ('Alice Johnson', 'alice@email.com', 28),
                ('Bob Smith', 'bob@email.com', 35),
                ('Carol White', 'carol@email.com', 22),
                ('David Brown', 'david@email.com', 45),
                ('Eva Green', 'eva@email.com', 31)
            """))
            conn.execute(text("""
                INSERT INTO products (name, category, price, stock) VALUES
                ('Laptop Pro', 'electronics', 999.99, 50),
                ('Wireless Mouse', 'electronics', 29.99, 200),
                ('Office Chair', 'furniture', 349.99, 30),
                ('Notebook', 'stationery', 4.99, 500),
                ('Coffee Mug', 'kitchen', 12.99, 150)
            """))
            conn.execute(text("""
                INSERT INTO orders (user_id, product_name, amount, status) VALUES
                (1, 'Laptop Pro', 999.99, 'delivered'),
                (1, 'Wireless Mouse', 29.99, 'delivered'),
                (2, 'Office Chair', 349.99, 'shipped'),
                (3, 'Notebook', 4.99, 'pending'),
                (4, 'Coffee Mug', 12.99, 'delivered'),
                (5, 'Laptop Pro', 999.99, 'cancelled'),
                (2, 'Wireless Mouse', 29.99, 'pending')
            """))
            conn.commit()

def execute_sql(sql: str):
    # ONLY SELECT QUERIES ALLOWED, ALL OTHERS ARE FLAGGED
    sql_upper = sql.strip().upper()
    if any(sql_upper.startswith(k) for k in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]):
        return {"success": False, "error": "Only SELECT queries are allowed"}

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return {"success": True, "columns": columns, "rows": rows}
    except Exception as e:
        return {"success": False, "error": str(e)}