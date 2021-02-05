import nmap3
import subprocess



# Runs nmap --top-ports shell command and returns its output.
def __get_top_ports(target: str, top_port_num: int):

    # Initialize Nmap object.
    nmap = nmap3.Nmap()

    scan_result = nmap.scan_top_ports(target, top_port_num)

    return scan_result

# Parse top ports shell output, return only open ports.
def __parse_top_ports_output(target: str, shell_output: str):

    info = []

    # Traverse open ports. Return list of open services.
    for item in shell_output[target]["ports"]:

        port_info = {
            "protocol":"",
            "port":"",
            "name":"",
        }

        if item["state"] == "open":

            port_info["protocol"] = item["protocol"]
            port_info["port"] = item["portid"]
            port_info["name"] = item["service"]["name"]

            info.append(port_info)

    return list(info)



def __run_harvester():

    shell_output = subprocess.run(["theHarvester", "-d", "localhost", "-l", "10", "-b", "bing"], capture_output=True, text=True)

    return shell_output

def __parse_harvester_output(shell_output: str):

    pass

#---------------- PUBLIC FUNCTIONS --------------------#

# Returns dictionary with osint results.
def run_osint(target: str) -> dict:

    osint_data = {
        "emails":[],
        "hosts_found":[],
        "open_ports":[]
    }

    out = __get_top_ports(target, 100)

    osint_data["open_ports"] = __parse_top_ports_output(target, out)

    return osint_data
