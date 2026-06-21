import json
from multiprocessing import Queue, Event
import time

STATUS_FILE='/media/ssd/SteamLibrary/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/Status.json'

class Statest:

    def __init__(self, shared_state: dict):
        self.shared = shared_state

    def test_update(self):
        filename = 'dataref/Statuslatitude.json'
        with open(filename, "r") as file:
            data = json.load(file)

        self.shared["status_update"] = data
        print(self.shared)

    def decode_flags(self, flags_value: int) -> dict:
        """
        Decodes the Elite Dangerous Status Flags integer into human-readable status.
        Args:
            flags_value (int): The Flags value from the Status event (e.g. 150994952)
        Returns:
            dict: Dictionary with active flags and their descriptions
        """

        flag_definitions = {
            0: ("Docked", "On a landing pad"),
            1: ("Landed", "On planet surface"),
            2: ("LandingGearDown", "Landing gear is down"),
            3: ("ShieldsUp", "Shields are active"),
            4: ("Supercruise", "In Supercruise"),
            5: ("FlightAssistOff", "Flight Assist is Off"),
            6: ("HardpointsDeployed", "Hardpoints are deployed"),
            7: ("InWing", "Flying in a wing"),
            8: ("LightsOn", "Ship lights are on"),
            9: ("CargoScoopDeployed", "Cargo scoop is deployed"),
            10: ("SilentRunning", "Silent Running mode active"),
            11: ("ScoopingFuel", "Scooping fuel"),
            12: ("SrvHandbrake", "SRV Handbrake engaged"),
            13: ("SrvTurretView", "SRV in Turret view"),
            14: ("SrvTurretRetracted", "SRV turret retracted"),
            15: ("SrvDriveAssist", "SRV Drive Assist enabled"),
            16: ("FsdMassLocked", "FSD Mass Locked"),
            17: ("FsdCharging", "FSD is charging"),
            18: ("FsdCooldown", "FSD in cooldown"),
            19: ("LowFuel", "Fuel below 25%"),
            20: ("OverHeating", "Ship overheating (>100%)"),
            21: ("HasLatLong", "Has latitude/longitude"),
            22: ("IsInDanger", "In danger / under attack"),
            23: ("BeingInterdicted", "Being interdicted"),
            24: ("InMainShip", "Currently in main ship"),
            25: ("InFighter", "Currently in fighter"),
            26: ("InSRV", "Currently in SRV"),
            27: ("AnalysisMode", "HUD in Analysis mode"),
            28: ("NightVision", "Night Vision active"),
            29: ("AltitudeFromAverage", "Altitude from average radius"),
            30: ("FsdJump", "Currently performing FSD Jump"),
            31: ("SrvHighBeam", "SRV High Beam lights on"),
        }

        active_flags = {}

        for bit, (short_name, description) in flag_definitions.items():
            mask = 1 << bit
            if flags_value & mask:
                active_flags[short_name] = description

        return active_flags


    def decode_gui_focus(self, gui_focus_value: int) -> str:

        gui_focus_definitions = {
            0: ("NoFocus", "No panel focused"),
            1: ("InternalPanel", "Right-hand internal panel"),
            2: ("ExternalPanel", "Left-hand external panel"),
            3: ("CommsPanel", "Top comms panel"),
            4: ("RolePanel", "Bottom role panel"),
            5: ("StationServices", "Station services menu"),
            6: ("GalaxyMap", "Galaxy map open"),
            7: ("SystemMap", "System map open"),
            8: ("Orrery", "Orrery view open"),
            9: ("FSSMode", "FSS (Full Spectrum Scanner) mode"),
            10: ("SAAMode", "SAA (Surface Area Analysis) mode"),
            11: ("Codex", "Codex / Knowledge Base open")
        }

        if gui_focus_value in gui_focus_definitions:
            short_name, description = gui_focus_definitions[gui_focus_value]
        #     return {"focus": short_name, "description": description}
            return short_name
        # return {"focus": "Unknown", "description": f"Unknown GuiFocus value: {gui_focus_value}"}
        return "Unknown"

    def test_flags(self):

        example_flags = 150994952
        print(f"Decoding Flags value: {example_flags}\n")

        result = self.decode_flags(example_flags)

        print("Active Flags:")
        for flag, desc in result.items():
            print(f"   • {flag:<20} : {desc}")

        print(f"\nTotal active flags: {len(result)}")

        status = {
            "Flags": 150994952,
            "GuiFocus": 6
        }

        print("GuiFocus:", self.decode_gui_focus(status["GuiFocus"]))

