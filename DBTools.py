from pymongo import MongoClient
from typing import Tuple, List, Optional


# TODO: use API to update DB when making calls

class DBTools:
    max_range = 200  # ly



    def find_nearest_neutron(self,
        player_coords: Tuple[float, float, float],  # (x, y, z)
        limit: int = 5, current_system = "",
    ) -> List[dict]:

        db_name = "mongotest"
        collection_name = "neutron_stars"
        client = MongoClient("mongodb://localhost:27017/")

        try:
            collection = client[db_name][collection_name]
            max_range = 1000  # ly

            query = {
                "coords.x": {
                    "$gte": player_coords[0] - max_range,
                    "$lte": player_coords[0] + max_range,
                },
                "coords.y": {
                    "$gte": player_coords[1] - max_range,
                    "$lte": player_coords[1] + max_range,
                },
                "coords.z": {
                    "$gte": player_coords[2] - max_range,
                    "$lte": player_coords[2] + max_range,
                },
                "name": {"$ne": current_system},
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
                        "id64": 1,
                        "name": 1,
                        "coords": 1
                    }
                }
            ]

            results = list(collection.aggregate(pipeline, allowDiskUse=True))

            return results

        except Exception as e:
            print(f"Error finding nearest neutron: {e}")
            return []
        finally:
            if client:
                client.close()

    def find_nearest(self,
        player_coords: Tuple[float, float, float],  # (x, y, z)
        limit: int = 5, service: str = "Refuel"
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

            max_range = 1000  # ly

            query = {
                "coords.x": {
                    "$gte": player_coords[0] - max_range,
                    "$lte": player_coords[0] + max_range,
                },
                "coords.y": {
                    "$gte": player_coords[1] - max_range,
                    "$lte": player_coords[1] + max_range,
                },
                "coords.z": {
                    "$gte": player_coords[2] - max_range,
                    "$lte": player_coords[2] + max_range,
                },
                "type": {
                    "$in": ports
                },
                "otherServices": service
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
        limit: int = 10, current_system = ""
    ) -> List[dict]:
        """
        Find the closest stations that stock rare commodities.
        Returns a list of stations sorted by distance (closest first).
        """

        db_name = "mongotest"
        collection_name = "stations"
        client = MongoClient("mongodb://localhost:27017/")
        collection = client[db_name][collection_name]

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

            max_range = 1000  # ly

            query = {
                "coords.x": {
                    "$gte": player_coords[0] - max_range,
                    "$lte": player_coords[0] + max_range,
                },
                "coords.y": {
                    "$gte": player_coords[1] - max_range,
                    "$lte": player_coords[1] + max_range,
                },
                "coords.z": {
                    "$gte": player_coords[2] - max_range,
                    "$lte": player_coords[2] + max_range,
                },
                "rareCommodities": "true",
                "type": {
                    "$in": ports
                },
                "systemName": {"$nin": [current_system]},
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
                        "distanceToArrival": {
                            "$convert": {
                                "input": "$distanceToArrival",
                                "to": "int",
                                "onError": 0,      # fallback value if conversion fails
                                "onNull": 0
                            }
                        },
                        "distance": {
                            "$convert": {
                                "input": "$distance",
                                "to": "int",
                                "onError": 0,
                                "onNull": 0
                            }
                        },
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
