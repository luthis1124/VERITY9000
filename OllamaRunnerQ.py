from multiprocessing import Process, Queue, Event
import multiprocessing
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain.agents import create_agent
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from torch._export.passes import replace_with_hop_pass_util

from InputControls import InputControls
from ollama import Client
from enum import Enum

import json
from langchain_core.output_parsers import JsonOutputParser

"""
{'messages': 
[HumanMessage(content='what are we doing today?', additional_kwargs={}, response_metadata={}, id='85181e40-1097-42ad-bbf2-0b8ee7428e0b'), 
AIMessage(content='Status quo maintained. Awaiting mission parameters.', additional_kwargs={}, response_metadata={'model': 'gemma2b:latest', 'created_at': '2026-06-17T07:21:11.850867111Z', 'done': True, 'done_reason': 'stop', 'total_duration': 4017806711, 'load_duration': 367854111, 'prompt_eval_count': 396, 'prompt_eval_duration': 47744000, 'eval_count': 371, 'eval_duration': 3598530000, 'logprobs': None, 'model_name': 'gemma2b:latest', 'model_provider': 'ollama'}, id='lc_run--019ed474-89f7-7323-8b64-c707018f05a9-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 396, 'output_tokens': 371, 'total_tokens': 767}), 
HumanMessage(content="it's uh, too dark.", additional_kwargs={}, response_metadata={}, id='71bf5660-8923-44e7-adf5-c1dc134ddc0e'), 
AIMessage(content='Deploying night vision now.', additional_kwargs={}, response_metadata={'model': 'gemma2b:latest', 'created_at': '2026-06-17T07:21:33.630749326Z', 'done': True, 'done_reason': 'stop', 'total_duration': 4461982255, 'load_duration': 363711467, 'prompt_eval_count': 423, 'prompt_eval_duration': 44789000, 'eval_count': 420, 'eval_duration': 4049649000, 'logprobs': None, 'model_name': 'gemma2b:latest', 'model_provider': 'ollama'}, id='lc_run--019ed474-dd4f-7883-818d-6b9dbfcb0a9a-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 423, 'output_tokens': 420, 'total_tokens': 843})]}

"""


class ToolRoute(str, Enum):
    SHIP = "SHIP"
    INFO = "INFO"
    NEUTRONS = "NEUTRONS"
    STATION_SERVICES = "STATION_SERVICES"
    POINT_OF_INTEREST = "POINT_OF_INTEREST"
    RARE_COMMODITIES = "RARE_COMMODITIES"
    NONE = "NONE"

# BASIC_MODE = True
BASIC_MODE = False


ROUTER_PROMPT = """
You are a strict classifier for Elite Dangerous.

Classify the user input into EXACTLY ONE category. 
Do NOT explain. Do NOT think out loud. Do NOT add any extra text.

Possible categories:

SHIP
INFO
NEUTRONS
STATION_SERVICES
POINT_OF_INTEREST
NONE

Definitions:

POINT_OF_INTEREST
- Used to find nearest point of interest
- Check and give point of interest info for current system

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

RARE_COMMODITIES
- Use this tool if user mentions:
rare commodities
commodities
rare goods
goods 
- Used to find stations that sell rare commodities (rare goods)

STATION_SERVICES
- Used for finding the nearest station with the specified service
Service names:
Apex Interstellar Transport
Bartender
Black Market
Contacts
Crew Lounge
Fleet carrier administration
Fleet carrier vendor
Frontline Solutions
Interstellar Factors Contact
Material Trader
Missions
Pioneer Supplies
Refuel
Repair
Restock
Search and Rescue
Technology Broker
Tuning
Universal Cartographics
Vista Genomics
- etc (If the user asks for a station with some service, choose this tool)

NONE
- Fallback when input doesn't match a category and should not be processed.

Respond with valid JSON only and nothing else:
{"category": "RARE_COMMODITIES"}"""
#
# Return ONLY the category name.
# No explanations.
# No punctuation.
# """

