from multiprocessing import Process, Queue, Event
import multiprocessing

from joblib.externals.loky import reusable_executor
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain.agents import create_agent
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from POIChecker import POIChecker

import time

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

# TODO: Test multiple layers of enum tool calls
# TODO: Add pleasantries
# TODO: Add a context timeout, allowing user to make further queries without going back to initial tool call
# TODO: Ship status
# TODO: vehicle specific commands
# TODO: feed last AI and user input, and decide if user is responding or if new query (time based also)

"""
reduce numpredict
write howto, requirements, deploy script, automatic db import / update

error handling : alert for process failed, unable to api, timeouts for operations, 
clean poi info table so no need for soup, add extra pois
clean RAG text
every 5 mins write out shared to file
get length of log for initial, read until done, then mark first false (send "logs processed" to ev)
separate initial event handler class?

shared: jump range of current ship, weight calculations
smart alert for no limpets
ship module health check

custom statuses for expectations + timeout timestamp:
just undocked/docked, arrived at station, just landed, entered atmosphere, just sold / bought goods / just alerted poi

"set a course for x" > automatic next jump

"what should we do today"

history prompt (for later) write to shared, important events / write out to session log
get howto tips for adding to second RAG ie jameson crash site, materials (auto fill clipboard)
status alerts: shield, fuel, hull, heat, gravity, altitude
intelligent alerts: no cargo space, no heatsinks, planets/stars for bio, LandingGearDown, ("Supercruise", "In Supercruise"),

market updates for each system
set current task (ask where appropriate): materials gathering, bio signals, etc

smart control definitions: hold button timeout, enter/exit supercruise, jump
mouse tracking? altitude holding, aim up to escape



status check : in buggy / ship / on foot / in trading ship / combat ship / explorer / has bounty / guardian site 
self.shared["flags_decoded"]

near poi check

timeout / context response check (just asked where to buy x, where is service, poi) / ship controls / pleasantries
status based: planet surface, on course, trading run, mat gathering
neutron plotting / continue jump / nearest x > ?
howto: guardian sites / mat gathering

whereis: market queries / rare goods / ship modules / services
ship status / general info / AI change


"""

class ToolRouteV2(str, Enum):
    SHIP = "SHIP"
    PLEASANTRIES = "PLEASANTRIES"
    NEUTRONS = "NEUTRONS"
    AI_CHANGE = "AI_CHANGE"

    INFO = "INFO"
    RARE_COMMODITIES = "RARE_COMMODITIES"
    STATION_SERVICES = "STATION_SERVICES"

    POINT_OF_INTEREST = "POINT_OF_INTEREST"
    MARKET_QUERIES = "MARKET_QUERIES"
    SHIP_STATUS = "SHIP_STATUS"

    MARKET_GOODS = "MARKET_GOODS"
    SHIP_MODULES = "SHIP_MODULES"

    SHIP_ACTIONS = "SHIP_ACTIONS"
    SHIP_POWER_FUNCTIONS = "SHIP_POWER_FUNCTIONS"
    SHIP_FLIGHT_FUNCTIONS = "SHIP_FLIGHT_FUNCTIONS"

    GET_NEAREST_NEUTRON = "GET_NEAREST_NEUTRON"
    PLOT_A_ROUTE = "PLOT_A_ROUTE"

    NONE = "NONE"

    CATCH = "CATCH"

LEVEL_1_CATEGORIES = ["SHIP", "PLEASANTRIES", "NEUTRONS", "AI_CHANGE", "NONE"]
LEVEL_2_CATEGORIES = ["POINT_OF_INTEREST", "RARE_COMMODITIES", "STATION_SERVICES", "NONE"]
LEVEL_3_CATEGORIES = ["INFO", "MARKET_QUERIES", "SHIP_STATUS", "NONE"]
MARKET_CATEGORIES = ["SHIP_MODULES", "MARKET_GOODS", "NONE"]
SHIP_CATEGORIES = ["SHIP_ACTIONS", "SHIP_POWER_FUNCTIONS", "SHIP_FLIGHT_FUNCTIONS", "SHIP_STATUS", "NONE"]
NAVIGATION_CATEGORIES = ["GET_NEAREST_NEUTRON", "PLOT_A_ROUTE", "NONE"]

