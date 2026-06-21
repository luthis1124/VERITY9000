from rapidfuzz import process, fuzz
from DBTools import DBTools
from multiprocessing import Queue, Event
from PlayAudioFile import PlayAudioFile
from InputControls import InputControls

class VoiceCommandInterceptQ:

    def __init__(self, to_vci: Queue, to_llm: Queue,  to_tts: Queue, shutdown_event: Event, shared_state: dict):
        self.to_vci = to_vci
        self.to_llm = to_llm
        self.to_tts = to_tts
        self.shutdown_event = shutdown_event
        self.ap = PlayAudioFile()
        self.shared = shared_state
        self.action = InputControls()

    def run(self):
        while not self.shutdown_event.is_set():
            try:
                request = self.to_vci.get(timeout=0.5)
                if request:
                    print("checking: " + request)
                    self.check(request)
            except Exception as e:
                pass

    def check(self, input: str):
        # print("starting check for " + input)
        services = [
            'Apex Interstellar Transport',
            'Bartender',
            'Black Market',
            'Contacts',
            'Crew Lounge',
            'Fleet carrier administration',
            'Fleet carrier vendor',
            'Frontline Solutions',
            'Interstellar Factors Contact',
            'Material Trader',
            'Missions',
            'Pioneer Supplies',
            'Refuel',
            'Repair',
            'Restock',
            'Search and Rescue',
            'System colonisation',
            'Technology Broker',
            'Tuning',
            'Universal Cartographics',
            'Vista Genomics',
            'colonisationcontribution'
        ]

        candidates = [
            "deploy heatsink",
            "take us up", "launch",
            "request docking",
            "boost", "post",
            "full thrust", "full throttle", "throttle up",
            "system map",
            "galaxy map",
            "fss", "scanner",
            "stop",
            "supercruise",
            "hardpoints",
            "cargo scoop",
            "landing gear", "lending gear", "gear up",
            "night vision",
            "lights", "headlights",
            "interstellar factor",
            "technology broker", "tech broker", "tick broker", "broker", "take broken",
            "material trader",
            "cartographics", "universal cartographics",
            "system poi", "system p o i",
            "nearest point of interest", "nearest poi", "nearest p o i",
            "copy current system",
            "rare goods", "rare commodities", "goods"
        ]

        word_count = len(input.split())
        keywords = ["verity", "fairity", "ferrity"]
        text = input.lower()
        has_verity = any(k in text for k in keywords)
        # has_verity = "verity" in input.lower().split()

        if word_count > 5 or has_verity:
            self.to_llm.put(input)
            return True

        results = process.extract(
            input,
            candidates,
            scorer=fuzz.WRatio,
            score_cutoff=80  # Minimum threshold
        )

        # print("do we get past the fuzz match?" )
        if results:
            match results[0][0]:
                case "system poi" | "system p o i" | "point of interest":
                    self.play_poi()
                case "nearest point of interest" | "nearest poi" | "nearest p o i":
                    self.get_nearest_poi()
                case "interstellar factor":
                    self.find_station(self.shared["star_pos"], 'Interstellar Factors Contact')
                case "technology broker" | "tech broker" | "tick broker" | "broker":
                    self.find_station(self.shared["star_pos"], 'Technology Broker')
                case "material trader":
                    self.find_station(self.shared["star_pos"], 'Material Trader')
                case "cartographics" | "universal cartographics":
                    self.find_station(self.shared["star_pos"], 'Universal Cartographics')
                case "copy current system":
                    self.ap.affirmative()
                    self.clipboard(self.shared["system_name"])
                case "rare goods" | "rare commodities" | "goods":
                    self.get_next_rare_goods(self.shared["star_pos"])
                case "deploy heatsink":
                    self.ap.affirmative()
                    self.action.do_action('DeployHeatSink')
                case "take us up" | "launch":
                    self.ap.affirmative()
                    self.action.hold_action('UpThrustButton')
                case "night vision":
                    self.ap.affirmative()
                    self.action.do_action('NightVisionToggle')
                case "lights" | "headlights":
                    self.ap.affirmative()
                    self.action.do_action('ShipSpotLightToggle')
                case "request docking":
                    self.ap.affirmative()
                    self.action.request_docking()
                case "boost" | "post":
                    self.ap.affirmative()
                    self.action.do_action('UseBoostJuice')
                case "full thrust" | "full throttle" | "throttle up":
                    self.ap.affirmative()
                    self.action.do_action('SetSpeed100')
                case "system map":
                    self.ap.affirmative()
                    self.action.do_action('SystemMapOpen')
                case "galaxy map":
                    self.ap.affirmative()
                    self.action.do_action('GalaxyMapOpen')
                case "fss" | "scanner":
                    self.ap.affirmative()
                    self.action.do_action('ExplorationFSSEnter')
                case "stop":
                    self.ap.affirmative()
                    self.action.do_action('SetSpeedZero')
                case "supercruise":
                    self.ap.affirmative()
                    self.action.do_action('Supercruise')
                case "hardpoints":
                    self.ap.affirmative()
                    self.action.do_action('DeployHardpointToggle')
                case "cargo scoop":
                    self.ap.affirmative()
                    self.action.do_action('ToggleCargoScoop')
                case "landing gear" | "lending gear" | "gear up":
                    self.ap.affirmative()
                    self.action.do_action('LandingGearToggle')
                case _:
                    # print(f"Unknown command: {results[0][0]}")

                    return True
        else:
            self.to_llm.put(input)
            return True

    def play_poi(self):
        poi_result = self.shared["system_poi"]
        if poi_result:
            for poi in poi_result:
                poi_message = poi["name"] + ". " + poi["descriptionHtml"]
                self.to_tts.put(poi_message)
        else:
            self.ap.no_record()

    def get_nearest_poi(self):
        from POIChecker import POIChecker
        poi = POIChecker()

        player_pos = self.shared["star_pos"]
        near = poi.get_nearest_poi(player_coords=player_pos)

        for poi in near:
            print("nearest poi at " + poi["galMapSearch"])
            poi_address = "The nearest point of interest to your location is in " + poi["galMapSearch"]
            self.to_tts.put(poi_address)

    def get_next_rare_goods(self, player_pos):
        visited = self.shared["visited_rare_goods"]
        db = DBTools()
        stations = db.find_nearest_rares(player_pos)

        for i, station in enumerate(stations, 18):
            print("checking system: " + str(station.get('systemName')))
            print("against list: " + str(visited))
            if station.get('systemName') not in visited:
                dist = station['distance']
                dist_to_arrival= station.get('distanceToArrival')
                self.clipboard(station.get('systemName'))
                output = f"The nearest rare commodities are available {dist:,.0f} lightyears away in system {station.get('systemName')}, at station {station['name']}, {dist_to_arrival:,.0f} lightseconds from exit."
                self.to_tts.put(output)
                break

    def find_station(self, player_pos, service):
        db = DBTools()
        stations = db.find_nearest(player_pos, limit=1, service=service)

        if not stations:
            self.ap.unable_service()
            return None
        for i, station in enumerate(stations, 1):
            dist = station['distance']
            dist_to_arrival= station.get('distanceToArrival')
            self.clipboard(station.get('systemName'))
            output = f"The nearest {service} is {dist:,.0f} lightyears away in system {station.get('systemName')}, at station {station['name']}, {dist_to_arrival:,.0f} lightseconds from exit."
            self.to_tts.put(output)
            return None

    def clipboard(self, text="none"):
        import subprocess

        subprocess.run(
            ["wl-copy"],
            input=text,
            text=True,
            check=True
        )