class StatusMonitor:
    """
    maintains the player state from the status json
    https://elite-journal.readthedocs.io/en/latest/Status%20File.html
    https://edcodex.info/?m=doc
    """

    def __init__(self, to_llm: Queue, shutdown_event: Event, shared_state: dict):
        self.Home_Station = "Csoma Ring"
        self.Commander_Name = "Luthis"
        self.to_llm = to_llm
        self.shared = shared_state
        self.shutdown_event = shutdown_event
        self.poll_interval=1.0

    def run(self):
        print(f"status mon started")
        try:
            while not self.shutdown_event.is_set():
                try:
                    with open(STATUS_FILE, "r") as file:
                        data = json.load(file)
                    self.shared["status_update"] = data

                except Exception as e:
                    pass
                time.sleep(self.poll_interval)

        except Exception as e:
            print(f"statusmon Error: {e}")

    def print_values(self):
        print(self.shared["status_update"].get("timestamp"))
        print(self.shared["status_update"].get("event"))
        print(self.shared["status_update"].get("Flags"))
        print(self.shared["status_update"].get("Latitude"))
        print(self.shared["status_update"].get("Longitude"))

    def set_home_station(self, home: str):
        if home:
            self.Home_Station = home
    def get_home_station(self) -> str:
        return self.Home_Station

    def decode_gui_focus(self, gui_focus_value: int) -> str:

        gui_focus_definitions = {
            0: ("NoFocus", "No panel focused"),
            1: ("InternalPanel", "Right-hand internal panel"),
            2: ("ExternalPanel", "Left-hand external panel"),
            3: ("CommsPanel", "Top comms panel"),
            4: ("RolePanel", "Bottom role panel"),
            5: ("StationServices", "Station services menu"),
            6: ("GalaxyMap", "Galaxy map open"),
            7: ("SystemMap", "System map open"),
            8: ("Orrery", "Orrery view open"),
            9: ("FSSMode", "FSS (Full Spectrum Scanner) mode"),
            10: ("SAAMode", "SAA (Surface Area Analysis) mode"),
            11: ("Codex", "Codex / Knowledge Base open")
        }

        if gui_focus_value in gui_focus_definitions:
            short_name, description = gui_focus_definitions[gui_focus_value]
        #     return {"focus": short_name, "description": description}
            return short_name
        # return {"focus": "Unknown", "description": f"Unknown GuiFocus value: {gui_focus_value}"}
        return "Unknown"

    def decode_flags(self, flags_value: int) -> dict:
        """
        Decodes the Elite Dangerous Status Flags integer into human-readable status.
        Args:
            flags_value (int): The Flags value from the Status event (e.g. 150994952)
        Returns:
            dict: Dictionary with active flags and their descriptions
        """

        flag_definitions = {
            0: ("Docked", "On a landing pad"),
            1: ("Landed", "On planet surface"),
            2: ("LandingGearDown", "Landing gear is down"),
            3: ("ShieldsUp", "Shields are active"),
            4: ("Supercruise", "In Supercruise"),
            5: ("FlightAssistOff", "Flight Assist is Off"),
            6: ("HardpointsDeployed", "Hardpoints are deployed"),
            7: ("InWing", "Flying in a wing"),
            8: ("LightsOn", "Ship lights are on"),
            9: ("CargoScoopDeployed", "Cargo scoop is deployed"),
            10: ("SilentRunning", "Silent Running mode active"),
            11: ("ScoopingFuel", "Scooping fuel"),
            12: ("SrvHandbrake", "SRV Handbrake engaged"),
            13: ("SrvTurretView", "SRV in Turret view"),
            14: ("SrvTurretRetracted", "SRV turret retracted"),
            15: ("SrvDriveAssist", "SRV Drive Assist enabled"),
            16: ("FsdMassLocked", "FSD Mass Locked"),
            17: ("FsdCharging", "FSD is charging"),
            18: ("FsdCooldown", "FSD in cooldown"),
            19: ("LowFuel", "Fuel below 25%"),
            20: ("OverHeating", "Ship overheating (>100%)"),
            21: ("HasLatLong", "Has latitude/longitude"),
            22: ("IsInDanger", "In danger / under attack"),
            23: ("BeingInterdicted", "Being interdicted"),
            24: ("InMainShip", "Currently in main ship"),
            25: ("InFighter", "Currently in fighter"),
            26: ("InSRV", "Currently in SRV"),
            27: ("AnalysisMode", "HUD in Analysis mode"),
            28: ("NightVision", "Night Vision active"),
            29: ("AltitudeFromAverage", "Altitude from average radius"),
            30: ("FsdJump", "Currently performing FSD Jump"),
            31: ("SrvHighBeam", "SRV High Beam lights on"),
        }

        active_flags = {}

        for bit, (short_name, description) in flag_definitions.items():
            mask = 1 << bit
            if flags_value & mask:
                active_flags[short_name] = description

        return active_flags

    def test_state(self):

        example_flags = 150994952

        print(f"Decoding Flags value: {example_flags}\n")

        result = self.decode_flags(example_flags)

        print("Active Flags:")
        for flag, desc in result.items():
            print(f"   • {flag:<20} : {desc}")

        print(f"\nTotal active flags: {len(result)}")

        status = {
            "Flags": 150994952,
            "GuiFocus": 6
        }

        print("GuiFocus:", self.decode_gui_focus(status["GuiFocus"]))