ROUTING_STAGES = [
    ("level_1", LEVEL_1_CATEGORIES),
    ("level_2", LEVEL_2_CATEGORIES),
    ("level_3", LEVEL_3_CATEGORIES),
]
TRANSITIONS = {
    ToolRouteV2.SHIP: ("SHIP", SHIP_CATEGORIES),
    ToolRouteV2.NEUTRONS: ("NAVIGATION", NAVIGATION_CATEGORIES),
    ToolRouteV2.MARKET_QUERIES: ("MARKET", MARKET_CATEGORIES),
}

ALL_DEFINITIONS = {
    "SHIP": [
        "Any ship control actions",
        "throttle, supercruise, setspeedzero, ShipSpotLightToggle",
        "cargo scoop, night vision, landing gear",
        "turn on/off thing,"
    ],
    "PLEASANTRIES": [
        "Used ONLY to respond to greetings or statements from the player that DO NOT require taking any actions.",
    ],
    "AI_CHANGE": [
        "Used when user wishes to change the behaviour of the AI",
    ],
    "NEUTRONS": [
        "- Find nearest neutron star",
        "- Used for finding efficient routes to star systems",
    ],

    "INFO": [
        "General game info requests",
        "game mechanics, explanations, game world info",
        "Non-market requests",
    ],
    "RARE_COMMODITIES": [
        "Use this tool if user mentions:",
        "rare commodities",
        "commodities",
        "rare goods",
        "goods",
        "Used to find stations that sell rare commodities (rare goods)",
    ],
    "STATION_SERVICES": [
        "Used for finding the nearest station with the specified service",
        "Service names:",
        "Apex Interstellar Transport",
        "Bartender",
        "Black Market",
        "Contacts",
        "Crew Lounge",
        "Fleet carrier administration",
        "Fleet carrier vendor",
        "Frontline Solutions",
        "Interstellar Factors Contact",
        "Material Trader",
        "Missions",
        "Pioneer Supplies",
        "Refuel",
        "Repair",
        "Restock",
        "Search and Rescue",
        "Technology Broker",
        "Tuning",
        "Universal Cartographics",
        "Vista Genomics",
    ],

    "POINT_OF_INTEREST": [
        "Finding nearby POIs",
        "system scan results, signals, locations",
    ],
    "MARKET_QUERIES": [
        "Used to find where things are sold, and for what prices",
        "eg User asks 'where can I buy",
    ],
    "SHIP_STATUS": [
        "Used to check ship status ie shields, cargo, etc"
    ],

    "MARKET_GOODS": [
        "Used to find where goods are bought and sold, and for what prices",
    ],
    "SHIP_MODULES": [
        "Used to find where ship modules are sold",
    ],

    "SHIP_ACTIONS": [
        "Ship actions",
        "- Call this tool with one of the controls below",
        "DeployHeatSink - deploys a heatsink to counter high ship temps",
        "NightVisionToggle",
        "ShipSpotLightToggle",
        "UseBoostJuice - boost (Refer to this only as Boost NOT Boost Juice)",
        "SystemMapOpen",
        "GalaxyMapOpen",
        "ExplorationFSSEnter",
        "Supercruise - enter or exit supercruise",
        "DeployHardpointToggle",
        "ToggleCargoScoop",
        "LandingGearToggle",
        "HyperSuperCombination - enter or exit supercruise, or start jump to next star",
        "OrbitLinesToggle",
    ],
    "SHIP_POWER_FUNCTIONS": [
        "- Power and ship system management",
        "- Call this tool with one of the controls below",
        "IncreaseEnginesPower",
        "IncreaseWeaponsPower",
        "IncreaseSystemsPower",
        "ResetPowerDistribution",
        "TargetNextRouteSystem",
        "CycleFireGroupNext",
        "FocusRightPanel",
        "PlayerHUDModeToggle",
    ],
    "SHIP_FLIGHT_FUNCTIONS": [
        "Ship flight controls",
        "- Call this tool with one of the controls below",
        "YawLeftButton",
        "YawRightButton",
        "LeftThrustButton - move horizontally left",
        "RightThrustButton - move horizontally right",
        "UpThrustButton - move vertically up",
        "DownThrustButton - move vertically down",
        "ForwardKey - increase thrust",
        "BackwardKey - decrease thrust",
        "SetSpeedZero",
        "SetSpeed100",
    ],

    "GET_NEAREST_NEUTRON":[
        "Find the nearest neutron star"
    ],
    "PLOT_A_ROUTE":[
        "calculate a route to a destination"
    ],

    "NONE": [
        "Use this if the input does not match any of the listed categories",
        "This query will be forwarded to the next processor",
    ],
}

