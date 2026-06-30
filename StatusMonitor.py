import json
from multiprocessing import Queue, Event
import time
from PlayAudioFile import PlayAudioFile


STATUS_FILE='/media/ssd/SteamLibrary/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/Status.json'

# TODO: sent significant events to LLM (separate queue)

class Statest:

    def __init__(self, shared_state: dict):
        self.shared = shared_state

    def test_update(self):
        filename = 'dataref/Statuslatitude.json'
        with open(filename, "r") as file:
            data = json.load(file)

        self.shared["status_file"] = data
        print(self.shared)

    def decode_flags(self, flags_value: int) -> dict:
        """
        Decodes the Elite Dangerous Status Flags integer into human-readable status.
        Args:
            flags_value (int): The Flags value from the Status event (e.g. 150994952)
        Returns:
            dict: Dictionary with active flags and their descriptions

            Active Flags:
           • ShieldsUp            : Shields are active
           • InMainShip           : Currently in main ship
           • AnalysisMode         : HUD in Analysis mode
        """

        important_flags = {
            "Docked": "On a landing pad",
            "Landed": "On planet surface",
            "LandingGearDown": "Landing gear is down",
            "ShieldsUp": "Shields are active",
            "Supercruise": "In Supercruise",
            "HardpointsDeployed": "Hardpoints are deployed",
            "LightsOn": "Ship lights are on",
            "CargoScoopDeployed": "Cargo scoop is deployed",
            "ScoopingFuel": "Scooping fuel",
            "FsdMassLocked": "FSD Mass Locked",
            "FsdCharging": "FSD is charging",
            "FsdCooldown": "FSD in cooldown",
            "LowFuel": "Fuel below 25%",
            "OverHeating": "Ship overheating (>100%)",
            "HasLatLong": "in planet atmosphere with latitude/longitude",
            "IsInDanger": "In danger / under attack",
            "BeingInterdicted": "Being interdicted",
            "InMainShip": "Currently in main ship",
            "InFighter": "Currently in fighter",
            "InSRV": "Currently in SRV",
            "AnalysisMode": "HUD in Analysis mode",
            "NightVision": "Night Vision active",
            "AltitudeFromAverage": "Altitude from average radius",
            "FsdJump": "Currently performing FSD Jump",
            "SrvHighBeam": "SRV High Beam lights on",
        }


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

        self.shared.setdefault("flags_decoded", [])
        self.shared["flags_decoded"] = active_flags

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

        print(self.shared)

        # example_flags = 153157640
        example_flags = 1
        self.decode_flags(example_flags)
        print(self.shared)


class StatusMonitor:
    """
    maintains the player state from the status json
    https://elite-journal.readthedocs.io/en/latest/Status%20File.html
    https://edcodex.info/?m=doc

    { "timestamp":"2026-06-16T06:18:46Z", "event":"Status", "Flags":153157640, "Flags2":0, "Pips":[4,8,0], "FireGroup":0, "GuiFocus":0,
    "Fuel":{ "FuelMain":87.419518, "FuelReservoir":0.864385 }, "Cargo":0.000000, "LegalState":"Clean",
    "Latitude":34.901585, "Longitude":71.426796, "Heading":321, "Altitude":66, "BodyName":"Phylur UW-G b12-0 ABC 2 c",
    "PlanetRadius":927530.625000, "Balance":5402295250,
    "Destination":{ "System":637938182249, "Body":31, "Name":"Phylur UW-G b12-0 ABC 2 c" } }

    """

    def __init__(self, to_llm: Queue, shutdown_event: Event, shared_state: dict):
        self.to_llm = to_llm
        self.shared = shared_state
        self.shutdown_event = shutdown_event
        self.poll_interval=1.0
        self.ap = PlayAudioFile()
        self.shared["home_station"] = "Csoma Ring"
        self.shared["commander_name"] = "Luthis"

    def run(self):
        print(f"status mon started")
        try:
            while not self.shutdown_event.is_set():
                try:
                    with open(STATUS_FILE, "r") as file:
                        data = json.load(file)
                    self.shared["status_file"] = data

                except Exception as e:
                    pass
                time.sleep(self.poll_interval)

        except Exception as e:
            print(f"statusmon Error: {e}")

    def print_values(self):
        print(self.shared["status_file"].get("timestamp"))
        print(self.shared["status_file"].get("event"))
        print(self.shared["status_file"].get("Flags"))
        print(self.shared["status_file"].get("Latitude"))
        print(self.shared["status_file"].get("Longitude"))
        print(self.shared["status_file"].get("Heading"))
        print(self.shared["status_file"].get("Altitude"))
        print(self.shared["status_file"].get("BodyName"))
        print(self.shared["status_file"].get("PlanetRadius"))
        print(self.shared["status_file"].get("Destination"))

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

        important_flags = {
            "Docked": "On a landing pad",
            "Landed": "On planet surface",
            "LandingGearDown": "Landing gear is down",
            "ShieldsUp": "Shields are active",
            "Supercruise": "In Supercruise",
            "HardpointsDeployed": "Hardpoints are deployed",
            "LightsOn": "Ship lights are on",
            "CargoScoopDeployed": "Cargo scoop is deployed",
            "ScoopingFuel": "Scooping fuel",
            "FsdMassLocked": "FSD Mass Locked",
            "FsdCharging": "FSD is charging",
            "FsdCooldown": "FSD in cooldown",
            "LowFuel": "Fuel below 25%",
            "OverHeating": "Ship overheating (>100%)",
            "HasLatLong": "in planet atmosphere with latitude/longitude",
            "IsInDanger": "In danger / under attack",
            "BeingInterdicted": "Being interdicted",
            "InMainShip": "Currently in main ship",
            "InFighter": "Currently in fighter",
            "InSRV": "Currently in SRV",
            "AnalysisMode": "HUD in Analysis mode",
            "NightVision": "Night Vision active",
            "AltitudeFromAverage": "Altitude from average radius",
            "FsdJump": "Currently performing FSD Jump",
            "SrvHighBeam": "SRV High Beam lights on",
        }

        active_flags = {}

        for bit, (short_name, description) in flag_definitions.items():
            mask = 1 << bit
            if flags_value & mask:
                if short_name == "LowFuel" and not self.shared["major_warning_given"]:
                    self.ap.major_fuel_alert()
                    self.shared["major_warning_given"] = True
                active_flags[short_name] = description

        self.shared.setdefault("flags_decoded", [])
        self.shared["flags_decoded"] = active_flags

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
