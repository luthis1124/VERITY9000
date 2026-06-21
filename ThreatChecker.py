class ThreatChecker:
    """
    Class to check if a system is dangerous and return its threat level.
    """

    def __init__(self, dangerous_systems: dict = None):
        """
        Initialize with a dictionary of dangerous systems.

        Args:
            dangerous_systems (dict): Dictionary with system names as keys
                                     and threat levels as values.
        """
        self.dangerous_systems = {
        "San Tu": "Extreme threat",
        "Deciat": "High threat",
        "HIP 4981": "Medium threat",
        "Shinrarta Dezhra": "Medium threat",
        "Sol": "Medium threat",
        "HIP 112008": "Low threat",
        "Barnard's Star": "Low threat",
        "Cubeo": "Low threat",
        "Bunuson": "Low threat",
        "Niu Yun": "Low threat",
        "Synuefe PX-J c25-8": "Very low threat",
        "Colonia": "Very low threat",
        "Alpha Centauri": "Very low threat",
        "HIP 111823": "Very low threat",
        "Hyades Sector DB-X d1-112": "Very low threat"
    }

    def check_system(self, current_system: str):
        """
        Check if the current system is dangerous.

        Args:
            current_system (str): Name of the current system.

        Returns:
            dict: Contains 'is_dangerous', 'threat_level', and 'message'

            ⚠️ DANGEROUS SYSTEM: San Tu - Extreme threat
            ✅ Safe system: Duamta

        """
        if not current_system:
            print("no value in system variable")
            return {
                "is_dangerous": False,
                "threat_level": None,
            }

        # Normalize input (strip whitespace and capitalize properly)
        system_name = current_system.strip()

        if system_name in self.dangerous_systems:
            threat_level = self.dangerous_systems[system_name]
            return {
                "is_dangerous": True,
                "threat_level": threat_level,
            }
        else:
            return {
                "is_dangerous": False,
                "threat_level": None,
            }

    def is_dangerous(self, current_system: str) -> bool:
        """Simple boolean check if system is dangerous."""
        result = self.check_system(current_system)
        return result["is_dangerous"]

    def get_threat_level(self, current_system: str):
        """Return just the threat level or None if safe."""
        result = self.check_system(current_system)
        return result["threat_level"]