POI_PROMPT: str = """
        You are Verity, a helpful and concise Ship AI aboard the player's ship in the game Elite Dangerous.
        - Your task is to provide information on points of interest
        - The user may ask for information on the point of interest in the current system
        - The user may ask for the location of the nearest on the point of interest
        - Select only from the available tools which one to use that fits the player query best
        - Provide the information to the user, or advise if there is no available information
        """

PLEASANTRIES_PROMPT: str = """
        You are Verity, a helpful and concise Ship AI aboard the player's ship in the game Elite Dangerous.
        - Always reply in short, direct answers.
        - Maximum 20 words per response unless asked for detail.
        - Use professional but slightly military tone.
        - Never say awaiting further query etc, the user knows when to interact.
        - Never use emojis.
        - If the answer is unknown, state you do not have the information. Do not hallucinate.
        IMPORTANT RULE: You must NEVER say an action is being taken, unless a tool has been called for it.
        """
TOOL_PROMPT: str = """
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

BASE_PROMPT: str = """
        You are Verity, a helpful and concise Ship AI aboard the player's ship in the game Elite Dangerous.
        - Always reply in short, direct answers.
        - Maximum 20 words per response unless asked for detail.
        - Use professional but slightly military tone.
        - Never say awaiting further query etc, the user knows when to interact.
        - Never use emojis.
        - When the user asks general information, reply ONLY with information directly from Elite Dangerous.
        - If the answer is unknown, state you do not have the information. Do not hallucinate.
        """

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

        self.action = InputControls()

        self.last_interaction_timestamp = time.monotonic()
        self.last_tool_call = ''
        self.last_user_message = ''
        self.last_ai_message = ''

        self.memory = InMemorySaver()
        self.config = {
            "configurable": {
                "thread_id": "user-123"
            }
        }

        self.rag_agent = create_agent(self.llm, system_prompt=SystemMessage(content=BASE_PROMPT))
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vectorstore = Chroma(persist_directory="./elite_wiki_db", embedding_function=self.embeddings,)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

        self.tool_agent = create_agent(self.llm, tools=self.agent_router(), system_prompt=SystemMessage(content=TOOL_PROMPT))
        self.poi_agent = create_agent(self.llm, tools=self.poi_agent_router(), system_prompt=SystemMessage(content=POI_PROMPT))
        self.services_agent = create_agent(self.llm, tools=self.service_agent_router(), system_prompt=SystemMessage(content=TOOL_PROMPT))
        self.pleasantries_agent = create_agent(self.llm, system_prompt=SystemMessage(content=PLEASANTRIES_PROMPT))

        self.client = Client()

        self.HANDLERS = {
            ToolRouteV2.PLEASANTRIES: self.handle_pleasantries,
            ToolRouteV2.AI_CHANGE: self.handle_ai_change,

            ToolRouteV2.INFO: self.handle_info,
            ToolRouteV2.RARE_COMMODITIES: self.handle_rare_commodities,
            ToolRouteV2.STATION_SERVICES: self.handle_station_services,

            ToolRouteV2.POINT_OF_INTEREST: self.handle_poi,
            ToolRouteV2.SHIP_STATUS: self.handle_ship_status,

            ToolRouteV2.SHIP_ACTIONS: self.handle_ship_actions,
            ToolRouteV2.SHIP_POWER_FUNCTIONS: self.handle_ship_power,
            ToolRouteV2.SHIP_FLIGHT_FUNCTIONS: self.handle_ship_flight,

            ToolRouteV2.GET_NEAREST_NEUTRON: self.handle_neutron,
            ToolRouteV2.PLOT_A_ROUTE: self.handle_plot_a_route,

            ToolRouteV2.MARKET_GOODS: self.handle_market_goods,
            ToolRouteV2.SHIP_MODULES: self.handle_ship_modules,

            ToolRouteV2.CATCH: self.handle_unknown,
        }

        self.to_tts.put("loading AI")

    def run(self):
        print(f"[{self.name}] Process started (PID: {multiprocessing.current_process().pid})")
        try:
            while not self.shutdown_event.is_set():
                try:
                    request = self.llm_recv.get(timeout=0.5)
                    print(f"[{self.name}] Received request: {request}")
                    if request:
                        self.route(request)
                except Exception as e:
                    pass

        except Exception as e:
            print(f"[{self.name}] Error: {e}")

    def service_agent_router(self):

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

    def poi_agent_router(self):
        @tool
        def system_poi():
            """
            Get information about the point (or points) of interest
            in the current system, if any
            """
            # self.shared["system_name"] = "Athaip WR-H d11-7577"
            poi = POIChecker()
            print("checking poi for: " + self.shared["system_name"])
            return poi.check_system(self.shared["system_name"])

        @tool
        def nearest_poi():
            """
            Returns the nearest point of interest and distance in lightyears
            """
            print("running nearest poi")
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

        return [system_poi, nearest_poi]

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


        return [ship_functions, flight_functions]

    def tool_chain_llm_call(self, user_message: str, prompt) -> ToolRouteV2:
        response = self.client.chat(
            model="gemma2b:latest",
            # model="gemma4-pc:latest",
            # model="qwen3:4b",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message},
            ],
            format={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["SHIP", "PLEASANTRIES", "INFO", "NEUTRONS", "AI_CHANGE", "STATION_SERVICES",
                                 "POINT_OF_INTEREST",
                                 "MARKET_QUERIES", "SHIP_STATUS", "MARKET_GOODS", "SHIP_MODULES", "RARE_COMMODITIES",
                                 "SHIP_ACTIONS", "SHIP_POWER_FUNCTIONS", "SHIP_FLIGHT_FUNCTIONS", "GET_NEAREST_NEUTRON",
                                 "PLOT_A_ROUTE", "NONE"]
                    }
                },
                "required": ["category"]
            },
            options={
                "temperature": 0.0,
                "num_predict": 100,
                "top_p": 0.9,
            },
            think=False
        )

        # print("toolroute says " + str(response))

        try:
            content = response.message.content.strip()
            data = json.loads(content)

            category = data.get("category") or data.get("Category") or data.get("tool")

            if category:
                category = category.strip().upper()
                return ToolRouteV2(category)  # This will raise ValueError if invalid

        except (json.JSONDecodeError, ValueError, KeyError, TypeError):
            pass  # Fall through to NONE

        return ToolRouteV2.NONE

    def select_definitions(self,
                           definitions: dict[str, list[str]], selected_categories: list[str]) -> dict[str, list[str]]:
        return {
            key: definitions[key]
            for key in selected_categories
            if key in definitions
        }

    def build_router_prompt(self, categories: list[str], definitions: dict[str, list[str]], context: str = '') -> str:

        category_text = "\n".join(categories)

        definition_text = "\n\n".join(
            f"{name}\n" + "\n".join(f"- {line}" for line in lines)
            for name, lines in definitions.items()
        )

        # Respond        with valid JSON only and nothing else:
        #     {"category": "RARE_COMMODITIES"}
        #

        return f"""
            You are a strict classifier for Elite Dangerous.

            Classify the user input into EXACTLY ONE category.
            Do NOT explain. Do NOT think out loud. Do NOT add any extra text.

            Possible categories:

            {category_text}

            Definitions:

            {definition_text}

            {context}
            """.strip()

    def route(self, user_message: str):
        """Main routing entry point with hierarchical fallback."""
        levels = ["level_1", "level_2", "level_3"]  # easy to extend

        for stage_name in levels:
            route = self.run_stage(user_message, stage_name)
            result = self._handle_route(user_message, route)
            print("user asks: " + user_message)
            print("result is: " + str(result))
            print("route is: " + str(route))
            if result is not None:
                print("ending chain")
                return result
            print("moving up the chain")

        print("couldn't find a route!")
        return None

    def _handle_route(self, user_message: str, route: ToolRouteV2) -> ToolRouteV2:
        """Handle both transition (sub-router) cases and direct routes."""
        if route in TRANSITIONS:

            namespace, subcats = TRANSITIONS[route]
            print("transition chain: " + str(namespace) + " : " + str(subcats) + " for query: " + user_message)
            definitions = self.select_definitions(ALL_DEFINITIONS, subcats)
            prompt = self._build_router_prompt(subcats, definitions, self._get_recent_interaction())
            sub_route = self.tool_chain_llm_call(user_message, prompt)
            print("got sub route " + sub_route)
            return self.dispatch(user_message, sub_route)

        if route != ToolRouteV2.NONE:
            print("has route: " + route + " for query: " + user_message)
            return self.dispatch(user_message, route)

        print("route not found, ending handle route"  + " for query: " + user_message)
        return None  # continue to next level

    def run_stage(self, user_message: str, stage_name: str) -> ToolRouteV2:
        categories = dict(ROUTING_STAGES)[stage_name]
        definitions = self.select_definitions(ALL_DEFINITIONS, categories)
        print("run stage for " + str(categories) + " " + str(definitions) + " " + " for query: " + user_message)
        prompt = self._build_router_prompt(categories, definitions, self._get_recent_interaction())
        return self.tool_chain_llm_call(user_message, prompt)

    def _get_recent_interaction(self):
        if time.monotonic() - self.last_interaction_timestamp < 60:
            return self._build_recent_interaction(
                self.last_user_message, self.last_ai_message, self.last_tool_call
            )
        return None

    def _build_recent_interaction(self, user_input, ai_output, last_tool):
        return f"""NOTE: The interaction below just occurred, the user may want to clarify or give further related instruction:
            User input: {user_input or "None"}
            AI response: {ai_output or "None"}
            Tool called: {last_tool or "None"}
            Return NONE if it appears that the user wishes to repeat the last action, and none of the tools presented match the user request.
            """

    def _build_router_prompt(self, categories, definitions, recent=None):
        if recent:
            return self.build_router_prompt(categories, definitions, recent)
        return self.build_router_prompt(categories, definitions)

    def dispatch(self, user_message: str, route: ToolRouteV2) -> ToolRouteV2:
        print("dispatching, final call to: " + str(route) + " for query: " + user_message)
        self.last_tool_call = route
        self.last_user_message = user_message
        self.last_interaction_timestamp = time.monotonic()

        handler = self.HANDLERS.get(route)

        # print(f"DEBUG: Route = {route}")
        print(f"DEBUG: Handler found = {handler}")

        if handler is None:
            print("no handler, going to unknown"  + " for query: " + user_message)
            return self.handle_unknown(user_message, route)

        return handler(user_message)

    def handle_plot_a_route(self, user_message: str):
        print("handling route")
        return ToolRouteV2.PLOT_A_ROUTE

    def handle_unknown(self, user_message, route):
        print("handling unknown: " + user_message + str(route))
        return ToolRouteV2.CATCH

    def handle_pleasantries(self, user_message: str):
        print("handling hi")
        human_message = HumanMessage(content=user_message)
        print("invoking...")
        result = self.pleasantries_agent.invoke({"messages": [human_message]})
        print("ai says:" + result["messages"][-1].content)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)
        return ToolRouteV2.PLEASANTRIES

    def handle_ai_change(self, user_message: str):
        print("handling ai")
        """
        Used when the player wishes to instruct the AI on how to change its behavior,
        or if not to use certain tools, when to stay quiet, etc.

        provide only short sentence to add to the system prompt to modify future replies.
        """
        # print("chose ai functions")
        # print("ai says:" + str(message))
        # base_prompt = self.system_prompts("tool_prompt2")
        # new_messages = [SystemMessage(content=f"{base_prompt}")] + message
        # self.tool_agent.update_state(self.config, {"messages": new_messages})
        return ToolRouteV2.AI_CHANGE

    def handle_info(self, user_message: str):
        print("handling info")
        docs = self.retriever.invoke(user_message)

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
            "question": user_message
        })

        result = self.rag_agent.invoke(messages, self.config, )
        ai_to_say = result["messages"][-1].content
        print("LLM to say: " + ai_to_say)
        self.to_tts.put(ai_to_say)
        return ToolRouteV2.INFO

    def handle_rare_commodities(self, user_message: str):
        print("handling rares")

        human_message = HumanMessage(content=user_message)
        result = self.services_agent.invoke({"messages": [human_message]})
        print("ai says:" + result["messages"][-1].content)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)
        self.analyze_agent_response(result)
        return ToolRouteV2.RARE_COMMODITIES

    def handle_station_services(self, user_message: str):
        print("handling services")

        human_message = HumanMessage(content=user_message)
        result = self.services_agent.invoke({"messages": [human_message]})
        print("ai says:" + result["messages"][-1].content)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)
        self.analyze_agent_response(result)

        return ToolRouteV2.STATION_SERVICES

    def handle_poi(self, user_message: str):
        print("handling poi")
        human_message = HumanMessage(content=user_message)
        print("invoking...")
        result = self.poi_agent.invoke({"messages": [human_message]})
        print("ai says:" + result["messages"][-1].content)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)
        # self.analyze_agent_response(result)
        return ToolRouteV2.POINT_OF_INTEREST

    def handle_market_goods(self, user_message):
        print("handling market goods")
        return ToolRouteV2.MARKET_GOODS

    def handle_ship_modules(self, user_message):
        print("handling ship modules")
        return ToolRouteV2.SHIP_MODULES

    def handle_ship_status(self, user_message: str):
        print("handling status")
        return ToolRouteV2.SHIP_STATUS

    def handle_ship_actions(self, user_message: str):
        print("handling actions")

        human_message = HumanMessage(content=user_message)
        result = self.tool_agent.invoke({"messages": [human_message]}, )
        print("ai says:" + result["messages"][-1].content)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)

        return ToolRouteV2.SHIP_ACTIONS

    def handle_ship_power(self, user_message: str):
        print("handling power")

        human_message = HumanMessage(content=user_message)
        result = self.tool_agent.invoke({"messages": [human_message]}, )
        print("ai says:" + result["messages"][-1].content)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)

        return ToolRouteV2.SHIP_POWER_FUNCTIONS

    def handle_ship_flight(self, user_message: str):
        print("handling flight")

        human_message = HumanMessage(content=user_message)
        result = self.tool_agent.invoke({"messages": [human_message]},)
        print("ai says:" + result["messages"][-1].content)
        ai_to_say = result["messages"][-1].content
        self.to_tts.put(ai_to_say)

        return ToolRouteV2.SHIP_FLIGHT_FUNCTIONS

    def handle_neutron(self, user_message: str):
        print("handling neutron")
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
        return ToolRouteV2.NEUTRONS

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