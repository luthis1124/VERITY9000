from multiprocessing import Process, Queue, Event
from RareCommodityChecker import RareCommodityChecker
from ThreatChecker import ThreatChecker
from StatusMonitor import StatusMonitor
from InputControls import InputControls
from POIChecker import POIChecker
from PlayAudioFile import PlayAudioFile


class JournalEventHandlerQ:

    def __init__(self, to_ev: Queue, to_tts: Queue, shutdown_event: Event, shared_state: dict):
        self.status = StatusMonitor()
        self.to_ev = to_ev
        self.to_tts = to_tts
        self.shutdown_event = shutdown_event
        self.fuel_warning_given = False
        self.latest_events = {}
        self.ap = PlayAudioFile()
        self.shared = shared_state

    def run(self):
        print(f"started journal event")
        try:
            while not self.shutdown_event.is_set():
                try:
                    request = self.to_ev.get(timeout=1)
                    # print(f"journal handler Received request: {request}")
                    print("first run: " + self.shared["first_run"])
                    if request:
                        if self.shared["first_run"]:
                            self.handle_event_initial(request)
                        else:
                            self.handle_event(request)
                except Exception as e:
                    pass

        except Exception as e:
            print(f"event Error: {e}")

    def handle_event(self, data: dict):
        """
        Handle specific events with match-case.
        Takes the full parsed JSON dictionary.
        """
        if not isinstance(data, dict) or 'event' not in data:
            return

        event = data['event']
        self.latest_events[event] = data

        match event:
            case "FSSSignalDiscovered":
                # self.ship.set_system_address(data.get('SystemAddress'))
                # print("")
                pass
            case "Location":
                # print("")
                pass
            case "Loadout":
                self.shared["ship_name"] = data.get('ShipName', 'Unknown')
                self.shared["fuel_capacity"] = float(data.get('FuelCapacity', {}).get('Main'))
                self.shared["cargo_capacity"] = (data.get('CargoCapacity', {}).get('Main'), 10)

            case "StartJump":
                jump_type = data.get('JumpType', 'Unknown')
                match jump_type:
                    case "Hyperspace":
                        system = data.get('StarSystem', 'Unknown')
                        print(f"StartJump → {system} ({jump_type})")
                        jumpinfo = "System " + system

            case "FSDJump":
                StarSystem = data.get('StarSystem', 'Unknown')
                self.shared["system_name"] = (data.get('StarSystem', 'Unknown'))
                self.shared["star_pos"] = (data.get('StarPos', ''))
                self.shared["system_address"] = (data.get('SystemAddress', ''))
                self.shared["system_alliegance"] = (data.get('SystemAllegiance', ''))
                self.shared["fuel_level"] = (data.get('FuelLevel', ''))
                self.on_system_enter(StarSystem)

            case "HeatDamage":
                self.ap.heat_alert()
                action = InputControls()
                action.do_action('DeployHeatSink')

            case "Docked":
                station = data.get('StationName', 'Unknown')
                # self.ship.set_station(data.get('StationName', 'Unknown'))
                self.shared["station"] = data.get('StationName', 'Unknown')
                print(f"Docked at {station}")

            case "Undocked":
                action = InputControls()
                action.do_action('LandingGearToggle')
                print("Undocked")

            case "SupercruiseExit":
                body = data.get('Body', 'Unknown')
                body_audio = "Arriving at " + str(body)
                self.to_tts.put(body_audio)

                if body == self.status.get_home_station():
                    self.ap.welcome_home()

            case "ApproachBody":
                bodyid = data.get('BodyID', 'Unknown')
                approach = "Arriving at body " + str(bodyid)
                self.to_tts.put(approach)

            case "ApproachSettlement":
                settlement = data.get('Name', 'Unknown')
                approachsettlement = settlement
                self.to_tts.put(approachsettlement)

            case "Music":
                musictype = data.get('MusicTrack', '')
            case _:
                pass

    def handle_event_initial(self, data: dict):

        if not isinstance(data, dict) or 'event' not in data:
            return

        event = data['event']

        match event:
            case "Loadout":
                # self.ship.set_ship_name(data.get('ShipName'))
                self.shared["ship_name"] = data.get('ShipName', 'Unknown')
                # self.ship.set_fuel_capacity(float(data.get('FuelCapacity', {}).get('Main')))
                self.shared["fuel_capacity"] = float(data.get('FuelCapacity', {}).get('Main'))
                # self.ship.set_cargo_capacity(int(data.get('CargoCapacity')))
                self.shared["cargo_capacity"] = (data.get('CargoCapacity', {}).get('Main'), 10)
            case "FSDJump":
                # self.ship.set_system_name(data.get('StarSystem', 'Unknown'))
                self.shared["system_name"] = (data.get('StarSystem', 'Unknown'))
                # self.ship.set_star_pos(data.get('StarPos', ''))
                self.shared["star_pos"] = (data.get('StarPos', ''))
                # self.ship.set_system_address(data.get('SystemAddress', ''))
                self.shared["system_address"] = (data.get('SystemAddress', ''))
                # self.ship.set_system_alliegance(data.get('SystemAllegiance', ''))
                self.shared["system_alliegance"] = (data.get('SystemAllegiance', ''))
                # self.ship.set_fuel_level(data.get('FuelLevel', ''))
                self.shared["fuel_level"] = (data.get('FuelLevel', ''))
            case "Docked":
                # self.ship.set_station(data.get('StationName', 'Unknown'))
                self.shared["station"] = data.get('StationName', 'Unknown')
            case _:
                pass

    def on_system_enter(self, StarSystem: str):
        jumpinfo = "System " + StarSystem
        self.to_tts.put(jumpinfo)

        level = self.shared["fuel_level"]
        fuelcap = self.shared["fuel_capacity"]

        if fuelcap / level < 2.0:
            self.fuel_warning_given = False

        elif fuelcap / level > 2.0 and not self.fuel_warning_given:
            self.fuel_warning_given = True
            self.ap.fuel_alert()

        elif fuelcap / level > 4.0:
            self.ap.major_fuel_alert()

        tc = ThreatChecker()
        if tc.is_dangerous(StarSystem):
            self.ap.high_threat()

        rc = RareCommodityChecker()
        result = rc.check(StarSystem)
        if result["found"]:
            commodity_message = "Rare goods sold in station " + result["station"]
            self.to_tts.put(commodity_message)
            system = StarSystem.strip()
            self.shared.setdefault("visited_rare_goods", [])
            if system not in self.shared["visited_rare_goods"]:
                self.shared["visited_rare_goods"].append(system)

        poi = POIChecker()
        poi_result = poi.check_system(StarSystem)
        self.shared["system_poi"] = poi_result
        if poi_result:
            if len(poi_result) == 1:
                self.ap.poi_message()
            elif len(poi_result) > 1:
                self.ap.multiple_poi_message()
