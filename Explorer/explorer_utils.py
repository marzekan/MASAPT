import nmap3
import subprocess

target = "127.0.0.1"

osint_data = {
    "emails":[],
    "hosts_found":[],
    "open_ports":[]
}

# Runs nmap --top-ports shell command and returns its output.
def get_top_ports(top_port_num: int):

    # Initialize Nmap object.
    nmap = nmap3.Nmap()

    scan_result = nmap.scan_top_ports(target, top_port_num)
    
    return scan_result

# Parse top ports shell output, return only open ports.
def parse_top_ports_output(shell_output: str):
    
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



def run_harvester():

    shell_output = subprocess.run(["theHarvester", "-d", "kali.org", "-l", "10", "-b", "google"], capture_output=True, text=True)

    return shell_output

def parse_harvester_output(shell_output: str):

    shell_output_split = shell_output.split("\n")

    emails = []
    hosts = []

    def find_emails(item:str):

        next_item = shell_output_split[shell_output_split.index(item)+1]

        # If first char is a letter.
        if next_item[0].isalpha() and next_item[0] != '-':
            emails.append(next_item)
            find_emails()
        else:
            return emails

    def find_hosts(item:str):

        next_item = shell_output_split[shell_output_split.index(item)+1]

        # If first char is a letter.
        if next_item[0].isalpha() and next_item[0] != '-':
            hosts.append(next_item)
            find_hosts()
        else:
            return hosts

    # print(shell_output_split)
    # return 

    for item in shell_output_split:

        if "Emails" in item:
            print(item)
            find_emails(item)
        
        elif "Hosts" in item:
            print(item)
            find_hosts(item)

    return emails, hosts

if __name__ == "__main__":

    # out = get_top_ports(100)

    # res = parse_top_ports_output(out)

    harvest_out = run_harvester()

    emails, hosts = parse_harvester_output(harvest_out.stdout)


    from pprint import pprint
    pprint(emails)
    print()
    pprint(hosts)