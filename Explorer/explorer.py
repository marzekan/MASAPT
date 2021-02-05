#!/usr/bin/python3.8

import argparse
import spade
import time
import random
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template

from explorer_utils import run_osint

CGREEN = '\33[32m'
CEND = '\33[0m'

class Explorer(Agent):
    def __init__(self, jid, pwd, target):
        super().__init__(jid, pwd)

        self.role = "Explorer"
        self.target = target

        self.recived_msg: Message
        self.sender: str
        self.osint_info: dict
        self.message_to_send: str

        self.contacts = ["coordinator@localhost"]


    def log(self, message):
        print(f"{CGREEN} {self.role} {CEND}: {message}")

    def on_coordinator_available(peer_jid, stanza):
        pass

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
                self.agent.sender = str(msg.sender)

                print()
                print("Primljenja poruka:", msg.body)
                print()

                self.set_next_state("SendMsg")

            else:
                self.set_next_state("AwaitMsg")

    class SendMsg(State):
        async def run(self):

            if 

            msg = Message(
                to="reporter@localhost",
                body=f"marco",
                metadata={
                    "performative":"inform",
                    "ontology":"security",
                    "target":str(self.agent.target),
                    "osint_info": str(self.agent.osint_info)
                }
            )

            await self.send(msg)

            self.set_next_state("AwaitMsg")

    class InterpretMsg(State):

        # cases:
        #   Coordinator : msg_recived --> Explorer --> Coordinator : osint_info

        async def run(self):

            if self.recived_msg.sender == "coordinator@localhost":
                pass


    class PerformOSINT(State):

        async def run(self):
            # Run OSINT analysis and set results in osint_info
            self.agent.osint_info = run_osint(self.agent.target)

            if self.agent.osint_info == None or len(self.agent.osint_info.keys()) == 0:

                # Try OSINT again after some time, not immediately.
                time.sleep(random.randint(0,5))

                self.set_next_state("PerformOSINT")
            else:
                self.set_next_state("SendMsg")

    class End(State):
        # Runs when agent behaviour finishes.
        async def run(self):
            self.agent.stop()
            spade.quit_spade()

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
        agent_behaviour.add_transition(source="PerformOSINT", dest="SendMsg")
        agent_behaviour.add_transition(source="SendMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="InterpretMsg")
        agent_behaviour.add_transition(source="InterpretMsg", dest="SendMsg")
        agent_behaviour.add_transition(source="InterpretMsg", dest="End")


        self.add_behaviour(agent_behaviour, communication_template)




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Runs explorer agent.")
    parser.add_argument("-jid", type=str, help="Explorer agents JID for XMPP service", default="explorer@localhost")
    parser.add_argument("-pwd", type=str, help="Explorer agents password for XMPP service", default="explorerSecret")
    parser.add_argument("-t", "--target", type=str, help="Pass target address on which to perform OSINT analysis", default="localhost/sqlilabs")

    args = parser.parse_args()

    explorer = Explorer(jid=args.jid, pwd=args.pwd, target=args.target)

    future = explorer.start()
    future.result()

    print(explorer.target)


    input("Press ENTER to exit.\n")

    explorer.stop()
    spade.quit_spade()
