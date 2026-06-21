import requests
import json
import requests
from typing import Dict, Any, Optional

class EDSM_API:

    def get_edsm_system(self, system_name):
        """
        Query EDSM API for system information.

        Args:
            system_name: Name of the star system to look up
            show_information: Whether to include additional info (default: True)

        Returns:
            dict: Parsed JSON response, or None if request fails

            HTTP Request: GET https://www.edsm.net/api-v1/system

            Parameter 	Default 	Description
            systemName* 	NULL            The system name
            showId 	0               Set to 1 to get our internal ID for this system.
            showCoordinates 	0 	Set to 1 to get the system coordinates. If coordinates are unknown, the coords key will not be returned.
            showPermit 	0 	        Set to 1 to get the system permit if there is one. If the permit is named, also return permitName.
            showInformation 	0 	 Set to 1 to get the system information like allegiance, government...  If no information is stored, an empty array will be returned.
            showPrimaryStar 	0    Set to 1 to get the system primary star if known. If no primary star is stored, a NULL will be returned.
            includeHidden 	0      Set to 1 to get system even if hidden in the database.  Hidden system are generally typo errors, renamed system in the game...

        """
        """
         HTTP Request: GET https://www.edsm.net/api-system-v1/factions 
         curl "https://www.edsm.net/api-system-v1/factions?systemName=HIP%2087621" | jq .
         %20 for space
         curl "https://www.edsm.net/api-system-v1/factions?systemName=IC%202391%20Sector%20CA-A%20d43" | jq .
         curl "https://www.edsm.net/api-v1/system?systemName=Anima&showInformation=1" | jq .

        """
        url = "https://www.edsm.net/api-v1/system"
        params = {
            "systemName": system_name,
            "showInformation": 1
        }
        headers = {
            "User-Agent": "MyPythonScript/1.0 (thisworkedbeforewithoutheaders@wtf.com)"
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors

            data = response.json()
            print(json.dumps(data, indent=2))  # Pretty-print JSON
            return data

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None

    def get_system_factions_safe(self, system_name: str) -> Optional[Dict[str, Any]]:
        """
        Safer version that returns None on failure instead of raising exceptions.
        """
        try:
            url = "https://www.edsm.net/api-system-v1/factions"
            headers = {
                "User-Agent": "MyPythonScript/1.0 (thisworkedbeforewithoutheaders@wtf.com)"
            }

            response = requests.get(
                url,
                params={"systemName": system_name},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching factions for {system_name}: {e}")
            return None

    def print_controlling_allegiance(self, data: dict) -> None:
        """
        Prints the allegiance of the controlling faction from EDSM system data.

        Args:
            data (dict): The JSON response from get_system_factions()
        """
        try:
            controlling = data.get("controllingFaction")

            if not controlling:
                print("No controlling faction found.")
                return

            allegiance = controlling.get("allegiance")

            if allegiance:
                print(f"Controlling Faction Allegiance: {allegiance}")
            else:
                print("Allegiance information not available.")

        except Exception as e:
            print(f"Error extracting allegiance: {e}")

    def print_controlling_faction_info(self, data: dict) -> None:
        """Prints detailed controlling faction information."""
        try:
            cf = data.get("controllingFaction")
            if not cf:
                print("No controlling faction data available.")
                return

            print(f"System: {data.get('name')}")
            print(f"Controlling Faction: {cf.get('name')}")
            print(f"Allegiance: {cf.get('allegiance')}")
            print(f"Government: {cf.get('government')}")

        except Exception as e:
            print(f"Error: {e}")