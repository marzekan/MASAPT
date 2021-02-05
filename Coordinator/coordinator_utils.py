
import json

common_db_ports = {
    "mysql":"3306",
    "postgres":"5432",
    "mongodb":"27017",
    "neo4j":"7474"
    }

agents = {
    "sqli":"sql_inform",
    "dos":"dos_inform"
}

osint_info_test = "{'emails':[], 'hosts_found':[], 'open_ports':[{'protocol':'tcp', 'port':'3306', 'name':'mysql'}]}"

def exploit_agent(osint_data: str):

    format_osint_data = osint_data.replace("'", "\"")
    format_osint_data = json.loads(format_osint_data)

    for port in format_osint_data["open_ports"]:
        if port["port"] in common_db_ports.values():
            return agents["sqli"]
