#!/usr/bin/python3.8

import argparse
import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template



class Explorer(Agent):
    def __init__(self, jid, pwd):
        super().__init__(jid, pwd)

        self.role = "Explorer"

        self.recived_msg: Message
        self.sender: str

    def log(self, message):
        print(f"{self.role}: {message}")

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

                self.set_next_state("SendResponse")
            
            else:
                self.set_next_state("AwaitMsg")

    class SendResponse(State):
        async def run(self):

            msg = Message(
                to="reporter@localhost",
                body=f"Bok Reporter",
                metadata={
                    "performative":"inform",
                    "ontology":"security",
                }
            )

            await self.send(msg)

            self.set_next_state("AwaitMsg")
            


    async def setup(self):
        self.log("Starting...")

        communication_template = Template(
            metadata={"ontology":"security"}
        )

        agent_behaviour = self.Behaviour()

        agent_behaviour.add_state(name="AwaitMsg", state=self.AwaitMsg())
        agent_behaviour.add_state(name="SendResponse", state=self.SendResponse(), initial=True)

        agent_behaviour.add_transition(source="AwaitMsg", dest="SendResponse")
        agent_behaviour.add_transition(source="SendResponse", dest="AwaitMsg")
        agent_behaviour.add_transition(source="AwaitMsg", dest="AwaitMsg")


        self.add_behaviour(agent_behaviour, communication_template)

        
    


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Runs explorer agent.")
    parser.add_argument("-jid", type=str, help="Explorer agents JID for XMPP service", default="explorer@localhost")
    parser.add_argument("-pwd", type=str, help="Explorer agents password for XMPP service", default="explorerSecret")
    
    args = parser.parse_args()

    explorer = Explorer(jid=args.jid, pwd=args.pwd)
    
    explorer.start()
    

    input("Press ENTER to exit.\n")

    explorer.stop()
    spade.quit_spade()



