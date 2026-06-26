from multiprocessing import Process, Queue, Event
from enum import Enum
from ollama import Client
from langchain.agents import create_agent

client = Client()

class ToolRoute(str, Enum):
    SHIP = "SHIP"
    INFO = "INFO"
    NEUTRONS = "NEUTRONS"
    NONE = "NONE"


ROUTER_PROMPT = """
You are a request classifier.

The context is the video game Elite Dangerous.

Classify the user's message into exactly one category.

Possible categories:

SHIP
INFO
NEUTRONS
NONE

Definitions:

SHIP
- Any ship control actions
- throttle, supercruise, setspeedzero
- cargo scoop, night vision, landing gear

INFO
- Any questions about game lore
- Game information
- People, places, exobiology, etc

NEUTRONS
- Used for finding efficient routes to star systems
- Find nearest neutron star

NONE
- Fallback when input doesn't match a category and should not be processed

Return ONLY the category name.
No explanations.
No punctuation.
"""

def select_tool2(user_message: str) -> ToolRoute:
    response = client.chat(
        model="gemma2b:latest",

        messages=[
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": user_message},
        ],
        format={
            "type": "string",
            "enum": [
                "SHIP",
                "INFO",
                "NEUTRONS",
                "NONE"
            ]
        },
        options={
            "temperature": 0,
            "num_predict": 3
        }
    )

    try:
        return ToolRoute(
            response["message"]["content"].strip()
        )
    except ValueError:
        return ToolRoute.NONE

route = select_tool2(
    "What was I working on yesterday?"
)

print(route)

user_message = "what meetings do I have?"

route = select_tool2(user_message)

match route:
    case ToolRoute.MEMORY:
        # tool_result = memory_search(user_message)
        print("mem")
    case ToolRoute.WEB:
        # tool_result = web_search(user_message)
        print("web")
    case ToolRoute.CALENDAR:
        # tool_result = calendar_search(user_message)
        print("cal")

    case ToolRoute.NONE:
        tool_result = None
        print("none")


#
#
# class OllamaRunnerQ:
#
#     def __init__(self, llm_recv: Queue, to_tts: Queue, shutdown_event: Event, shared_state: dict):
#         self.llm_recv = llm_recv
#         self.to_tts = to_tts
#         self.shutdown_event = shutdown_event
#         self.name = "OllamaRunnerQ"
#         self.shared = shared_state
#         self.llm = ChatOllama(
#             # model="gemma4-pc:latest",
#             model="gemma2b:latest",
#             validate_model_on_init=True,
#             temperature=0.7)
#
#         self.message_count = 0
#         self.action = InputControls()
#
#         base = self.system_prompts("base")
#
#         system_prompt = SystemMessage(content=base)
#
#         self.memory = InMemorySaver()
#         self.config = {
#             "configurable": {
#                 "thread_id": "user-123"
#             }
#         }
#
#         self.rag_agent = create_agent(self.llm, system_prompt=system_prompt)
#         self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
#         self.vectorstore = Chroma(
#             persist_directory="./elite_wiki_db",
#             embedding_function=self.embeddings,)
#         self.retriever = self.vectorstore.as_retriever(
#             search_kwargs={"k": 5})
#
#         tool_prompt = self.system_prompts("tool_prompt2")
#
#         # self.tool_agent = create_agent(self.llm, tools=self.agent_router(),
#         #                                checkpointer=self.memory, system_prompt=tool_prompt)
#         self.tool_agent = create_agent(self.llm, tools=self.agent_router(), system_prompt=tool_prompt)
#         self.to_tts.put("loading AI")
#
#
#     def run(self):
#         print("Ollama started")
#         try:
#             while not self.shutdown_event.is_set():
#                 try:
#                     request = self.llm_recv.get(timeout=0.5)
#                     print(f"[{self.name}] Received request: {request}")
#                     if request:
#                         if BASIC_MODE:
#                             print("basic mode call")
#                             self.call_llm_chat(request)
#                         else:
#                             self.call_llm_advanced(request)
#
#                 except Exception as e:
#                     pass
#
#         except Exception as e:
#             print(f"[{self.name}] Error: {e}")