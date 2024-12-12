import yaml
from sqlalchemy import create_engine, Table, MetaData, select, inspect

class Database:
    def __init__(self):

        self.inventory_tables_data = "src/models/database.yaml"

        with open(self.inventory_tables_data, 'r') as file:
            self.inventory_type_tables = yaml.safe_load(file)['INVENTORY_TYPES']
        
        #Initialize SQL DB URL
        self.db_url = 'postgresql+psycopg2://postgres:team3#@100.91.167.126:5432/inventory_management'
        self.engine = create_engine(self.db_url)

    
    def get_inventory_table_types(self):
        return self.inventory_type_tables


    def get_latest_barcode_id(self, table_type):
        if 'product' in table_type:
            table_type = 'batch_inventory'

        sanitized_table_type = table_type.replace(" ", "_").lower()

        # Attempt to retrieve the barcode ID
        print(f"Attempting to retrieve latest {sanitized_table_type} ID...")

        # Use inspect to check if the table exists
        inspector = inspect(self.engine)
        if sanitized_table_type not in inspector.get_table_names():
            print(f"{sanitized_table_type} not found in database")
            return None

        # Reflect the table from the database
        table = Table(sanitized_table_type, autoload_with=self.engine)

        print(table)
        # Use SQLAlchemy to execute the query directly (no session)
        stmt = select([table.c.id]).order_by(table.c.id.desc()).limit(1)
        with self.engine.connect() as connection:
            result = connection.execute(stmt).fetchone()

        if result:
            print(f"Latest {sanitized_table_type} ID retrieved")
            return result[0]
        else:
            print(f"No records found in {sanitized_table_type}")
            return None