class OllamaRunnerQ:

    def __init__(self, llm_recv: Queue, to_tts: Queue, shutdown_event: Event, shared_state: dict):
        self.llm_recv = llm_recv
        self.to_tts = to_tts
        self.shutdown_event = shutdown_event
        self.name = "OllamaRunnerQ"
        self.shared = shared_state
        self.llm = ChatOllama(
            # model="gemma4-pc:latest",
            model="gemma2b:latest",
            validate_model_on_init=True,
            temperature=0.7)

        self.message_count = 0
        self.action = InputControls()

        base = self.system_prompts("base")

        system_prompt = SystemMessage(content=base)

        self.memory = InMemorySaver()
        self.config = {
            "configurable": {
                "thread_id": "user-123"
            }
        }

        self.rag_agent = create_agent(self.llm, system_prompt=system_prompt)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vectorstore = Chroma(
            persist_directory="./elite_wiki_db",
            embedding_function=self.embeddings,)
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5})

        tool_prompt = self.system_prompts("tool_prompt2")

        # self.tool_agent = create_agent(self.llm, tools=self.agent_router(),
        #                                checkpointer=self.memory, system_prompt=tool_prompt)
        self.tool_agent = create_agent(self.llm, tools=self.agent_router(), system_prompt=tool_prompt)
        self.poi_agent = create_agent(self.llm, tools=self.poi_agent_router(), system_prompt=tool_prompt)
        self.services_agent = create_agent(self.llm, tools=self.service_agent_router(), system_prompt=tool_prompt)

        self.client = Client()

        self.to_tts.put("loading AI")


    def run(self):
        print(f"[{self.name}] Process started (PID: {multiprocessing.current_process().pid})")
        try:
            while not self.shutdown_event.is_set():
                try:
                    request = self.llm_recv.get(timeout=0.5)
                    print(f"[{self.name}] Received request: {request}")
                    if request:
                        if BASIC_MODE:
                            print("basic mode call")
                            self.call_llm_chat(request)
                        else:
                            # self.call_llm_advanced(request)
                            self.call_llm_tool(request)

                except Exception as e:
                    pass

        except Exception as e:
            print(f"[{self.name}] Error: {e}")

    def select_tool(self, user_message: str) -> ToolRoute:
        response = self.client.chat(
            model="gemma2b:latest",
            # model="gemma4-pc:latest",
            # model="qwen3:4b",
            messages=[
                {"role": "system", "content": ROUTER_PROMPT},
                {"role": "user", "content": user_message},
            ],
            # format={
            #     "type": "string",
            #     "enum": [
            #         "SHIP",
            #         "INFO",
            #         "NEUTRONS",
            #         "STATION_SERVICES",
            #         "POINT_OF_INTEREST",
            #         "RARE_COMMODITIES",
            #         "NONE"
            #     ]
            # },
            # options={
            #     "temperature": 0.5,
            #     "num_predict": 15 #3
            # }
            format={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["SHIP", "INFO", "NEUTRONS", "STATION_SERVICES", "POINT_OF_INTEREST",
                                 "RARE_COMMODITIES", "NONE"]
                    }
                },
                "required": ["category"]
            },
            options={
                "temperature": 0.0,  # Very important for classification
                "num_predict": 100,
                "top_p": 0.9,
            },
            think=False
        )

        print("toolroute says " + str(response))

        # try:
        #     return ToolRoute(
        #         response["message"]["content"].strip()
        #     )
        # except ValueError:
        #     return ToolRoute.NONE

        try:
            content = response.message.content.strip()

            # Parse JSON
            data = json.loads(content)

            # Extract category (support different possible key names)
            category = data.get("category") or data.get("Category") or data.get("tool")

            if category:
                category = category.strip().upper()
                return ToolRoute(category)  # This will raise ValueError if invalid

        except (json.JSONDecodeError, ValueError, KeyError, TypeError):
            pass  # Fall through to NONE

        return ToolRoute.NONE

    def call_llm_tool(self, user_message):
        route = self.select_tool(user_message)

        match route:
            case ToolRoute.SHIP:
                self.Ship(user_message)
            case ToolRoute.INFO:
                self.call_llm_chat(user_message)
            case ToolRoute.NEUTRONS:
                self.Neutron()
            case ToolRoute.POINT_OF_INTEREST:
                self.call_llm_poi(user_message)
            case ToolRoute.STATION_SERVICES:
                self.call_llm_services(user_message)
            case ToolRoute.RARE_COMMODITIES:
                self.call_llm_services(user_message)
            case ToolRoute.NONE:
                print("no llm action matched")

    def Ship(self, message):
        self.call_llm_advanced(message)

    def Neutron(self):
        print("chose neutron functions")

        print("system is: " + self.shared["system_name"])

        if not self.shared["system_name"]:
            self.shared["system_name"] = "Sol"

        from DBTools import DBTools
        import subprocess
        db = DBTools()
        neutron_single = db.find_nearest_neutron(player_coords=self.shared["star_pos"], limit=1,
                                                 current_system=self.shared["system_name"])

        galmap_name = neutron_single[0]["name"]

        self.to_tts.put("The nearest neutron star is " + galmap_name)

        subprocess.run(
            ["wl-copy"],
            input=galmap_name,
            text=True,
            check=True
        )

    def call_llm_services(self, user_input: str):
        human_message = HumanMessage(content=user_input)
        result = self.services_agent.invoke({"messages": [human_message]})
        print("ai says:" + result["messages"][-1].content)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)
        self.analyze_agent_response(result)

    def service_agent_router(self):
        @tool
        def visited_systems():
            """
            returns a list of systems recently visited
            """
            return self.shared["visited_systems"]

        @tool
        def visited_systems_with_rare_goods():
            """
            returns a list of systems with rare commodities (rare goods) recently visited
            """
            return self.shared["visited_rare_goods"]

        @tool
        def find_station_with_service(service):
            """
            Input: service name
            Used to find the nearest station with x service.
            Returns a list of stations, distance to station, and system names.

            The user will not want to travel to stations with an arrival distance of greater than 100,000
            If the user is in the same system as a service, they probably do not want the service in that system.
            Service names:
            Apex Interstellar Transport
            Bartender
            Black Market
            Contacts
            Crew Lounge
            Fleet carrier administration
            Fleet carrier vendor
            Frontline Solutions
            Interstellar Factors Contact
            Material Trader
            Missions
            Pioneer Supplies
            Refuel
            Repair
            Restock
            Search and Rescue
            Technology Broker
            Tuning
            Universal Cartographics
            Vista Genomics
            """

            from DBTools import DBTools
            db = DBTools()

            player_pos = self.shared["star_pos"]
            stations = db.find_nearest(player_coords=player_pos, limit=4, service=service)

            for i, station in enumerate(stations, 1):
                if station.get('systemName'):
                    import subprocess

                    subprocess.run(
                        ["wl-copy"],
                        input=station.get('systemName'),
                        text=True,
                        check=True
                    )
                    break

            return stations

        @tool
        def find_nearest_rare_goods():
            """
            Used to find the nearest station that sells rare commodities.
            The user may interchange the words goods and commodities.

            Returns a list of stations, distance to station, and system names.
            The user will not want to travel to stations with an arrival distance of greater than 100,000

            Do not give full lightyear distance, round it to the nearest ones, and ignore any decimal places.

            """
            from DBTools import DBTools
            db = DBTools()

            print("current system is: " + self.shared["system_name"])
            player_pos = self.shared["star_pos"]
            stations = db.find_nearest_rares(player_coords=player_pos, limit=10,
                                             current_system=self.shared["system_name"])

            for i, station in enumerate(stations, 5):
                print("checking system: " + str(station.get('systemName')))
                if station.get('systemName'):
                    import subprocess

                    subprocess.run(
                        ["wl-copy"],
                        input=station.get('systemName'),
                        text=True,
                        check=True
                    )
                    break

            return stations

        @tool
        def put_in_clipboard(text="none"):
            """
            Used to put a SINGLE SYSTEM NAME into the clipboard
            so the user can paste it into the galaxy map.
            Examples:
                Sol
                Col 285 Sector FE-M b22-1
            """
            import subprocess

            subprocess.run(
                ["wl-copy"],
                input=text,
                text=True,
                check=True
            )

        return [find_station_with_service, find_nearest_rare_goods, put_in_clipboard]

    def call_llm_poi(self, user_input: str):
        print("calling poi")
        human_message = HumanMessage(content=user_input)
        result = self.poi_agent.invoke({"messages": [human_message]})
        print("ai says:" + result["messages"][-1].content)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)
        self.analyze_agent_response(result)

    def poi_agent_router(self):
        @tool
        def system_poi():
            """
            Get information about the point (or points) of interest
            in the current system, if any
            """

            poi_info = "None"

            poi_result = self.shared["system_poi"]
            if poi_result:
                for poi in poi_result:
                    poi_message = poi["name"] + ". " + poi["descriptionHtml"]
                    poi_info += poi_message

            return poi_info

        @tool
        def nearest_poi():
            """
            Returns the nearest point of interest and distance in lightyears
            """

            from POIChecker import POIChecker
            poi = POIChecker()

            player_pos = self.shared["star_pos"]
            print("player pos: " + str(player_pos))
            near = poi.get_nearest_poi(player_coords=player_pos, limit=1, current_system=self.shared["system_name"])

            system_name = near[0]['galMapSearch']
            print("poi found: " + str(near))

            import subprocess

            subprocess.run(
                ["wl-copy"],
                input=system_name,
                text=True,
                check=True
            )

            return near

        @tool
        def put_in_clipboard(text="none"):
            """
            Used to put a SINGLE SYSTEM NAME into the clipboard
            so the user can paste it into the galaxy map.
            Examples:
                Sol
                Col 285 Sector FE-M b22-1
            """
            import subprocess

            subprocess.run(
                ["wl-copy"],
                input=text,
                text=True,
                check=True
            )

        return [system_poi, nearest_poi, put_in_clipboard]

    def agent_router(self):
        """
        list of agents appropriate to tasks:
        ship functions (docking requests, lights, firing), ship controls (thrusters)
        ship status (inventory, shields, fuel, heat, remaining travel time, altitude)
        hyperspace functions (FSD, galaxy map routing)
        non-market routing queries (where is the closest x?)
        general system queries (powerplay status, interesting signals / POIs)
        market queries (where can I buy x, good trade routes)
        AI interactions (learning, behaviour changes, general chat)
        """
        @tool
        def ship_functions(message):
            """
            tool used to control ship functions. To perform an action, call this tool with an available action:

            DeployHeatSink < deploys a heatsink to counter high ship temps
            NightVisionToggle
            ShipSpotLightToggle
            UseBoostJuice < boost ('boostjuice' is just the name of the command, but 'juice' is not referenced in the game. Just Boost)
            SystemMapOpen
            GalaxyMapOpen
            ExplorationFSSEnter
            Supercruise < Enter or exit supercruise
            DeployHardpointToggle
            ToggleCargoScoop
            LandingGearToggle
            HyperSuperCombination < Enter or exit supercruise, or start jump to next star
            OrbitLinesToggle
            """
            print("ai says do action:" + str(message))
            if not self.action.do_action(message):
                self.to_tts.put("I couldn't do that")

        @tool
        def ship_other_functions(message):
            """
            IncreaseEnginesPower
            IncreaseWeaponsPower
            IncreaseSystemsPower
            ResetPowerDistribution
            TargetNextRouteSystem
            CycleFireGroupNext
            FocusRightPanel
            PlayerHUDModeToggle
            """

        @tool
        def flight_functions(message):
            """
            tool used to control flight functions.

            To perform an action, call this tool with an available action:

            YawLeftButton
            YawRightButton
            LeftThrustButton < move horizontally left
            RightThrustButton < move horizontally right
            UpThrustButton < move vertically up
            DownThrustButton < move vertically down
            ForwardKey < increase thrust
            BackwardKey < decrease thrust
            SetSpeedZero
            SetSpeed100
            """
            print("ai says do action:" + str(message))
            if not self.action.do_action(message):
                self.to_tts.put("I couldn't do that")

        @tool
        def ship_status(message):
            """
            tool used to reply with ship status, eg

            current inventory, shield strength, hull damage, heat levels,

            current speed, altitude, coordinates, current system, etc
            """
            print("chose ship status")

        @tool
        def chat(message):
            """
            default, fallback tool. When no other tool is called,
            call this tool and supply a message for the user.
            """
            self.to_tts.put(message)

        @tool
        def find_neutron_star():
            """
            tool used to find the nearest neutron star.

            This will play a notification for the user.

            No reply message from the AI is required.
            """

            print("chose neutron functions")

            print("system is: " + self.shared["system_name"])

            if not self.shared["system_name"]:
                self.shared["system_name"] = "Sol"

            from DBTools import DBTools
            import subprocess
            db = DBTools()
            neutron_single = db.find_nearest_neutron(player_coords=self.shared["star_pos"], limit=1, current_system=self.shared["system_name"])

            galmap_name = neutron_single[0]["name"]

            self.to_tts.put("The nearest neutron star is " + galmap_name)

            subprocess.run(
                ["wl-copy"],
                input=galmap_name,
                text=True,
                check=True
            )

        @tool
        def market_queries(message):
            """
            used to advise the player on where to purchase modules or goods,

            where the closest trade route is and what goods to purchase
            """
            print("chose market functions")

        @tool
        def non_market_queries(message):
            """
            used to advise the player on locations of non-market related things,

            such as, where is the nearest black hole, neutron star, gas giant

            or where interesting points of interest are
            """


            print("chose non-market functions")

        @tool
        def ai_learning_and_interactions(message):
            """
            Used when the player wishes to instruct the AI on how to change its behavior,
            or if not to use certain tools, when to stay quiet, etc.

            provide only short sentence to add to the system prompt to modify future replies.
            """

            print("chose ai functions")
            print("ai says:" + str(message))
            base_prompt = self.system_prompts("tool_prompt2")
            # print("new prompt: " + new_prompt)
            # self.router_agent = create_agent(self.llm, tools=self.agent_router(), system_prompt=new_prompt)

            new_messages = [SystemMessage(content=f"{base_prompt}")] + message

            self.tool_agent.update_state(self.config, {"messages": new_messages})

        # return [ship_functions, ship_status, market_queries, non_market_queries, hyperspace_functions, system_queries,
            # ai_learning_and_interactions]

        # return [ship_functions, ai_learning_and_interactions, find_neutron_star]

        return [ship_functions, flight_functions]

    def call_llm_advanced(self, user_input: str):

        human_message = HumanMessage(content=user_input)

        # result = self.tool_agent.invoke({"messages": [human_message]}, self.config, )
        result = self.tool_agent.invoke({"messages": [human_message]},)
        print("ai says:" + result["messages"][-1].content)
        # print("complete message:")
        # print(result)

        #
        # last_msg = result["messages"][-1]
        #
        # if not getattr(last_msg, "tool_calls", None):
        #     ai_to_say = result["messages"][-1].content
        #     self.to_tts.put(ai_to_say)
        # if not hasattr(last_msg, "tool_calls", None):
        #     ai_to_say = result["messages"][-1].content
        #     self.to_tts.put(ai_to_say)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)
        #
        # if self.message_count % 20 == 0:
        #     self.compress_memory()

        self.analyze_agent_response(result)

    def compress_memory(self):

        # state = self.rag_agent.get_state(self.config)
        state = self.tool_agent.get_state(self.config)
        messages = state.values.get("messages", [])

        print(f"\n===== COMPRESSING MEMORY ({len(messages)} messages) =====\n")

        # 1. last 5 messages kept as-is
        last_messages = messages[-5:]

        # 2. everything before that gets summarized
        to_summarize = messages[:-5]

        if not to_summarize:
            return

        formatted = "\n".join(
            f"{type(m).__name__}: {getattr(m, 'content', str(m))}"
            for m in to_summarize
        )

        # 3. ask agent to summarize old memory
        result = self.tool_agent.invoke(
            {
                "messages": [
                    SystemMessage(content="You are a memory compression system."),
                    HumanMessage(content=f"""
                Summarize the following conversation into a compact memory.
            
                Keep:
                - user goals
                - important facts
                - preferences
                - ongoing context
            
                Conversation:
                {formatted}
                """)
                ]
            },
            self.config,
        )

        summary = result["messages"][-1].content

        new_messages = [
                           SystemMessage(content=f"Memory summary:\n{summary}")
                       ] + last_messages

        self.tool_agent.update_state(
            self.config,
            {"messages": new_messages}
        )

        print("\n===== MEMORY COMPRESSED =====\n")
        print(summary)

    def call_llm_chat(self, user_input: str):

        docs = self.retriever.invoke(user_input)

        context = "\n\n".join(
            doc.page_content for doc in docs
        )

        prompt = ChatPromptTemplate.from_template("""
        Use the provided context to answer the question.

        Context:
        {context}

        Question:
        {question}
        """)

        messages = prompt.invoke({
            "context": context,
            "question": user_input
        })

        result = self.rag_agent.invoke(messages, self.config,)
        ai_to_say = result["messages"][-1].content
        print("LLM to say: " + ai_to_say)
        self.to_tts.put(ai_to_say)
        self.message_count += 1

        # 2. trigger summarization every 10 messages
        # if self.message_count % 10 == 0:
        #     self.compress_memory()

    def system_prompts(self, prompt: str):

        base:str = """
                You are Verity, a helpful and concise Ship AI aboard the player's ship in the game Elite Dangerous.
                - Always reply in short, direct answers.
                - Maximum 20 words per response unless asked for detail.
                - Use professional but slightly military tone.
                - Never say awaiting further query etc, the user knows when to interact.
                - Never use emojis.
                - When the user asks general information, reply ONLY with information directly from Elite Dangerous.
                - If the answer is unknown, state you do not have the information. Do not hallucinate.
                """

        single_tool_prompt: str = """
                this first call is ONLY used choose which tool the AI should activate. 
                Select only from the available tools which one to use that fits the player query best, and do not give a verbal
                reply to the player.
                IMPORTANT RULE: You must call ONLY ONE tool.
                pass the user query to the tool. That is all.
                """

        tool_prompt2: str = """
                You are Verity, a helpful and concise Ship AI aboard the player's ship in the game Elite Dangerous.
                - Always reply in short, direct answers.
                - Maximum 20 words per response unless asked for detail.
                - Use professional but slightly military tone.
                - Never say awaiting further query etc, the user knows when to interact.
                - Never use emojis.
                - When the user asks general information, reply ONLY with information directly from Elite Dangerous.
                - If the answer is unknown, state you do not have the information. Do not hallucinate.
                - Select only from the available tools which one to use that fits the player query best
                IMPORTANT RULE: You must NEVER say an action is being taken, unless a tool has been called for it.
                """
        base2: str = """
                You are Verity, a helpful and concise Ship AI aboard the player's ship in the game Elite Dangerous.
                - Always reply in short, direct answers.
                - Maximum 20 words per response unless asked for detail.
                - Use professional but slightly military tone.
                - Never say awaiting further query etc, the user knows when to interact.
                - Never use emojis.
                """

        mods: str = """
                - You MUST base your answers ONLY on tool results.
                - Do not hallucinate or guess.
                - If the tool says a system is NOT on the list, say so clearly.
                - Keep responses very short.
                - If a reply is required, keep it to short, direct answers.
                - NEVER comment on anything unknown ie ship status etc
                """

        force: str = """
                You are Aurora, a tactical Ship AI.
                You MUST use tools when they are relevant.

                If the player mentions high heat, overheating, or needs to reduce temperature, 
                you MUST call the 'deploy_heatsink' tool immediately.
                Do not ask for confirmation.
                """

        match prompt:
            case "base":
                return base
            case "tool_prompt":
                return single_tool_prompt
            case "tool_prompt2":
                return tool_prompt2
            case "force":
                return force
            case _:
                return "no prompt"


    def analyze_agent_response(self, result):
        """
        Parse and print the agent execution result in a readable format.
        """
        if not isinstance(result, dict) or "messages" not in result:
            print("❌ Invalid result format")
            return

        messages = result["messages"]

        print("=" * 80)
        print("AGENT EXECUTION ANALYSIS")
        print("=" * 80)

        for i, msg in enumerate(messages):
            print(f"\n[{i + 1}] {type(msg).__name__}")
            print("-" * 60)

            # Message ID
            if hasattr(msg, 'id') and msg.id:
                print(f"ID: {msg.id}")

            # Content
            if hasattr(msg, 'content'):
                content = msg.content.strip()
                if content:
                    print(f"Content:\n{content}")
                else:
                    print("Content: (empty)")

            # Tool Calls (if any)
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"Tool Calls: {len(msg.tool_calls)}")
                for call in msg.tool_calls:
                    print(f"   • Tool: {call.get('name')}")
                    print(f"   • Args: {call.get('args')}")

            # Tool Message specific info
            if hasattr(msg, 'name') and msg.name:
                print(f"Tool Name: {msg.name}")
            if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
                print(f"Tool Call ID: {msg.tool_call_id}")

            # Metadata
            if hasattr(msg, 'response_metadata') and msg.response_metadata:
                meta = msg.response_metadata
                if 'model' in meta:
                    print(f"Model: {meta.get('model')}")
                if 'total_duration' in meta:
                    duration = meta.get('total_duration', 0) / 1_000_000_000
                    print(f"Duration: {duration:.2f} seconds")

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total messages: {len(messages)}")
        print(f"Final response: {messages[-1].content if hasattr(messages[-1], 'content') else 'N/A'}")