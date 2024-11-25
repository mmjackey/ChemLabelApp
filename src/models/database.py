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
            "Chemical Details": ["chemical_details"],
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
    
    #Testing
    def fetch_table_names(self):
        self.cur.execute(
        """SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        ORDER BY table_name;"""
        )
        # Fetch column names for specific table
        tables = self.cur.fetchall()
        for table in tables:
            print(table[0].title())
            if "batch_inventory" in table[0].lower():
                self.cur.execute(
                f"""SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name   = '{table[0]}'
                ORDER BY ordinal_position;"""
                )
                vals = self.cur.fetchall()
                for column, data_type in vals:
                    print(f"  - Column: {column}, Type: {data_type}")
    
    def get_latest_barcode_id(self):
        self.cur.execute(
        """SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        ORDER BY table_name;"""
        )
        # Fetch column names for specific table
        tables = self.cur.fetchall()
        for table in tables:
            if "batch_inventory" in table[0].lower():
                self.cur.execute(
                    """SELECT id
                    FROM batch_inventory
                    ORDER BY id DESC
                    LIMIT 1;"""
                )

                latest_id = self.cur.fetchone()
                if latest_id:
                    return latest_id[0]
                else: return None
        return None
                
    #USE ONCE - should not be adding tables this way
    def add_details_table(self):
        change_owner_query = "ALTER TABLE chemical_details OWNER TO database_dev;"
        self.cur.execute(change_owner_query)
        self.conn.commit()
        print("Sucessfully changed owner to database_dev")
    #     create_table_query = """
    #     CREATE TABLE chemical_details (
    #         id VARCHAR(12) PRIMARY KEY,  -- Changed to character varying (up to 12 characters)
    #         chemical_name VARCHAR(255),  -- Variable-length string for chemical name
    #         volume REAL,  -- Changed to REAL (floating-point type)
    #         concentration REAL,  -- Changed to REAL (floating-point type)
    #         date_created TEXT,  -- Changed to TEXT type (to store as a string)
    #         order_url VARCHAR(255),  -- Variable-length string for order URL (max 255 characters)
    #         image_url VARCHAR(255)   -- Variable-length string for image URL (max 255 characters)
    #     );
    #     """
    #     self.cur.execute(create_table_query)
    #     self.conn.commit()
        


if __name__ == "__main__":
    db = Database()
    db.fetch_column_names("general_product")
    #db.fetch_table_names()
    