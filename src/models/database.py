import psycopg2


class Database:
    def __init__(self):

        self.item_type_tables = {
            "Chemical Inventory": ["chemical_inventory", "general_product"],
            "General Inventory": ["general_inventory", "general_product"],
            "Product Inventory (Batch Process)": [
                "batch_inventory",
                "synthesis",
                "washing",
                "drying",
                "functionalization",
                "quality_control",
                "shipping",
            ],
        }

        self.conn = psycopg2.connect(
            database="inventory_management",
            user="postgres",
            host="192.168.68.73",
            password="team3#",
            port=5432,
        )

        self.cur = self.conn.cursor()

    def fetch_column_names(self, tables):
        column_names_dict = {}

        for table in tables:
            self.cur.execute(
                f"""SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name   = '{table}'
                ORDER BY ordinal_position;"""
            )
            vals = self.cur.fetchall()

            """
            fetchall returns a tuple of elements, but all but 0 is empty,
            we create a list of the table names
            """

            vals = [item[0] for item in vals]

            column_names_dict[table] = vals

        return column_names_dict


if __name__ == "__main__":
    db = Database()
    db.fetch_column_names("general_product")
