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

from coordinator_utils import exploit_agent

CYELLOW = '\33[33m'
CEND = '\33[0m'

newline = "\n\n"

class Coordinator(Agent):
    def __init__(self, jid, pwd):
        super().__init__(jid, pwd)

        self.role = "Coordinator"
        self.osint_data = None
        self.exploit_agent = None

        self.target: str
        self.recived_msg: Message
        self.sender: str
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
                temp = JID.fromstr(str(msg.sender))
                self.agent.sender = temp.localpart + "@" + temp.domain

                self.set_next_state("InterpretMsg")
                return

            else:
                self.set_next_state("AwaitMsg")

            # If agent has not recieved OSINT data from explorer, send request to explorer.
            if self.agent.osint_data == None:
                self.agent.message_to_send = "give osint"
                self.set_next_state("SendMsg")


    class SendMsg(State):
        async def run(self):

            if self.agent.message_to_send == "give osint":

                msg = Message(
                    to="explorer@localhost",
                    body=f"{self.agent.message_to_send}",
                    metadata={
                        "performative":"inform",
                        "ontology":"security",
                    }
                )

                self.set_next_state("AwaitMsg")

                self.agent.log("Give OSINT sent")

                await self.send(msg)

                return

            elif self.agent.message_to_send == "explorer_conf":
                msg = Message(
                    to="explorer@localhost",
                    body="conf",
                    metadata={
                        "performative":"inform",
                        "ontology":"security",
                    }
                )

                await self.send(msg)

                self.agent.message_to_send = "inform_attackers"

                self.agent.log("Confirmation to Explorer sent")

                self.set_next_state("SendMsg")

                return


            elif self.agent.message_to_send == "inform_attackers":

                if self.agent.exploit_agent == "sqli":

                    msg = Message(
                        to="sqlinjector@localhost",
                        body=f"{self.agent.message_to_send}",
                        metadata={
                            "performative":"inform",
                            "ontology":"security",
                            "target":str(self.agent.target),
                            "recipient":"sqli",
                        }
                    )

                    await self.send(msg)

                    self.agent.log("SQLinjector informed")

                    self.set_next_state("AwaitMsg")

                    return


    class InterpretMsg(State):

        async def run(self):

            # Check if message sender is explorer agent
            if self.agent.sender == "explorer@localhost":

                if self.agent.recived_msg.body == "osint data":

                    self.agent.log("OSINT data recived")

                    self.agent.osint_data = self.agent.recived_msg.metadata["osint_info"]
                    self.agent.target = self.agent.recived_msg.metadata["target"]

                    self.set_next_state("DecideAgent")

                    return

            elif self.agent.sender == "sqlinjector@localhost":

                if self.agent.recived_msg.body == "sql_conf":

                    self.agent.log("SQLinjector conf recived")
                    self.set_next_state("End")

                    return


    class DecideAgent(State):

        async def run(self):

            attacker_agent = exploit_agent(self.agent.osint_data)


            self.agent.target = self.agent.recived_msg.metadata["target"]

            self.agent.exploit_agent = attacker_agent

            self.agent.message_to_send = "explorer_conf"


            self.set_next_state("SendMsg")

            return


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

        agent_behaviour.add_state(name="AwaitMsg", state=self.AwaitMsg(), initial=True)
        agent_behaviour.add_state(name="SendMsg", state=self.SendMsg())
        agent_behaviour.add_state(name="InterpretMsg", state=self.InterpretMsg())
        agent_behaviour.add_state(name="DecideAgent", state=self.DecideAgent())
        agent_behaviour.add_state(name="End", state=self.End())

        agent_behaviour.add_transition(source="DecideAgent", dest="SendMsg")
        agent_behaviour.add_transition(source="SendMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="SendMsg", dest="SendMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="SendMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="InterpretMsg")
        agent_behaviour.add_transition(source="InterpretMsg", dest="DecideAgent")
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

    print("Wait for user interrupts with ctrl+c")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break;


    coordinator.stop()
    spade.quit_spade()
