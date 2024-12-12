import psycopg2
import yaml


class Database:
    def __init__(self):

        self.inventory_tables_data = "src/models/database.yaml"

        with open(self.inventory_tables_data, "r") as file:
            self.inventory_type_tables = yaml.safe_load(file)[
                "INVENTORY_TYPES"
            ]

        self.conn = psycopg2.connect(
            database="inventory_management",
            user="postgres",
            host="100.91.167.126",
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
    
    def fetch_columns_in_table(self,table_name):
        try:
            self.cur.execute(
                """SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = %s;
                """, (table_name,)
                )
                
            columns = self.cur.fetchall()

            return [column[0] for column in columns]

        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_inventory_table_types(self):
        return self.inventory_type_tables

    def get_table_id_column(self, table_name):
        self.cur.execute(
            f"""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """
        )
        table_cols = self.cur.fetchall()
        for col in table_cols:
            if "id" in col[0]:
                id_col = col[0]
        return id_col

    def check_table_exists(self, table_name):
        # Check if the table exists
        # you need 'quotes' around the table name or it'll error out
        self.cur.execute(
            f"""SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = '{table_name}'
            );""",
        )

        table_exists = self.cur.fetchone()[0]
        return table_exists

    def get_latest_barcode_id(self, table_type):

        if "product" in table_type:
            table_type = "batch_inventory"

        # Prevent SQL injection
        sanitized_table_type = table_type.replace(" ", "_").lower()

        # Attempt to retrieve the barcode ID
        print(f"Attempting to retrieve latest {sanitized_table_type} ID...")

        table_exists = self.check_table_exists(sanitized_table_type)

        if table_exists:

            # Is 'id' present in table?
            self.cur.execute(
                f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s AND column_name = 'id';
                """, (sanitized_table_type,)
            )
            column_exists = self.cur.fetchone()

            # Is 'product_id' present in table? (General Inventory)
            self.cur.execute(
                f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s AND column_name = 'product_id';
                """, (sanitized_table_type,)
            )
            other_column_exists = self.cur.fetchone()

            if column_exists or other_column_exists:
                
                column_name = 'id' if column_exists else 'product_id'

                # Fetch most recent 'id' value
                self.cur.execute(
                    f"""SELECT {column_name}
                    FROM {sanitized_table_type}
                    ORDER BY {column_name} DESC
                    LIMIT 1;"""
                )
                
                latest_id = self.cur.fetchone()
                if latest_id:
                    print(f"Latest {sanitized_table_type} ID retrieved: {latest_id[0]}\n")
                    return latest_id[0]
                else:
                    print(f"No records found in {sanitized_table_type}\n")
                    return None
            else:
                print(f"Column 'id' does not exist in table {sanitized_table_type}\n")
        else:
            print(f"{sanitized_table_type} not found in database\n")
            return None

    
    # Check if column name is in specified table
    def column_in_table(self, column_name, table_name):
        try:
            query = ("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s;
            """)

            self.cur.execute(query, (table_name, column_name))
            result = self.cur.fetchone()

            if result:
                #print(f"Column '{column_name}' exists in table '{table_name}'.")
                return True
            else:
                #print(f"Column '{column_name}' does not exist in table '{table_name}'.")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False


    def check_column_data_types(self, user_input_dict, table_name):
        try:

            # Get column names, their data types, and whether they are nullable
            query = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
            """

            self.cur.execute(query, (table_name,))
            columns_info = self.cur.fetchall()

            # Create a dictionary of columns with their types and nullability
            column_details = {
                column[0]: {"type": column[1], "nullable": column[2] == "YES"}
                for column in columns_info
            }

            # Check the user inputs against the column data types
            mismatches = []

            for column, value in user_input_dict.items():
                # Check if the column is required and the value is missing
                if not column_details[column]["nullable"] and (
                    value is None or value == ""
                ):
                    mismatches.append(
                        f"Column '{column}' cannot be NULL because it is NOT NULL."
                    )
                    continue

                expected_type = column_details.get(column, {}).get("type")

                if not expected_type:
                    mismatches.append(
                        f"Column '{column}' does not exist in the table."
                    )
                    continue

                # Check for type mismatches
                if not self.check_type(value, expected_type):
                    mismatches.append(
                        f"Column '{column}' has a type mismatch. Expected {expected_type}, got {type(value).__name__}"
                    )

            # Return any mismatches
            if mismatches:
                return mismatches
            else:
                return "All columns are correctly typed."

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the cursor
            # cursor.close()
            pass

    def check_type(self, value, expected_type):
        if expected_type == "text":
            return isinstance(value, str)
        elif expected_type == "real":
            return isinstance(value, float)
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "character varying" or expected_type == "text":
            return isinstance(value, str)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "numeric":
            return isinstance(value, (int, float))
        elif expected_type == "date":
            return isinstance(
                value, str
            )  # You might want to add more sophisticated date checking
        elif expected_type == "timestamp without time zone":
            return isinstance(
                value, str
            )  # Same as date, check for datetime format if needed
        else:
            # Default to True (any other type comparison can be added as needed)
            return True

    def get_column_types_from_db(self, table_name):
        try:
            query = f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
            """
            self.cur.execute(query)

            # Create the dictionary for column types
            column_types = {}
            for row in self.cur.fetchall():
                column_name, data_type = row
                column_types[column_name] = data_type

            return column_types

        except Exception as e:
            print(f"Error: {e}")
            return {}

    def fetch_chemicals_stock(self):
        try:
            query = "SELECT name FROM chemical_inventory"

            self.cur.execute(query)

            names_results = self.cur.fetchall()

            names = []

            for name in names_results:
                if name[0] is None:
                    names.append("No Name in Database")
                else:
                    names.append(name[0])

            return names
        except Exception as e:
            print("Error: ", e)
            return []

    def get_column_order(self, table_name):
        # Create a connection and cursor to the database

        # Query to fetch column names ordered by their ordinal position
        self.cur.execute(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """,
            (table_name,),
        )

        # Fetch the column names and store them in a list
        column_order = [row[0] for row in self.cur.fetchall()]

        return column_order
    
    def insert_data_into_db(self, table, valid_entries):
        columns = ", ".join(valid_entries.keys())
        values_to_insert = tuple(str(value) if value is not None else None for value in valid_entries.values())
        placeholders = ', '.join(['%s'] * len(values_to_insert))
        try:
            sql_query2 = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
                RETURNING *;
            """

            # self.cur.execute(sql_query, values_to_insert)
            self.cur.execute(sql_query2,values_to_insert)

            inserted_row = self.cur.fetchone()

            # Save changes
            self.conn.commit()

            column_names = [desc[0] for desc in self.cur.description]
            inserted_dict = dict(zip(column_names, inserted_row))

            print("Data inserted successfully.")
            return True
        
        except Exception as e:
            error = f"Error inserting data: {e}"
            self.conn.rollback()
            return error
        finally:
            # self.cur.close()
            # self.conn.close()
            pass

    # USE ONCE - should not be adding tables this way
    # def add_details_table(self):
    #     change_owner_query = "ALTER TABLE chemical_details OWNER TO database_dev;"
    #     self.cur.execute(change_owner_query)
    #     self.conn.commit()
    #     print("Sucessfully changed owner to database_dev")
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
