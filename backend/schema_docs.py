SCHEMA_DOCS = [
    "Table: users — columns: id, name, email, age, created_at. Use to query user info.",
    "Table: orders — columns: id, user_id (FK→users.id), product_name, amount, status (pending/shipped/delivered/cancelled), ordered_at.",
    "Table: products — columns: id, name, category, price, stock. Use for product/inventory queries.",
    "To get orders with user names, JOIN orders o ON users u WHERE o.user_id = u.id.",
]