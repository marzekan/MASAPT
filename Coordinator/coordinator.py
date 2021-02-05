#!/usr/bin/python3.8

import argparse
import spade
import time
import random
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template

from coordinator_utils import exploit_agent

CYELLOW = '\33[33m'
CEND = '\33[0m'

class Coordinator(Agent):
    def __init__(self, jid, pwd):
        super().__init__(jid, pwd)

        self.role = "Coordinator"

        self.target: str
        self.recived_msg: Message
        self.sender: str
        self.osint_data: str
        self.message_to_send: str


        self.contacts = ["sqlinjector@localhost", "dos@localhost"]


    def log(self, message):
        print(f"{CYELLOW} {self.role} {CEND}: {message}")


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

                self.set_next_state("InterpretMsg")

            else:
                self.set_next_state("AwaitMsg")


    class SendMsg(State):
        async def run(self):

            # If message to send is 'marco' that means that coordinator still hasn't confirmed that he is available.
            if self.agent.message_to_send == "marco":

                msg = Message(
                    to="coordinator@localhost",
                    body=f"{self.agent.message_to_send}",
                    metadata={
                        "performative":"inform",
                        "ontology":"security",
                    }
                )

                self.agent.log("marco sent")

                # If message is still 'marco' send marco until coordinator respondes
                self.set_next_state("SendMsg")

                # Check if coordinator is available every second.
                time.sleep(1)

                await self.send(msg)

            # If the message to send is 'osint data' that means that coordinator has confirmed that he is available to recive the data,
            elif self.agent.message_to_send == "osint data":
                # If coordinator is online send him OSINT data.
                msg = Message(
                    to="coordinator@localhost",
                    body=f"{self.agent.message_to_send}",
                    metadata={
                        "performative":"inform",
                        "ontology":"security",
                        "target":str(self.agent.target),
                        "osint_info": str(self.agent.osint_info)
                    }
                )

                self.agent.log("OSINT data sent")

                await self.send(msg)

                self.set_next_state("AwaitMsg")


    class InterpretMsg(State):

        async def run(self):

            # Check if message sender is explorer agent
            if self.agent.recived_msg.sender == "explorer@localhost":

                # Explorer checks if coordinator is available.
                if self.recived_msg.body == "marco":
                    self.agent.log("marco recived")

                    # If coordinator is available - send him OSINT data.
                    self.agent.message_to_send = "polo"
                    self.set_next_state("SendMsg")

                    return

                # Coordinator confirms that he got the messasge,.
            elif self.agent.recived_msg.body == "osint data":

                    self.agent.log("OSINT data recived")

                    # If explorer has sent OSINT results - send confirmation
                    self.agent.message_to_send = "conf"
                    self.set_next_state("SendMsg")

                    return



    class DecideAgent(State):

        async def run(self):

            next_agent = exploit_agent(self.agent.osint_data)

            if next_agent == None or next_agent == "" or next_agent not in self.agent.contacts:

                self.set_next_state("DecideAgent")

            else:
                self.agent.message_to_send = "sqli ping"
                self.set_next_state("SendMsg")

    class End(State):
        # Runs when agent behaviour finishes.
        async def run(self):
            self.agent.log("Shutting down")
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
        agent_behaviour.add_state(name="DecideAgent", state=self.DecideAgent(), initial=True)
        agent_behaviour.add_state(name="End", state=self.End())

        agent_behaviour.add_transition(source="DecideAgent", dest="DecideAgent")
        agent_behaviour.add_transition(source="DecideAgent", dest="SendMsg")
        agent_behaviour.add_transition(source="SendMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="SendMsg", dest="SendMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="InterpretMsg")
        agent_behaviour.add_transition(source="InterpretMsg", dest="SendMsg")
        agent_behaviour.add_transition(source="InterpretMsg", dest="End")


        self.add_behaviour(agent_behaviour, communication_template)




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Runs coordinator agent. He coordinates other exploit agents.")
    parser.add_argument("-jid", type=str, help="Coordinator agents JID for XMPP service", default="coordinator@localhost")
    parser.add_argument("-pwd", type=str, help="Coordinator agents password for XMPP service", default="coordinatorSecret")

    args = parser.parse_args()

    coordinator = Coordinator(jid=args.jid, pwd=args.pwd)

    future = coordinator.start()
    future.result()

    input("Press ENTER to exit.\n")

    coordinator.stop()
    spade.quit_spade()
