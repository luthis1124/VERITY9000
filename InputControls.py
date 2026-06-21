import xml.etree.ElementTree as ET
from typing import Dict, Optional
import subprocess
import re
import time

BINDING_FILE = '/media/ssd/SteamLibrary/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings/Custom.4.2.binds'

class InputControls:
    """
    logically maps actions and keys taken from the control config

    <DeployHeatSink>
		<Primary Device="Keyboard" Key="Key_V" />
		<Secondary Device="{NoDevice}" Key="" />
	</DeployHeatSink>

    # Example usage:
    bindings = {
        'DeployHeatSink': {
            'primary': 'Keyboard:Key_V',
            'secondary': None,
            'primary_raw': 'Key_V',
            'secondary_raw': ''
        }
    }

    # Ctrl + V (Paste)
    xdotool key ctrl+v

    # Arrow Left
    xdotool key Left

    # Enter
    xdotool key Return

    # Escape
    xdotool key Escape


YawLeftButton             | Key_A
YawRightButton            | Key_D
LeftThrustButton          | Key_Q
RightThrustButton         | Key_E
UpThrustButton            | Key_R
DownThrustButton          | Key_F
ForwardKey                | Key_W
BackwardKey               | Key_S
SetSpeedZero              | Key_X
UseBoostJuice             | Key_Tab
HyperSuperCombination     | Key_F1
Supercruise               | Key_F2
SelectTarget              | Key_2
TargetNextRouteSystem     | Key_G
PrimaryFire               | Mouse_1
SecondaryFire             | Mouse_2
CycleFireGroupNext        | Key_1
CycleFireGroupPrevious    | Mouse_5
DeployHardpointToggle     | Key_3
DeployHeatSink            | Key_V
ShipSpotLightToggle       | Key_Insert
IncreaseEnginesPower      | Key_UpArrow
IncreaseWeaponsPower      | Key_RightArrow
IncreaseSystemsPower      | Key_LeftArrow
ResetPowerDistribution    | Key_DownArrow
ToggleCargoScoop          | Key_F4
LandingGearToggle         | Key_F3
UIFocus                   | Key_LeftShift
QuickCommsPanel           | Key_Enter
FocusRightPanel           | Key_4
GalaxyMapOpen             | Key_F7
SystemMapOpen             | Key_F8
PlayerHUDModeToggle       | Mouse_3
UI_Up                     | Key_W
UI_Down                   | Key_S
UI_Left                   | Key_A
UI_Right                  | Key_D
UI_Select                 | Key_Space
UI_Back                   | Key_Backspace
UI_Toggle                 | Key_Equals
CycleNextPanel            | Key_E
CyclePreviousPanel        | Key_Q
CycleNextPage             | Key_C
CyclePreviousPage         | Key_Z
GalaxyMapHome             | Key_Home

    """

    bindings = {}

    def __init__(self):
        self.bindings = self._import_bindings(BINDING_FILE)

    def resync_bindings(self):
        self.bindings = self._import_bindings(BINDING_FILE)

    def _import_bindings(self, file_path: str) -> Dict[str, Dict[str, str]]:
        """
        Parses Elite Dangerous key bindings file and returns a clean dictionary.
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Loop through all control bindings
            for control in root.findall("*"):  # Find all direct child elements
                control_name = control.tag  # e.g. "YawLeftButton"

                primary = None
                secondary = None

                # Get Primary binding
                primary_elem = control.find("Primary")
                if primary_elem is not None:
                    device = primary_elem.get("Device")
                    key = primary_elem.get("Key")
                    if device and key and device != "{NoDevice}" and key != "":
                        primary = f"{device}:{key}"

                # Get Secondary binding
                secondary_elem = control.find("Secondary")
                if secondary_elem is not None:
                    device = secondary_elem.get("Device")
                    key = secondary_elem.get("Key")
                    if device and key and device != "{NoDevice}" and key != "":
                        secondary = f"{device}:{key}"

                self.bindings[control_name] = {
                    "primary": primary,
                    "secondary": secondary,
                    "primary_raw": primary_elem.get("Key") if primary_elem is not None else None,
                    "secondary_raw": secondary_elem.get("Key") if secondary_elem is not None else None
                }

            print(f"✅ Successfully parsed {len(self.bindings)} controls from {file_path}")
            return self.bindings

        except Exception as e:
            print(f"❌ Error parsing keybindings file: {e}")
            return {}

    def print_controls(self, control_list: dict):
        for control in control_list:
            if control in self.bindings:
                data = self.bindings[control]
                print(f"{control:<25} → Primary: {data['primary_raw'] or 'None':<12} "
                      f"Secondary: {data['secondary_raw'] or 'None'}")

    def press_key(self, key: str):
        if len(key) == 1:
            key = key.lower()
        command = "xdotool keydown " + key
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keyup " + key
        subprocess.run(command, shell=True, executable="/bin/bash")
        print('pressed key ' + key)

    def do_action(self, action: str):
        try:
            key = self._extract_key_char(self.bindings[action])
        except (KeyError, TypeError) as e:
            print(f"Invalid action '{action}': {e}")
            return False

        if len(key) == 1:
            key = key.lower()
        command = "xdotool keydown " + key
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keyup " + key
        subprocess.run(command, shell=True, executable="/bin/bash")
        print('pressed key ' + key)
        return True

    def hold_action(self, action: str):
        key = self._extract_key_char(self.bindings[action])
        if len(key) == 1:
            key = key.lower()
        command = "xdotool keydown " + key
        subprocess.run(command, shell=True, executable="/bin/bash")
        print('holding key ' + key)

    def request_docking(self):
        UIFocus = self._extract_key_char(self.bindings["UIFocus"]).lower()
        UI_Left = self._extract_key_char(self.bindings["UI_Left"]).lower()
        UI_Right = self._extract_key_char(self.bindings["UI_Right"]).lower()
        UI_Select = self._extract_key_char(self.bindings["UI_Select"]).lower()
        CycleNextPanel = self._extract_key_char(self.bindings["CycleNextPanel"]).lower()
        # Ctrl + V (Paste)
        # xdotool        key        ctrl + v
        command = "xdotool keydown " + "shift"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keydown " + "a"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keyup " + "shift"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keyup " + "a"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)

        command = "xdotool keydown " + "e"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keyup " + "e"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keydown " + "e"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keyup " + "e"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keydown " + "d"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keyup " + "d"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.5)
        command = "xdotool keydown " + "space"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.5)
        command = "xdotool keyup " + "space"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keydown " + "shift"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        command = "xdotool keyup " + "shift"
        subprocess.run(command, shell=True, executable="/bin/bash")
        time.sleep(0.1)
        print("docking")

    def list_actions(self):
        print(self.bindings)

    def _extract_key_char(self, binding_dict):
        """
        Extracts the lowercase character from a binding dictionary.
        Assumes the format: {'primary': 'Keyboard:Key_X', ...}
        """
        primary = binding_dict.get('primary')

        if not primary:
            return None

        # Split by ':' and take the last part (e.g., 'Key_V' -> 'V')
        parts = primary.split(':')
        if len(parts) > 1:
            key_part = parts[-1]
            return re.sub(r'^Key_', '', key_part)
        #     # Return the last character in lowercase
        #     return key_part[-1].lower()
        #
        return None


    def list_active_primary_keys(self) -> str:
        """
        Iterates through the bindings dictionary and prints the control name
        and primary raw key only if the primary binding is not None.
        """
        # print(f"{'Control':<25} | {'Primary Raw Key':<20}")
        print("-" * 48)
        column = (f"{'Control':<25} | {'Primary Raw Key':<20}\n")
        column += ("-" * 48 + "\n")

        for control_name, data in self.bindings.items():
            # Check if 'primary' exists in the dict and is not None
            if data.get('primary') is not None:
                # Get the raw key, defaulting to 'N/A' if missing for safety
                raw_key = data.get('primary_raw', 'N/A')

                column += (f"{control_name:<25} | {raw_key:<20}\n")

                # Print formatted output
                # print(f"{control_name:<25} | {raw_key:<20}")

        # print(column)
        return column