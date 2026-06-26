from pymongo import MongoClient
from typing import Tuple, List, Optional
from bs4 import BeautifulSoup

class POIChecker:
    """
    Class to check if a system is in the POI list, and return any info.

    eg:
    type	"nebula"
    name	"The Clover Nebula"
    galMapSearch	"Dryooe Prou HH-C d267"
    coordinates	(3)[ -9875.8125, -333.375, 20760.25 ]
    descriptionHtml	'<p>A large, diffuse nebula some 1,200 light years from Jaques Station. Drawing a line from Jaques station through the nebula…ier.co.uk/showthread.php/116450-Information-The-Galactic-Mapping-Project-Expedition-Hub/page16"
        target="_blank">Link</a></p>'
    """

    # player_pos = (595.90625, -436.3125, -1211.21875)

    def get_nearest_poi(self, player_coords: Tuple[float, float, float],  # (x, y, z)
        limit: int = 5, current_system: str = "",):
        db_name = "mongotest"
        collection_name = "poi-1"
        client = MongoClient("mongodb://localhost:27017/")
        collection = client[db_name][collection_name]

        try:

            max_range = 10000  # ly

            query = {
                "coordinates.0": {
                    "$gte": player_coords[0] - max_range,
                    "$lte": player_coords[0] + max_range,
                },
                "coordinates.1": {
                    "$gte": player_coords[1] - max_range,
                    "$lte": player_coords[1] + max_range,
                },
                "coordinates.2": {
                    "$gte": player_coords[2] - max_range,
                    "$lte": player_coords[2] + max_range,
                },
                "name": {"$ne": current_system},
                "coordinates": {"$exists": True},
            }

            pipeline = [
                {"$match": query},
                {
                    "$addFields": {
                        "distSquared": {
                            "$reduce": {
                                "input": {"$map": {
                                    "input": {"$range": [0, 3]},
                                    "as": "i",
                                    "in": {
                                        "$pow": [
                                            {"$subtract": [
                                                {"$arrayElemAt": [player_coords, "$$i"]},
                                                {"$arrayElemAt": ["$coordinates", "$$i"]}
                                            ]},
                                            2
                                        ]
                                    }
                                }},
                                "initialValue": 0,
                                "in": {"$add": ["$$value", "$$this"]}
                            }
                        }
                    }
                },
                {
                    "$addFields": {
                        "distance": {"$sqrt": "$distSquared"}
                    }
                },
                {"$sort": {"distSquared": 1}},
                {"$limit": limit},

                {
                    "$project": {
                        "_id": 0,
                        "galMapSearch": 1,
                        "distance": {
                            "$convert": {
                                "input": "$distance",
                                "to": "int",
                                "onError": 0,
                                "onNull": 0
                            }
                        },
                        # "distance": {"$sqrt": "$distSquared"},
                    }
                }
            ]
            #
            # pipeline = [
            #     {"$match": query},
            #     {
            #         "$addFields": {
            #             "distance": {
            #                 "$sqrt": {
            #                     "$add": [
            #                         {"$pow": [{"$subtract": [player_coords[0], "$coordinates.0"]}, 2]},
            #                         {"$pow": [{"$subtract": [player_coords[1], "$coordinates.1"]}, 2]},
            #                         {"$pow": [{"$subtract": [player_coords[2], "$coordinates.2"]}, 2]}
            #                     ]
            #                 }
            #             }
            #         }
            #     },
            #     {"$sort": {"distance": 1}},
            #     {"$limit": limit},
            #     {
            #         "$project": {
            #             "_id": 0,
            #             # "name": 1,
            #             # "type": 1,
            #             "galMapSearch": 1
            #         }
            #     }
            # ]

            results = list(collection.aggregate(pipeline, allowDiskUse=True))

            return results

        except Exception as e:
            print(f"Error finding nearest poi: {e}")
            return []
        finally:
            if client:
                client.close()

    def check_system(self, current_system: str):

        if not current_system:
            return None

        db_name = "mongotest"
        collection_name = "poi-1"
        client = MongoClient("mongodb://localhost:27017/")

        try:
            collection = client[db_name][collection_name]

            query = {
                "galMapSearch": current_system  # Looks for exact match in array
            }

            pipeline = [
                {"$match": query},
                {
                    "$project": {
                        "_id": 0,
                        "name": 1,
                        "type": 1,
                        "galMapSearch": 1,
                        "coordinates": 1,
                        "descriptionHtml": 1
                    }
                }
            ]

            results = list(collection.aggregate(pipeline, allowDiskUse=True))

            if results:
                for poi in results:
                    soup = BeautifulSoup(poi["name"], "html.parser")
                    poi["name"] = soup.get_text(separator=" ", strip=True)
                    soup = BeautifulSoup(poi["descriptionHtml"], "html.parser")
                    poi["descriptionHtml"] = soup.get_text(separator=" ", strip=True)

            return results

        except Exception as e:
            print(f"Error getting system poi: {e}")
            return []
        finally:
            if client:
                client.close()