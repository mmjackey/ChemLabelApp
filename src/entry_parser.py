from dateutil import parser

class EntryParser:
    def __init__(self,db):
        super().__init__()
        self.database = db
        
    def convert_value_types(self,entries,tb):
        expected_types = {}
        types = self.database.get_column_types_from_db(tb)
        for name, entry in entries.items():
            for column, expected_type in types.items(): 
                if name.lower() in column.lower(): 
                    expected_types[column]= expected_type
        return expected_types

    def convert_to_types(self,user_entries,expected_types):
        
        if not user_entries: return

        for key, value in user_entries.items():
            if value == "": continue
            #print(f"Key:{key} and Value:{value} | Expected type: {expected_types.get(key)}")
            expected_type = expected_types.get(key)
            
            if expected_type == 'real':
                try:
                    user_entries[key] = float(value) 
                except ValueError:
                    return f"Error: The value '{value}' for '{key}' could not be converted to 'real'. Please provide a valid number."
            elif expected_type == 'integer':
                try:
                    user_entries[key] = int(value)
                except ValueError:
                    return f"Error: The value '{value}' for '{key}' could not be converted to 'int'. Please provide a valid integer."
            elif expected_type == 'character varying' or expected_type == 'text':
                try:
                    user_entries[key] = str(value)
                except ValueError:
                    return f"Error: The value '{value}' for '{key}' could not be converted to 'str'. Please provide a valid integer."
            elif expected_type == 'bigint':
                try:
                    user_entries[key] = int(value) 
                except ValueError:
                    return f"Error: The value '{value}' for '{key}' could not be converted to 'bigint'. Please provide a valid integer."
            elif expected_type == 'timestamp with timezone':
                try:
                    user_entries[key] = parser.parse(value)
                except (ValueError, TypeError) as e:
                    return f"Error: The value '{value}' for '{key}' could not be converted to '{expected_type}'. Please provide a valid value."

            else:
                pass

        return user_entries