from pymongo import MongoClient
from typing import Tuple, List, Optional

class DBTools:

    def find_nearest(self,
        player_coords: Tuple[float, float, float],  # (x, y, z)
        limit: int = 5,
        service: str = "Refuel"
    ) -> List[dict]:
        """
        Find the closest stations that offer 'Interstellar Factors Contact'.

        Returns a list of stations sorted by distance (closest first).
        """

        ports = [
            "Asteroid base",
            "Coriolis Starport",
            "Orbis Starport",
            "Fleet Carrier",
            "Mega ship",
            "Ocellus Starport",
            "Planetary Port"
        ]
        outposts = [
            "Outpost",
            "Planetary Outpost",
            "Odyssey Settlement"
        ]
        db_name = "mongotest"
        collection_name = "stations"
        client = MongoClient("mongodb://localhost:27017/")

        try:
            collection = client[db_name][collection_name]

            # Service filter
            query = {
                "coords": {"$exists": True},
                "type": {
                    "$in": ports
                },
                "otherServices": service  # Looks for exact match in array
            }

            pipeline = [
                {"$match": query},
                {
                    "$addFields": {
                        "distance": {
                            "$sqrt": {
                                "$add": [
                                    {"$pow": [{"$subtract": [player_coords[0], "$coords.x"]}, 2]},
                                    {"$pow": [{"$subtract": [player_coords[1], "$coords.y"]}, 2]},
                                    {"$pow": [{"$subtract": [player_coords[2], "$coords.z"]}, 2]}
                                ]
                            }
                        }
                    }
                },
                {"$sort": {"distance": 1}},
                {"$limit": limit},
                {
                    "$project": {
                        "_id": 0,
                        "name": 1,
                        "systemName": 1,
                        "type": 1,
                        "distanceToArrival": 1,
                        "distance": 1,
                        "allegiance": 1,
                        "government": 1,
                        "economy": 1,
                        "haveMarket": 1,
                        "haveShipyard": 1,
                        "haveOutfitting": 1,
                        "otherServices": 1,
                        "coords": 1
                    }
                }
            ]

            results = list(collection.aggregate(pipeline, allowDiskUse=True))

            return results

        except Exception as e:
            print(f"Error finding nearest Interstellar Factors station: {e}")
            return []
        finally:
            if client:
                client.close()


    def find_nearest_rares(self,
        player_coords: Tuple[float, float, float],  # (x, y, z)
        limit: int = 20,
    ) -> List[dict]:
        """
        Find the closest stations that offer 'Interstellar Factors Contact'.

        Returns a list of stations sorted by distance (closest first).
        """

        db_name = "mongotest"
        collection_name = "stations"
        client = MongoClient("mongodb://localhost:27017/")

        ports = [
            "Asteroid base",
            "Coriolis Starport",
            "Orbis Starport",
            "Fleet Carrier",
            "Mega ship",
            "Ocellus Starport",
            "Planetary Port"
        ]

        try:
            collection = client[db_name][collection_name]

            # Service filter
            query = {
                "coords": {"$exists": True},
                "rareCommodities": "true",
                "type": {
                    "$in": ports
                },
            }

            pipeline = [
                {"$match": query},
                {
                    "$addFields": {
                        "distance": {
                            "$sqrt": {
                                "$add": [
                                    {"$pow": [{"$subtract": [player_coords[0], "$coords.x"]}, 2]},
                                    {"$pow": [{"$subtract": [player_coords[1], "$coords.y"]}, 2]},
                                    {"$pow": [{"$subtract": [player_coords[2], "$coords.z"]}, 2]}
                                ]
                            }
                        }
                    }
                },
                {"$sort": {"distance": 1}},
                {"$limit": limit},
                {
                    "$project": {
                        "_id": 0,
                        "name": 1,
                        "systemName": 1,
                        "type": 1,
                        "distanceToArrival": 1,
                        "distance": 1,
                        "allegiance": 1,
                        "government": 1,
                        "economy": 1,
                        "haveMarket": 1,
                        "haveShipyard": 1,
                        "haveOutfitting": 1,
                        "otherServices": 1,
                        "coords": 1
                    }
                }
            ]

            results = list(collection.aggregate(pipeline, allowDiskUse=True))

            return results

        except Exception as e:
            print(f"Error finding nearest Interstellar Factors station: {e}")
            return []
        finally:
            if client:
                client.close()
