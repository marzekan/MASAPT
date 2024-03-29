#!/usr/bin/python3.8

import argparse
import spade
import time
import random
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template

from aioxmpp import JID
from contextlib import suppress

from explorer_utils import run_osint

CGREEN = '\33[32m'
CEND = '\33[0m'

class Explorer(Agent):
    def __init__(self, jid, pwd, target):
        super().__init__(jid, pwd)

        self.role = "Explorer"
        self.target = target

        if "localhost" in target:
            self.target_ip = "127.0.0.1"

        self.recived_msg: Message
        self.sender: str
        self.osint_info: dict
        self.message_to_send: str

        self.count_end_messages = 0

        self.contacts = ["coordinator@localhost"]


    def log(self, message):
        print(f"{CGREEN} {self.role} {CEND}: {message}")

    class Behaviour(FSMBehaviour):
        async def on_start(self):
            pass
        async def on_end(self):
            pass


    class AwaitMsg(State):
        async def run(self):

            msg = None
            msg = await self.receive()

            if msg:

                self.agent.recived_msg = msg
                temp = JID.fromstr(str(msg.sender))
                self.agent.sender = temp.localpart + "@" + temp.domain

                self.set_next_state("InterpretMsg")

            else:
                self.set_next_state("AwaitMsg")


    class SendMsg(State):
        async def run(self):

            # If the message to send is 'osint data' that means that coordinator has confirmed that he is available to recive the data,
            if self.agent.message_to_send == "osint data":
                # If coordinator is online send him OSINT data.
                msg = Message(
                    to=str(self.agent.sender),
                    body=f"{self.agent.message_to_send}",
                    metadata={
                        "performative":"inform",
                        "ontology":"security",
                        "target":str(self.agent.target),
                        "osint_info": str(self.agent.osint_info),
                    }
                )

                self.agent.log("OSINT data sent")

                await self.send(msg)

                self.set_next_state("AwaitMsg")


    class InterpretMsg(State):

        async def run(self):

            # Check if message sender is coordinator agent
            if self.agent.sender == "coordinator@localhost":

                if self.agent.recived_msg.body == "give osint":
                    self.agent.message_to_send = "osint data"
                    self.set_next_state("SendMsg")

                # Coordinator confirms that he got the messasge,.
                elif self.agent.recived_msg.body == "conf":
                    self.agent.log("Coordinator conf recived")

                    # If coordinator confirms that he got the payload - Explorer agent stops.
                    self.set_next_state("End")
                    return



    class PerformOSINT(State):

        async def run(self):

            # Run OSINT analysis and set results in osint_info
            self.agent.osint_info = run_osint(self.agent.target_ip)

            # If run_osint has failed or the target is offline.
            if self.agent.osint_info == None or len(self.agent.osint_info.keys()) == 0:

                # Try OSINT again after some time, not immediately.
                time.sleep(random.randint(0,5))

                self.set_next_state("PerformOSINT")

            # If data has been gathered successfully then send that to coordinator.
            else:
                self.agent.log("OSINT completed")
                self.agent.message_to_send = "osint data"
                self.set_next_state("AwaitMsg")

    class End(State):
        # Runs when agent behaviour finishes.
        async def run(self):

            if self.agent.count_end_messages < 1:
                self.agent.log("Shutting down")
                self.agent.count_end_messages += 1

            self.set_next_state("End")
            time.sleep(2)
            # await self.agent.stop()
            # spade.quit_spade()

    async def setup(self):
        self.log("Starting...")

        communication_template = Template(
            metadata={"ontology":"security"}
        )

        agent_behaviour = self.Behaviour()

        agent_behaviour.add_state(name="AwaitMsg", state=self.AwaitMsg())
        agent_behaviour.add_state(name="SendMsg", state=self.SendMsg())
        agent_behaviour.add_state(name="InterpretMsg", state=self.InterpretMsg())
        agent_behaviour.add_state(name="PerformOSINT", state=self.PerformOSINT(), initial=True)
        agent_behaviour.add_state(name="End", state=self.End())

        agent_behaviour.add_transition(source="PerformOSINT", dest="PerformOSINT")
        agent_behaviour.add_transition(source="PerformOSINT", dest="AwaitMsg")
        agent_behaviour.add_transition(source="SendMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="InterpretMsg")
        agent_behaviour.add_transition(source="InterpretMsg", dest="SendMsg")
        agent_behaviour.add_transition(source="InterpretMsg", dest="End")
        agent_behaviour.add_transition(source="End", dest="End")


        self.add_behaviour(agent_behaviour, communication_template)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Runs explorer agent.")
    parser.add_argument("-jid", type=str, help="Explorer agents JID for XMPP service", default="explorer@localhost")
    parser.add_argument("-pwd", type=str, help="Explorer agents password for XMPP service", default="explorerSecret")
    parser.add_argument("-t", "--target", type=str, help="Pass target address on which to perform OSINT analysis", default="localhost/sqlilabs/Less-1")

    args = parser.parse_args()

    explorer = Explorer(jid=args.jid, pwd=args.pwd, target=args.target)

    future = explorer.start()
    future.result()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    explorer.stop()
    spade.quit_spade()
