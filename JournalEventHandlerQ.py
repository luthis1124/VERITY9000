import time
from multiprocessing import Process, Queue, Event
from RareCommodityChecker import RareCommodityChecker
from ThreatChecker import ThreatChecker
from StatusMonitor import StatusMonitor
from InputControls import InputControls
from POIChecker import POIChecker
from PlayAudioFile import PlayAudioFile


class JournalEventHandlerQ:

    def __init__(self, to_ev: Queue, to_ev_initial: Queue, to_tts: Queue, shutdown_event: Event, shared_state: dict):
        self.to_ev = to_ev
        self.to_ev_initial = to_ev_initial
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
                if self.shared["first_run"]:
                    try:
                        init_request = self.to_ev_initial.get(timeout=3)
                        if init_request:
                                 self.handle_event_initial(init_request)
                    except Exception as e:
                        print("reached end of initial")
                        self.shared["first_run"] = False
                else:
                    try:

                        request = self.to_ev.get(timeout=1)

                        # print(f"journal handler Received request: {request}")

                        # print("first run: " + str(self.shared["first_run"]))
                        if request:
                            # if self.shared["first_run"]:
                            #     self.handle_event_initial(request)
                            #     # print("first run ev request: " + str(request))
                            # else:
                            #     # print("handling secondary")
                            #     self.handle_event(request)
                            self.handle_event(request)

                    except Exception as e:
                        # print(f"run event Error, maybe finished?: {e}")
                        # self.shared["first_run"] = False
                        pass

        except Exception as e:
            print(f"event Error: {e}")

    def handle_event(self, data: dict):
        """
        Handle specific events with match-case.
        Takes the full parsed JSON dictionary.

        {'timestamp': '2026-06-25T03:09:17Z', 'event': 'Location', 'Latitude': -7.783652, 'Longitude': -88.452721, 'DistFromStarLS': 32.435543, 'Docked': False, 'Taxi': False, 'Multicrew': False, 'StarSystem': 'Phylur TF-V c3-5',
        'SystemAddress': 1453947491362, 'StarPos': [-2559.40625, 491.375, 1674.625], 'SystemAllegiance': '', 'SystemEconomy': '$economy_None;', 'SystemEconomy_Localised': 'None', 'SystemSecondEconomy': '$economy_None;',
        'SystemSecondEconomy_Localised': 'None', 'SystemGovernment': '$government_None;', 'SystemGovernment_Localised': 'None', 'SystemSecurity': '$GAlAXY_MAP_INFO_state_anarchy;', 'SystemSecurity_Localised': 'Anarchy', 'Population': 0,
        'Body': 'Phylur TF-V c3-5 3', 'BodyID': 7, 'BodyType': 'Planet'}
        {'timestamp': '2026-06-25T03:09:17Z', 'event': 'Loadout', 'Ship': 'explorer_nx', 'ShipID': 9, 'ShipName': 'sun treader', 'ShipIdent': 'LU-cs1', 'ModulesValue': 406418918, 'HullHealth': 0.981151, 'UnladenMass': 1482.494995, 'CargoCapacity': 267, 'MaxJumpRange': 76.422279, 'FuelCapacity': {'Main': 128.0, 'Reserve': 1.14}, 'Rebuy': 20320947, 'Modules': [{'Slot': 'LargeHardpoint1', 'Item': 'hpt_basicmissilerack_fixed_large', 'On': True, 'Priority': 3, 'AmmoInClip': 6, 'AmmoInHopper': 36, 'Health': 0.843867, 'Value': 1471031, 'Engineering': {'Engineer': 'Liz Ryder', 'EngineerID': 300080, 'BlueprintID': 128682060, 'BlueprintName': 'Weapon_RapidFire', 'Level': 5, 'Quality': 1.0, 'ExperimentalEffect': 'special_weapon_efficient', 'ExperimentalEffect_Localised': 'Flow Control', 'Modifiers': [{'Label': 'PowerDraw', 'Value': 1.458, 'OriginalValue': 1.62, 'LessIsGood': 1}, {'Label': 'DamagePerSecond', 'Value': 22.619047, 'OriginalValue': 13.333334, 'LessIsGood': 0}, {'Label': 'Damage', 'Value': 38.0, 'OriginalValue': 40.0, 'LessIsGood': 0}, {'Label': 'DistributorDraw', 'Value': 0.156, 'OriginalValue': 0.24, 'LessIsGood': 1}, {'Label': 'RateOfFire', 'Value': 0.595238, 'OriginalValue': 0.333333, 'LessIsGood': 0}, {'Label': 'ReloadTime', 'Value': 4.2, 'OriginalValue': 12.0, 'LessIsGood': 1}, {'Label': 'Jitter', 'Value': 0.5, 'OriginalValue': 0.0, 'LessIsGood': 1}]}}, {'Slot': 'MediumHardpoint6', 'Item': 'hpt_pulselaserburst_gimbal_medium', 'On': False, 'Priority': 3, 'Health': 0.679658, 'Value': 48500}, {'Slot': 'MediumHardpoint5', 'Item': 'hpt_mininglaser_fixed_medium', 'On': False, 'Priority': 4, 'Health': 0.789464, 'Value': 22012}, {'Slot': 'MediumHardpoint1', 'Item': 'hpt_mining_abrblstr_fixed_small', 'On': False, 'Priority': 4, 'Health': 0.712143, 'Value': 9458}, {'Slot': 'MediumHardpoint2', 'Item': 'hpt_flakmortar_fixed_medium', 'On': True, 'Priority': 4, 'AmmoInClip': 1, 'AmmoInHopper': 32, 'Health': 0.818029, 'Value': 255255}, {'Slot': 'MediumHardpoint3', 'Item': 'hpt_railgun_fixed_medium', 'On': True, 'Priority': 3, 'AmmoInClip': 1, 'AmmoInHopper': 80, 'Health': 0.634244, 'Value': 402480, 'Engineering': {'Engineer': 'Etienne Dorn', 'EngineerID': 300290, 'BlueprintID': 128673609, 'BlueprintName': 'Weapon_LightWeight', 'Level': 5, 'Quality': 1.0, 'ExperimentalEffect': 'special_super_penetrator_cooled', 'ExperimentalEffect_Localised': '$special_super_penetrator_name;', 'Modifiers': [{'Label': 'Mass', 'Value': 0.4, 'OriginalValue': 4.0, 'LessIsGood': 1}, {'Label': 'Integrity', 'Value': 20.4, 'OriginalValue': 51.0, 'LessIsGood': 0}, {'Label': 'PowerDraw', 'Value': 0.978, 'OriginalValue': 1.63, 'LessIsGood': 1}, {'Label': 'DistributorDraw', 'Value': 3.3215, 'OriginalValue': 5.11, 'LessIsGood': 1}, {'Label': 'ThermalLoad', 'Value': 12.0, 'OriginalValue': 20.0, 'LessIsGood': 1}, {'Label': 'ReloadTime', 'Value': 1.5, 'OriginalValue': 1.0, 'LessIsGood': 1}]}}, {'Slot': 'MediumHardpoint4', 'Item': 'hpt_mining_subsurfdispmisle_fixed_medium', 'On': False, 'Priority': 0, 'AmmoInClip': 1, 'AmmoInHopper': 96, 'Health': 0.820975, 'Value': 107205}, {'Slot': 'TinyHardpoint1', 'Item': 'hpt_heatsinklauncher_turret_tiny', 'On': True, 'Priority': 0, 'AmmoInClip': 1, 'AmmoInHopper': 1, 'Health': 0.92942, 'Value': 3500, 'Engineering': {'Engineer': 'Ram Tah', 'EngineerID': 300110, 'BlueprintID': 128731666, 'BlueprintName': 'Misc_HeatSinkCapacity', 'Level': 1, 'Quality': 1.0, 'Modifiers': [{'Label': 'Mass', 'Value': 2.6, 'OriginalValue': 1.3, 'LessIsGood': 1}, {'Label': 'AmmoMaximum', 'Value': 3.0, 'OriginalValue': 2.0, 'LessIsGood': 0}, {'Label': 'ReloadTime', 'Value': 15.0, 'OriginalValue': 10.0, 'LessIsGood': 1}]}}, {'Slot': 'TinyHardpoint2', 'Item': 'hpt_heatsinklauncher_turret_tiny', 'On': True, 'Priority': 1, 'AmmoInClip': 1, 'AmmoInHopper': 0, 'Health': 0.90522, 'Value': 3500, 'Engineering': {'Engineer': 'Ram Tah', 'EngineerID': 300110, 'BlueprintID': 128731666, 'BlueprintName': 'Misc_HeatSinkCapacity', 'Level': 1, 'Quality': 1.0, 'Modifiers': [{'Label': 'Mass', 'Value': 2.6, 'OriginalValue': 1.3, 'LessIsGood': 1}, {'Label': 'AmmoMaximum', 'Value': 3.0, 'OriginalValue': 2.0, 'LessIsGood': 0}, {'Label': 'ReloadTime', 'Value': 15.0, 'OriginalValue': 10.0, 'LessIsGood': 1}]}}, {'Slot': 'TinyHardpoint3', 'Item': 'hpt_shieldbooster_size0_class5', 'On': True, 'Priority': 1, 'Health': 0.863748, 'Value': 273975, 'Engineering': {'Engineer': 'Lei Cheung', 'EngineerID': 300120, 'BlueprintID': 128673782, 'BlueprintName': 'ShieldBooster_HeavyDuty', 'Level': 3, 'Quality': 1.0, 'ExperimentalEffect': 'special_shieldbooster_efficient', 'ExperimentalEffect_Localised': 'Flow Control', 'Modifiers': [{'Label': 'Mass', 'Value': 10.5, 'OriginalValue': 3.5, 'LessIsGood': 1}, {'Label': 'Integrity', 'Value': 52.32, 'OriginalValue': 48.0, 'LessIsGood': 0}, {'Label': 'PowerDraw', 'Value': 1.242, 'OriginalValue': 1.2, 'LessIsGood': 1}, {'Label': 'DefenceModifierShieldMultiplier', 'Value': 48.800003, 'OriginalValue': 20.000004, 'LessIsGood': 0}]}}, {'Slot': 'TinyHardpoint4', 'Item': 'hpt_shieldbooster_size0_class5', 'On': True, 'Priority': 1, 'Health': 0.826491, 'Value': 273975, 'Engineering': {'Engineer': 'Lei Cheung', 'EngineerID': 300120, 'BlueprintID': 128673792, 'BlueprintName': 'ShieldBooster_Resistive', 'Level': 3, 'Quality': 1.0, 'ExperimentalEffect': 'special_shieldbooster_efficient', 'ExperimentalEffect_Localised': 'Flow Control', 'Modifiers': [{'Label': 'Integrity', 'Value': 44.16, 'OriginalValue': 48.0, 'LessIsGood': 0}, {'Label': 'PowerDraw', 'Value': 1.242, 'OriginalValue': 1.2, 'LessIsGood': 1}, {'Label': 'KineticResistance', 'Value': 11.000002, 'OriginalValue': 0.0, 'LessIsGood': 0}, {'Label': 'ThermicResistance', 'Value': 11.000002, 'OriginalValue': 0.0, 'LessIsGood': 0}, {'Label': 'ExplosiveResistance', 'Value': 11.000002, 'OriginalValue': 0.0, 'LessIsGood': 0}]}}, {'Slot': 'TinyHardpoint5', 'Item': 'hpt_cloudscanner_size0_class5', 'On': False, 'Priority': 4, 'Health': 0.778347, 'Value': 1069668, 'Engineering': {'Engineer': 'Etienne Dorn', 'EngineerID': 300290, 'BlueprintID': 128740096, 'BlueprintName': 'Sensor_LongRange', 'Level': 5, 'Quality': 1.0, 'Modifiers': [{'Label': 'PowerDraw', 'Value': 4.8, 'OriginalValue': 3.2, 'LessIsGood': 1}, {'Label': 'ScannerRange', 'Value': 8800.0, 'OriginalValue': 4000.0, 'LessIsGood': 0}, {'Label': 'MaxAngle', 'Value': 10.5, 'OriginalValue': 15.0, 'LessIsGood': 0}]}}, {'Slot': 'TinyHardpoint6', 'Item': 'hpt_mrascanner_size0_class5', 'On': False, 'Priority': 4, 'Health': 0.835104, 'Value': 1069668}, {'Slot': 'Armour', 'Item': 'explorer_nx_armour_grade3', 'On': True, 'Priority': 1, 'Health': 1.0, 'Value': 170990782, 'Engineering': {'Engineer': 'Selene Jean', 'EngineerID': 300210, 'BlueprintID': 128673634, 'BlueprintName': 'Armour_Advanced', 'Level': 5, 'Quality': 1.0, 'ExperimentalEffect': 'special_armour_chunky', 'ExperimentalEffect_Localised': 'Deep Plating', 'Modifiers': [{'Label': 'Mass', 'Value': 27.0, 'OriginalValue': 60.0, 'LessIsGood': 1}, {'Label': 'DefenceModifierHealthMultiplier', 'Value': 259.100006, 'OriginalValue': 250.0, 'LessIsGood': 0}, {'Label': 'KineticResistance', 'Value': -5.060005, 'OriginalValue': -20.000004, 'LessIsGood': 0}, {'Label': 'ThermicResistance', 'Value': 12.449998, 'OriginalValue': 0.0, 'LessIsGood': 0}, {'Label': 'ExplosiveResistance', 'Value': -22.570002, 'OriginalValue': -39.999996, 'LessIsGood': 0}]}}, {'Slot': 'PaintJob', 'Item': 'paintjob_explorer_nx_03_05', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'Decal1', 'Item': 'decal_squadronlogo_dynamic', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'Decal2', 'Item': 'decal_explorer_starblazer', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'Decal3', 'Item': 'decal_caspianownersclub_01', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'ShipName0', 'Item': 'nameplate_alliance03_white', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'ShipName1', 'Item': 'nameplate_alliance03_white', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'ShipID0', 'Item': 'nameplate_shipid_white', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'ShipID1', 'Item': 'nameplate_shipid_white', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'PowerPlant', 'Item': 'int_powerplant_size7_class5', 'On': True, 'Priority': 1, 'Health': 0.995871, 'Value': 38913291, 'Engineering': {'Engineer': 'Hera Tani', 'EngineerID': 300090, 'BlueprintID': 128673764, 'BlueprintName': 'PowerPlant_Armoured', 'Level': 5, 'Quality': 1.0, 'ExperimentalEffect': 'special_powerplant_highcharge', 'ExperimentalEffect_Localised': 'Monstered', 'Modifiers': [{'Label': 'Mass', 'Value': 52.800003, 'OriginalValue': 40.0, 'LessIsGood': 1}, {'Label': 'Integrity', 'Value': 316.800018, 'OriginalValue': 144.0, 'LessIsGood': 0}, {'Label': 'PowerCapacity', 'Value': 35.279995, 'OriginalValue': 30.0, 'LessIsGood': 0}, {'Label': 'HeatEfficiency', 'Value': 0.352, 'OriginalValue': 0.4, 'LessIsGood': 1}]}}, {'Slot': 'MainEngines', 'Item': 'int_engine_size7_class5_gravityoptimised_mkii', 'On': False, 'Priority': 0, 'Health': 0.901155, 'Value': 68368387, 'Engineering': {'Engineer': 'Professor Palin', 'EngineerID': 300220, 'BlueprintID': 128673659, 'BlueprintName': 'Engine_Dirty', 'Level': 5, 'Quality': 1.0, 'ExperimentalEffect': 'special_engine_overloaded', 'ExperimentalEffect_Localised': 'Drag Drives', 'Modifiers': [{'Label': 'Integrity', 'Value': 122.400002, 'OriginalValue': 144.0, 'LessIsGood': 0}, {'Label': 'PowerDraw', 'Value': 10.2144, 'OriginalValue': 9.12, 'LessIsGood': 1}, {'Label': 'EngineOptimalMass', 'Value': 1890.0, 'OriginalValue': 2160.0, 'LessIsGood': 0}, {'Label': 'EngineOptPerformance', 'Value': 145.599991, 'OriginalValue': 100.0, 'LessIsGood': 0}, {'Label': 'EngineHeatRate', 'Value': 2.288, 'OriginalValue': 1.3, 'LessIsGood': 1}]}}, {'Slot': 'FrameShiftDrive', 'Item': 'int_hyperdrive_overcharge_size8_class5_overchargebooster_mkii', 'On': True, 'Priority': 0, 'Health': 0.936941, 'Value': 82042064, 'Engineering': {'Engineer': 'Felicity Farseer', 'EngineerID': 300100, 'BlueprintID': 128673694, 'BlueprintName': 'FSD_LongRange', 'Level': 5, 'Quality': 1.0, 'ExperimentalEffect': 'special_fsd_heavy', 'ExperimentalEffect_Localised': 'Mass Manager', 'Modifiers': [{'Label': 'Mass', 'Value': 208.0, 'OriginalValue': 160.0, 'LessIsGood': 1}, {'Label': 'Integrity', 'Value': 147.016006, 'OriginalValue': 188.0, 'LessIsGood': 0}, {'Label': 'PowerDraw', 'Value': 1.2075, 'OriginalValue': 1.05, 'LessIsGood': 1}, {'Label': 'FSDOptimalMass', 'Value': 7528.039551, 'OriginalValue': 4670.0, 'LessIsGood': 0}]}}, {'Slot': 'LifeSupport', 'Item': 'int_lifesupport_size5_class5', 'On': True, 'Priority': 0, 'Health': 0.965217, 'Value': 1210285, 'Engineering': {'Engineer': 'Etienne Dorn', 'EngineerID': 300290, 'BlueprintID': 128731495, 'BlueprintName': 'Misc_LightWeight', 'Level': 5, 'Quality': 1.0, 'Modifiers': [{'Label': 'Mass', 'Value': 3.0, 'OriginalValue': 20.0, 'LessIsGood': 1}, {'Label': 'Integrity', 'Value': 57.5, 'OriginalValue': 115.0, 'LessIsGood': 0}]}}, {'Slot': 'PowerDistributor', 'Item': 'int_powerdistributor_size6_class5', 'On': True, 'Priority': 0, 'Health': 0.895044, 'Value': 3475688, 'Engineering': {'Engineer': 'The Dweller', 'EngineerID': 300180, 'BlueprintID': 128673739, 'BlueprintName': 'PowerDistributor_HighFrequency', 'Level': 5, 'Quality': 1.0, 'ExperimentalEffect': 'special_powerdistributor_fast', 'ExperimentalEffect_Localised': 'Super Conduits', 'Modifiers': [{'Label': 'WeaponsCapacity', 'Value': 45.599998, 'OriginalValue': 50.0, 'LessIsGood': 0}, {'Label': 'WeaponsRecharge', 'Value': 7.841599, 'OriginalValue': 5.2, 'LessIsGood': 0}, {'Label': 'EnginesCapacity', 'Value': 31.92, 'OriginalValue': 35.0, 'LessIsGood': 0}, {'Label': 'EnginesRecharge', 'Value': 4.8256, 'OriginalValue': 3.2, 'LessIsGood': 0}, {'Label': 'SystemsCapacity', 'Value': 31.92, 'OriginalValue': 35.0, 'LessIsGood': 0}, {'Label': 'SystemsRecharge', 'Value': 4.8256, 'OriginalValue': 3.2, 'LessIsGood': 0}]}}, {'Slot': 'Radar', 'Item': 'int_sensors_size8_class2', 'On': True, 'Priority': 0, 'Health': 0.908764, 'Value': 1700362, 'Engineering': {'Engineer': 'Juri Ishmaak', 'EngineerID': 300250, 'BlueprintID': 128740673, 'BlueprintName': 'Sensor_LightWeight', 'Level': 5, 'Quality': 1.0, 'Modifiers': [{'Label': 'Mass', 'Value': 12.799999, 'OriginalValue': 64.0, 'LessIsGood': 1}, {'Label': 'Integrity', 'Value': 60.0, 'OriginalValue': 120.0, 'LessIsGood': 0}, {'Label': 'SensorTargetScanAngle', 'Value': 22.5, 'OriginalValue': 30.0, 'LessIsGood': 0}]}}, {'Slot': 'FuelTank', 'Item': 'int_fueltank_size7_class3', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'Slot01_Size7', 'Item': 'int_cargorack_size7_class1', 'On': True, 'Priority': 1, 'Health': 1.0, 'Value': 1148960}, {'Slot': 'Slot02_Size6', 'Item': 'int_shieldgenerator_size6_class5', 'On': True, 'Priority': 0, 'Health': 0.992647, 'Value': 15775043, 'Engineering': {'Engineer': 'Lei Cheung', 'EngineerID': 300120, 'BlueprintID': 128673839, 'BlueprintName': 'ShieldGenerator_Reinforced', 'Level': 5, 'Quality': 1.0, 'ExperimentalEffect': 'special_shield_health', 'ExperimentalEffect_Localised': 'Hi-Cap', 'Modifiers': [{'Label': 'PowerDraw', 'Value': 4.774, 'OriginalValue': 4.34, 'LessIsGood': 1}, {'Label': 'ShieldGenStrength', 'Value': 175.535995, 'OriginalValue': 120.000008, 'LessIsGood': 0}, {'Label': 'BrokenRegenRate', 'Value': 4.797, 'OriginalValue': 5.33, 'LessIsGood': 0}, {'Label': 'EnergyPerRegen', 'Value': 0.84, 'OriginalValue': 0.6, 'LessIsGood': 1}, {'Label': 'KineticResistance', 'Value': 49.900002, 'OriginalValue': 39.999996, 'LessIsGood': 0}, {'Label': 'ThermicResistance', 'Value': -0.199997, 'OriginalValue': -20.000004, 'LessIsGood': 0}, {'Label': 'ExplosiveResistance', 'Value': 58.25, 'OriginalValue': 50.0, 'LessIsGood': 0}]}}, {'Slot': 'Slot03_Size6', 'Item': 'int_cargorack_size6_class1', 'On': True, 'Priority': 1, 'Health': 1.0, 'Value': 362591}, {'Slot': 'Slot04_Size5', 'Item': 'int_guardianfsdbooster_size5', 'On': True, 'Priority': 2, 'Health': 0.984375, 'Value': 6483100}, {'Slot': 'Slot05_Size5', 'Item': 'int_cargorack_size5_class1', 'On': True, 'Priority': 1, 'Health': 1.0, 'Engineering': {'EngineerID': 399999, 'BlueprintID': 129036395, 'BlueprintName': 'CargoRack_IncreasedCapacity', 'Level': 5, 'Quality': 1.0, 'Modifiers': [{'Label': 'CargoCapacity', 'Value': 43.0, 'OriginalValue': 32.0, 'LessIsGood': 0}]}}, {'Slot': 'Slot06_Size5', 'Item': 'int_cargorack_size5_class1', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'Slot07_Size5', 'Item': 'int_fuelscoop_size5_class5', 'On': True, 'Priority': 0, 'Health': 0.904818, 'Value': 9073694}, {'Slot': 'Slot08_Size4', 'Item': 'int_buggybay_size4_class2', 'On': True, 'Priority': 4, 'Health': 0.97987, 'Value': 84240}, {'Slot': 'Slot09_Size4', 'Item': 'int_dronecontrol_collection_size3_class4', 'On': False, 'Priority': 4, 'Health': 0.965568, 'Value': 50544, 'Engineering': {'Engineer': 'Marsha Hicks', 'EngineerID': 300150, 'BlueprintID': 128731530, 'BlueprintName': 'Misc_LightWeight', 'Level': 5, 'Quality': 1.0, 'Modifiers': [{'Label': 'Mass', 'Value': 1.2, 'OriginalValue': 8.0, 'LessIsGood': 1}, {'Label': 'Integrity', 'Value': 38.5, 'OriginalValue': 77.0, 'LessIsGood': 0}]}}, {'Slot': 'Slot10_Size3', 'Item': 'int_multidronecontrol_rescue_size3_class3', 'On': False, 'Priority': 4, 'Health': 0.973576, 'Value': 48750}, {'Slot': 'Slot11_Size2', 'Item': 'int_repairer_size2_class5', 'On': True, 'Priority': 0, 'Health': 0.915801, 'Value': 1421550, 'Engineering': {'Engineer': 'Bill Turner', 'EngineerID': 300010, 'BlueprintID': 128731658, 'BlueprintName': 'Misc_Shielded', 'Level': 3, 'Quality': 1.0, 'Modifiers': [{'Label': 'Integrity', 'Value': 165.199997, 'OriginalValue': 59.0, 'LessIsGood': 0}, {'Label': 'PowerDraw', 'Value': 2.528, 'OriginalValue': 1.58, 'LessIsGood': 1}]}}, {'Slot': 'Slot12_Size1', 'Item': 'int_detailedsurfacescanner_tiny', 'On': True, 'Priority': 0, 'Health': 0.994288, 'Value': 250000, 'Engineering': {'Engineer': 'Juri Ishmaak', 'EngineerID': 300250, 'BlueprintID': 128740151, 'BlueprintName': 'Sensor_Expanded', 'Level': 5, 'Quality': 1.0, 'Modifiers': [{'Label': 'PowerDraw', 'Value': 0.0, 'OriginalValue': 0.0, 'LessIsGood': 1}, {'Label': 'DSS_PatchRadius', 'Value': 30.0, 'OriginalValue': 20.0, 'LessIsGood': 0}]}}, {'Slot': 'Slot13_Size1', 'Item': 'int_supercruiseassist', 'On': True, 'Priority': 4, 'Health': 0.85}, {'Slot': 'Slot14_Size1', 'Item': 'int_dronecontrol_prospector_size1_class5', 'On': False, 'Priority': 4, 'Health': 0.98307, 'Value': 9360, 'Engineering': {'Engineer': 'Marsha Hicks', 'EngineerID': 300150, 'BlueprintID': 128731520, 'BlueprintName': 'Misc_LightWeight', 'Level': 5, 'Quality': 1.0, 'Modifiers': [{'Label': 'Mass', 'Value': 0.195, 'OriginalValue': 1.3, 'LessIsGood': 1}, {'Label': 'Integrity', 'Value': 28.0, 'OriginalValue': 56.0, 'LessIsGood': 0}]}}, {'Slot': 'PlanetaryApproachSuite', 'Item': 'int_planetapproachsuite_advanced', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'Bobble10', 'Item': 'bobble_snowman', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'WeaponColour', 'Item': 'weaponcustomisation_blue', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'EngineColour', 'Item': 'enginecustomisation_red', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'VesselVoice', 'Item': 'voicepack_verity', 'On': True, 'Priority': 1, 'Health': 1.0}, {'Slot': 'ShipCockpit', 'Item': 'explorer_nx_cockpit', 'On': True, 'Priority': 1, 'Health': 0.980678}, {'Slot': 'CargoHatch', 'Item': 'modularcargobaydoor', 'On': True, 'Priority': 4, 'Health': 0.925}]}

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

            case "Location":
                self.shared["system_name"] = (data.get('StarSystem', 'Unknown'))
                self.shared["system_address"] = (data.get('SystemAddress', ''))
                self.shared["star_pos"] = (data.get('StarPos', ''))
                self.shared["system_alliegance"] = (data.get('SystemAllegiance', ''))
                self.shared["body_id"] = data.get('BodyID', 'Unknown')
                self.shared["body_name"] = data.get('Body', 'Unknown')

            case "JetConeBoost":
                self.shared["BoostValue"] = (data.get('BoostValue', '0.0'))

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
                self.shared["BoostValue"] = '0.0'
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

                if body == self.shared["home_station"]:
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

        # print("trying handle initial")
        if not isinstance(data, dict) or 'event' not in data:
            return

        event = data['event']
        print("matching initial event: " + event)
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
                print("current system set: " + self.shared["system_name"])
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
            case "Location":
                print("found location")
                self.shared["system_name"] = (data.get('StarSystem', 'Unknown'))
                self.shared["system_address"] = (data.get('SystemAddress', ''))
                self.shared["star_pos"] = (data.get('StarPos', ''))
                self.shared["system_alliegance"] = (data.get('SystemAllegiance', ''))
                self.shared["body_id"] = data.get('BodyID', 'Unknown')
                self.shared["body_name"] = data.get('Body', 'Unknown')

                print("current system set: " + self.shared["system_name"])
            case _:
                pass

    def on_system_enter(self, StarSystem: str):

        self.shared.setdefault("visited_systems", []).append(StarSystem)

        jumpinfo = "System " + StarSystem
        self.to_tts.put(jumpinfo)

        level = self.shared["fuel_level"]
        fuelcap = self.shared["fuel_capacity"]

        if fuelcap / level < 2.0:
            self.fuel_warning_given = False

        elif fuelcap / level > 2.0 and not self.fuel_warning_given:
            self.fuel_warning_given = True
            time.sleep(5)

            self.ap.fuel_alert()

        elif fuelcap / level > 4.0:
            time.sleep(5)

            self.ap.major_fuel_alert()


        tc = ThreatChecker()
        if tc.is_dangerous(StarSystem):
            time.sleep(5)
            self.ap.high_threat()


        rc = RareCommodityChecker()
        result = rc.check(StarSystem)
        if result["found"]:
            commodity_message = "Rare goods sold in station " + result["station"]
            time.sleep(5)
            self.to_tts.put(commodity_message)
            system = StarSystem.strip()

            self.shared.setdefault("visited_rare_goods", [])
            if system not in self.shared["visited_rare_goods"]:
                self.shared["visited_rare_goods"].append(system)

        poi = POIChecker()
        poi_result = poi.check_system(StarSystem)
        self.shared["system_poi"] = poi_result
        if poi_result:
            time.sleep(5)
            if len(poi_result) == 1:
                self.ap.poi_message()
            elif len(poi_result) > 1:
                self.ap.multiple_poi_message()
