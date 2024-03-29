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

from reporter_utils import build_report, save_report_to_txt

CVIOLET = '\33[35m'
CEND = '\33[0m'
CBOLD = '\33[1m'

newline = "\n\n"

class Reporter(Agent):
    def __init__(self, jid, pwd):
        super().__init__(jid, pwd)

        self.role = "Reporter"
        self.final_report = None
        self.recived_data_dump = None

        self.recived_msg: Message
        self.sender: str
        self.message_to_send: str

        self.count_end_messages = 0

        self.contacts = ["sqlinjector@localhost", "dos@localhost"]


    def log(self, message):
        print(f"{CVIOLET} {self.role} {CEND}: {message}")


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

            # If agent has not recieved data dump from sqlinjector, send request to sqlinjector for that data dump again.
            if self.agent.recived_data_dump == None:
                self.agent.message_to_send = "give data dump"
                self.set_next_state("SendMsg")


    class SendMsg(State):
        async def run(self):

            if self.agent.message_to_send == "give data dump":

                msg = Message(
                    to="sqlinjector@localhost",
                    body=f"{self.agent.message_to_send}",
                    metadata={
                        "performative":"inform",
                        "ontology":"security",
                    }
                )

                self.set_next_state("AwaitMsg")

                self.agent.log("'Give data dump' request sent")

                await self.send(msg)

                time.sleep(3)

                return

            elif self.agent.message_to_send == "sqli_conf":
                msg = Message(
                    to="sqlinjector@localhost",
                    body="reporter_conf",
                    metadata={
                        "performative":"inform",
                        "ontology":"security",
                    }
                )

                await self.send(msg)

                self.agent.message_to_send = "end"

                self.agent.log("Confirmation to SQLinjector sent")

                self.set_next_state("End")

                return


    class InterpretMsg(State):

        async def run(self):

            # Check if message sender is coordinator agent
            if self.agent.sender == "sqlinjector@localhost":

                if self.agent.recived_msg.body == "inform_reporter":

                    self.agent.log("Data dump recived")

                    self.agent.recived_data_dump = str(self.agent.recived_msg.metadata["data_dump"])

                    self.set_next_state("PerformReporting")

                    return


    class PerformReporting(State):

        async def run(self):

            final_report = build_report(sqli_results=self.agent.recived_data_dump)

            self.agent.final_report = final_report

            save_report_to_txt(self.agent.final_report)

            self.agent.message_to_send = "sqli_conf"

            self.set_next_state("SendMsg")

            return


    class End(State):
        # Runs when agent behaviour finishes.
        async def run(self):

            if self.agent.count_end_messages < 1:
                self.agent.log("Shutting down")
                self.agent.count_end_messages += 1

                print(3*"\n")
                self.agent.log("Showing generated report:\n")

                print(self.agent.final_report)

                print("Report can be found at: ", CBOLD, "Reporter/reports/", CEND, "\n\n")

            self.set_next_state("End")
            time.sleep(2)

        # async def run(self):
        #     self.agent.log("Shutting down")
        #     self.agent.stop()
        #     spade.quit_spade()


    async def setup(self):
        self.log("Starting...")

        communication_template = Template(
            metadata={"ontology":"security"}
        )

        agent_behaviour = self.Behaviour()

        agent_behaviour.add_state(name="AwaitMsg", state=self.AwaitMsg(), initial=True)
        agent_behaviour.add_state(name="SendMsg", state=self.SendMsg())
        agent_behaviour.add_state(name="InterpretMsg", state=self.InterpretMsg())
        agent_behaviour.add_state(name="PerformReporting", state=self.PerformReporting())
        agent_behaviour.add_state(name="End", state=self.End())

        agent_behaviour.add_transition(source="PerformReporting", dest="SendMsg")
        agent_behaviour.add_transition(source="SendMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="SendMsg", dest="SendMsg")
        agent_behaviour.add_transition(source="SendMsg", dest="End")
        agent_behaviour.add_transition(source="AwaitMsg", dest="AwaitMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="SendMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="InterpretMsg")
        agent_behaviour.add_transition(source="InterpretMsg", dest="PerformReporting")
        agent_behaviour.add_transition(source="InterpretMsg", dest="End")
        agent_behaviour.add_transition(source="End", dest="End")


        self.add_behaviour(agent_behaviour, communication_template)




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Runs reporter agent. He creates reports from performed exploits.")
    parser.add_argument("-jid", type=str, help="Reporter agents JID for XMPP service", default="reporter@localhost")
    parser.add_argument("-pwd", type=str, help="Reporter agents password for XMPP service", default="reporterSecret")

    args = parser.parse_args()

    reporter = Reporter(jid=args.jid, pwd=args.pwd)

    future = reporter.start()
    future.result()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break


    reporter.stop()
    spade.quit_spade()
