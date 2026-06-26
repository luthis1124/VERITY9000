#
# def TTS_testing():
#     from GenerateTTS import GenerateTTS
#
#     # tts = "welcome home: commander."
#     # tts ="... Understood, Commander"
#     # tts ="... Copy that"
#     # tts ="... Affirmative"
#     # tts = "... Command received"
#     from PlayAudioFile import PlayAudioFile
#
#     ap = PlayAudioFile()
#     voice = GenerateTTS(ap)
#     # voice.list_sound_devices()
#     # voice.generate_and_play_tts(tts)
#     repeat = "repeat command"
#
#
#     no_record = "I don't have any records for that"
#     unable = "unable to locate service"
#     heat_alert = "Too hot!"
#     fuel_alert = "commander We are getting low on fuel"
#     major_fuel_alert = "Commander it is imperative we fuel up as soon as possible"
#     warning_message = "High Threat level reported"
#     poi_message = "Commander there is a point of interest in this system"
#     multiple_poi_message = "There are multiple points of interest in this system"
#
#     voice.generate_tts_audio(multiple_poi_message)

def status_testing():
    from multiprocessing import Process, Queue, Manager

    from StatusMonitor import Statest
    manager = Manager()
    shared_state = manager.dict()

    status = Statest(shared_state)
    status.test_update()
    status.test_flags()

def input_testing():
    from InputControls import InputControls

    action = InputControls()
    # Test some common controls
    test_controls = ["YawLeftButton", "YawRightButton", "PitchUpButton",
                     "PitchDownButton", "ThrottleForward", "FirePrimaryButton"]

    # action.print_controls(test_controls)

    action.print_active_keys()
    # print(action.list_active_primary_keys())
    # action.print_controls()
    # time.sleep(2)
    # action.request_docking()
    # action.do_action('DeployHeatSink')
    # action.do_action('UseBoostJuice')
    # time.sleep(2)
    # action.do_action('SetSpeed100')
    # time.sleep(2)
    # action.do_action('SetSpeedZero')
    # time.sleep(2)
    # action.do_action('SystemMapOpen')
    # time.sleep(2)
    # action.do_action('SystemMapOpen')

    # action.do_action('GalaxyMapOpen')
    # time.sleep(2)
    # action.do_action('GalaxyMapOpen')
    # time.sleep(2)
    #
    # action.do_action('ExplorationFSSEnter')
    # time.sleep(2)
    # action.do_action('ExplorationFSSEnter')
    # time.sleep(2)
    #
    #
    # action.do_action('DeployHardpointToggle')
    # time.sleep(2)
    #
    # action.do_action('ToggleCargoScoop')
    # time.sleep(2)
    #
    # action.do_action('Supercruise')
    # action.list_actions()

#
# def test_ollama():
#     from ShipAltitudeAndLocation import ShipAltitudeAndLocation
#     from OllamaRunnerST import OllamaRunnerST
#
#     ship = ShipAltitudeAndLocation()
#     llm = OllamaRunnerST(ship)
#
#     # llm.call_llm_chat("can you tell me anything about frame shift drives")
#     llm.call_llm_chat("shall we take a look down on the surface?")
#     # action = InputControls()
#     # action.print_active_primary_keys()
#     # llm.call_llm("given the list of keys here, what would you press for a heatsink" + action.print_active_primary_keys())
#     # llm.call_llm("deploy a heatsink")
#     # llm.call_llm("boost it!")
#     # llm.call_llm("list dangerous systems")
#     # llm.call_llm("deploy a heatsink")
#     # llm.call_llm("plot a course to duamta")
#     # llm.call_llm("where can I buy a cargo module?")
#     # llm.call_llm("is there anything worth seeing here?")
#     # llm.call_llm("alright, take us up.")
#     # llm.call_llm("punch it!")
#     # llm.call_llm("what were the last few things I asked?")
#     # llm.call_llm("engage FSD")
#     # llm.call_llm("a little to the left")
#     # llm.call_llm("how many limpets do I have?")
#
#     # llm.call_llm("list tools available and the function")
#
#     # llm.call_llm("what is this system name?")

def api_testing():
    from EDSM_API import EDSM_API

    api = EDSM_API()
    # api.print_controlling_allegiance(api.get_system_factions_safe("Synuefe EM-M c23-8"))
    # print("")
    # api.print_controlling_faction_info(api.get_system_factions_safe("Coalsack Sector DR-V b2-3"))
    api.get_edsm_system("Belalans")

    rare_commodities = [
        {"commodity": "Duradrives", "station": "Cowper Dock", "system": "Anima"},
        {"commodity": "Leathery Eggs", "station": "Ridley Scott", "system": "Zaonce"},
        {"commodity": "Lucan Onionhead", "station": "Cassie-L-Peia", "system": "Tanmark"},
        {"commodity": "Soontill Relics", "station": "Cheranovsky City", "system": "Ngurii"},
        {"commodity": "Sothis Crystalline Gold", "station": "Newholm Station", "system": "Sothis"},
        {"commodity": "Crystalline Spheres", "station": "Snow Moon", "system": "Bento"},
        {"commodity": "HIP 118311 Swarm", "station": "Lubbock Market", "system": "HIP 118311"},
        {"commodity": "The Waters Of Shintara", "station": "Jameson Memorial", "system": "Shinrarta Dezhra"},
        {"commodity": "Terra Mater Blood Bores", "station": "GR8Minds", "system": "Terra Mater"},
        {"commodity": "Personal Gifts", "station": "Frost Dock", "system": "Njambalba"},
        {"commodity": "Jaradharre Puzzle Box", "station": "Gohar Station", "system": "Jaradharre"},
        {"commodity": "Ngadandari Fire Opals", "station": "Napier Terminal", "system": "Ngadandari"},
        {"commodity": "Jaques Quinentian Still", "station": "Jaques Station", "system": "Colonia"},
        {"commodity": "Kamitra Cigars", "station": "Hammel Terminal", "system": "Kamitra"},
        {"commodity": "Platinum Alloy", "station": "Artzybasheff Terminal", "system": "Nahuatl"},
        {"commodity": "AZ Cancri Formula 42", "station": "Fisher Station", "system": "AZ Cancri"},
        {"commodity": "Giant Verrix", "station": "Greeboski's Outpost", "system": "Phiagre"},
        {"commodity": "Chameleon Cloth", "station": "Smith Reserve", "system": "LDS 883"},
        {"commodity": "Mokojing Beast Feast", "station": "Noli Terminal", "system": "Mokojing"},
        {"commodity": "Momus Bog Spaniel", "station": "Tartarus Point", "system": "Momus Reach"},
        {"commodity": "Lavian Brandy", "station": "Lave Station", "system": "Lave"},
        {"commodity": "Burnham Bile Distillate", "station": "Burnham Beacon", "system": "HIP 59533"},
        {"commodity": "Borasetani Pathogenetics", "station": "Katzenstein Terminal", "system": "Borasetani"},
        {"commodity": "Azure Milk", "station": "George Lucas", "system": "Leesti"},
        {"commodity": "Delta Phoenicis Palms", "station": "Trading Post", "system": "Delta Phoenicis"},
        {"commodity": "Cherbones Blood Crystals", "station": "Chalker Landing", "system": "Cherbones"},
        {"commodity": "Anduliga Fire Works", "station": "Celsius Estate", "system": "Anduliga"},
        {"commodity": "Banki Amphibious Leather", "station": "Antonio de Andrade Vista", "system": "Banki"},
        {"commodity": "Classified Experimental Equipment", "station": "Heart of Taurus", "system": "HIP 22460"},
        {"commodity": "Volkhab Bee Drones", "station": "Vernadsky Dock", "system": "Volkhab"},
        {"commodity": "Toxandji Virocide", "station": "Tsunenaga Orbital", "system": "Toxandji"},
        {"commodity": "Any Na Coffee", "station": "Libby Orbital", "system": "Any Na"},
        {"commodity": "Holva Duelling Blades", "station": "Kreutz Orbital", "system": "Holva"},
        {"commodity": "Neritus Berries", "station": "Toll Ring", "system": "Neritus"},
        {"commodity": "Albino Quechua Mammoth Meat", "station": "Crown Ring", "system": "Quechua"},
        {"commodity": "Rusani Old Smokey", "station": "Fernandes Market", "system": "Rusani"},
        {"commodity": "Baltah'sine Vacuum Krill", "station": "Baltha'Sine Station", "system": "Baltah'Sine"},
        {"commodity": "Wolf Fesh", "station": "Saunders's Dive", "system": "Wolf 1301"},
        {"commodity": "HIP 10175 Bush Meat", "station": "Stefanyshyn-Piper Station", "system": "HIP 10175"},
        {"commodity": "Saxon Wine", "station": "Hunt Enterprise", "system": "9 Aurigae"},
        {"commodity": "Wulpa Hyperbore Systems", "station": "Williams Gateway", "system": "Wulpa"},
        {"commodity": "Yaso Kondi Leaf", "station": "Wheeler Market", "system": "Yaso Kondi"},
        {"commodity": "Honesty Pills", "station": "King Gateway", "system": "LP 375-25"},
        {"commodity": "Thrutis Cream", "station": "Kingsbury Dock", "system": "Thrutis"},
        {"commodity": "Crom Silver Fesh", "station": "Chorel Survey", "system": "Crom"},
        {"commodity": "Onionhead Alpha Strain", "station": "Navigator Market", "system": "Xelabara"},
        {"commodity": "Uzumoku Low-G Wings", "station": "Sverdrup Ring", "system": "Uzumoku"},
        {"commodity": "Damna Carapaces", "station": "Nemere Market", "system": "Damna"},
        {"commodity": "Tanmark Tranquil Tea", "station": "Cassie-L-Peia", "system": "Tanmark"},
        {"commodity": "Chateau De Aegaeon", "station": "Schweickart Station", "system": "Aegaeon"},
        {"commodity": "Chi Eridani Marine Paste", "station": "Steve Masters", "system": "Chi Eridani"},
        {"commodity": "Eden Apples Of Aerial", "station": "Andrade Legacy", "system": "Aerial"},
        {"commodity": "Deuringas Truffles", "station": "Shukor Hub", "system": "Deuringas"},
        {"commodity": "HIP Proto-Squid", "station": "Andersson Station", "system": "HIP 41181"},
        {"commodity": "Gerasian Gueuze Beer", "station": "Yurchikhin Port", "system": "Geras"},
        {"commodity": "Wheemete Wheat Cakes", "station": "Eisinga Enterprise", "system": "Wheemete"},
        {"commodity": "Koro Kung Pellets", "station": "Lonchakov Orbital", "system": "Korro Kung"},
        {"commodity": "Eshu Umbrellas", "station": "Shajn Terminal", "system": "Eshu"},
        {"commodity": "Goman Yaupon Coffee", "station": "Gustav Sporer Port", "system": "Goman"},
        {"commodity": "Tauri Chimes", "station": "Porta", "system": "39 Tauri"},
        {"commodity": "CD-75 Kitten Brand Coffee", "station": "Kirk Dock", "system": "CD-75 661"},
        {"commodity": "Ethgreze Tea Buds", "station": "Bloch Station", "system": "Ethgreze"},
        {"commodity": "Haiden Black Brew", "station": "Searfoss Enterprise", "system": "Haiden"},
        {"commodity": "Aepyornis Egg", "station": "Glushko Station", "system": "47 Ceti"},
        {"commodity": "Fujin Tea", "station": "Futen Spaceport", "system": "Fujin"},
        {"commodity": "Witchhaul Kobe Beef", "station": "Hornby Terminal", "system": "Witchhaul"},
        {"commodity": "Ceti Rabbits", "station": "Kaufmanis Hub", "system": "47 Ceti"},
        {"commodity": "Belalans Ray Leather", "station": "Boscovich Ring", "system": "Belalans"},
        {"commodity": "Geawen Dance Dust", "station": "Obruchev Legacy", "system": "Geawen"},
        {"commodity": "Tarach Spice", "station": "Tranquillity", "system": "Tarach Tor"},
        {"commodity": "Alacarakmo Skin Art", "station": "Weyl Gateway", "system": "Alacarakmo"},
        {"commodity": "Giant Irukama Snails", "station": "Blaauw City", "system": "Irukama"},
        {"commodity": "Helvetitj Pearls", "station": "Friend Orbital", "system": "Helvetitj"},
        {"commodity": "Mechucos High Tea", "station": "Brandenstein Port", "system": "Mechucos"},
        {"commodity": "Jotun Mookah", "station": "Icelock", "system": "Jotun"},
        {"commodity": "Bast Snake Gin", "station": "Hart Station", "system": "Bast"},
        {"commodity": "Arouca Conventual Sweets", "station": "Shipton Orbital", "system": "Arouca"},
        {"commodity": "Utgaroar Millennial Eggs", "station": "Fort Klarix", "system": "Utgaroar"},
        {"commodity": "Tiegfries Synth Silk", "station": "Larbalestier Dock", "system": "Tiegfries"},
        {"commodity": "Zeessze Ant Grub Glue", "station": "Nicollier Hangar", "system": "Zeessze"},
        {"commodity": "Wuthielo Ku Froth", "station": "Tarter Dock", "system": "Wuthielo Ku"},
        {"commodity": "Karsuki Locusts", "station": "West Market", "system": "Karsuki Ti"},
        {"commodity": "Buckyball Beer Mats", "station": "Rebuy Prospect", "system": "Fullerene C60"},
        {"commodity": "Pantaa Prayer Sticks", "station": "Zamka Platform", "system": "George Pantazis"},
        {"commodity": "Rapa Bao Snake Skins", "station": "Flagg Gateway", "system": "Rapa Bao"},
        {"commodity": "Sanuma Decorative Meat", "station": "Dunyach Gateway", "system": "Sanuma"},
        {"commodity": "Onionhead", "station": "Harvestport", "system": "Kappa Fornacis"},
        {"commodity": "Shan's Charis Orchid", "station": "Baird Gateway", "system": "Arque"},
        {"commodity": "Njangari Saddles", "station": "Lee Hub", "system": "Njangari"},
        {"commodity": "Hip Organophosphates", "station": "Stasheff Colony", "system": "HIP 80364"},
        {"commodity": "Motrona Experience Jelly", "station": "Pinzon Dock", "system": "Dea Motrona"},
        {"commodity": "Orrerian Vicious Brew", "station": "Sharon Lee Free Market", "system": "Orrere"},
        {"commodity": "Jaroua Rice", "station": "McCool City", "system": "Jaroua"},
        {"commodity": "Centauri Mega Gin", "station": "Hutton Orbital", "system": "Alpha Centauri"},
        {"commodity": "Baked Greebles", "station": "Bamford Ring", "system": "38 Virginis"},
        {"commodity": "Leestian Evil Juice", "station": "George Lucas", "system": "Leesti"},
        {"commodity": "Live Hecate Sea Worms", "station": "RJH1972", "system": "Hecate"},
        {"commodity": "Rajukru Multi-Stoves", "station": "Snyder Terminal", "system": "Rajukru"},
        {"commodity": "Kongga Ale", "station": "Laplace Ring", "system": "Kongga"},
        {"commodity": "Pavonis Ear Grubs", "station": "Hooper Relay", "system": "Delta Pavonis"},
        {"commodity": "Indi Bourbon", "station": "Mansfield Orbiter", "system": "Epsilon Indi"},
        {"commodity": "Diso Ma Corn", "station": "Shifnalport", "system": "Diso"},
        {"commodity": "HR 7221 Wheat", "station": "Veron City", "system": "HR 7221"},
        {"commodity": "Tiolce Waste2Paste Units", "station": "Gordon Terminal", "system": "Tiolce"},
        {"commodity": "Aganippe Rush", "station": "Julian Market", "system": "Aganippe"},
        {"commodity": "Esuseku Caviar", "station": "Savinykh Orbital", "system": "Esuseku"},
        {"commodity": "Coquim Spongiform Victuals", "station": "Hirayama Installation", "system": "Coquim"},
        {"commodity": "Eranin Pearl Whisky", "station": "Azeban City", "system": "Eranin"},
        {"commodity": "Medb Starlube", "station": "Vela Dock", "system": "Medb"},
        {"commodity": "The Hutton Mug", "station": "Hutton Orbital", "system": "Alpha Centauri"},
        {"commodity": "Vidavantian Lace", "station": "Lee Mines", "system": "Vidavanta"},
        {"commodity": "Uszaian Tree Grub", "station": "Guest Installation", "system": "Uszaa"},
        {"commodity": "V Herculis Body Rub", "station": "Kaku Plant", "system": "V1090 Herculis"},
        {"commodity": "Nguna Modern Antiques", "station": "Biggle Hub", "system": "Nguna"},
        {"commodity": "Mulachi Giant Fungus", "station": "Clark Terminal", "system": "Mulachi"},
        {"commodity": "Nanomedicines", "station": "Elion Dock", "system": "Kuma"},
        {"commodity": "Ophiuch Exino Artefacts", "station": "Katzenstein Dock", "system": "36 Ophiuchi"},
        {"commodity": "Havasupai Dream Catcher", "station": "Lovelace Port", "system": "Havasupai"},
        {"commodity": "Altairian Skin", "station": "Solo Orbiter", "system": "Altair"},
        {"commodity": "Vega Slimweed", "station": "Taylor City", "system": "Vega"},
        {"commodity": "LTT Hyper Sweet", "station": "Smeaton Orbital", "system": "LTT 9360"},
        {"commodity": "Ceremonial Heike Tea", "station": "Brunel City", "system": "Heike"},
        {"commodity": "Non Euclidian Exotanks", "station": "Euclid Terminal", "system": "LTT 8517"},
        {"commodity": "Ochoeng Chillies", "station": "Roddenberry Gateway", "system": "Ochoeng"},
        {"commodity": "Void Extract Coffee", "station": "Ehrlich Orbital", "system": "LFT 1421"},
        {"commodity": "Galactic Travel Guide", "station": "Bluford Orbital", "system": "LHS 3447"},
        {"commodity": "Gilya Signature Weapons", "station": "Bell Orbital", "system": "Gilya"},
        {"commodity": "Lyrae Weed", "station": "Budrys Ring", "system": "16 Lyrae"},
        {"commodity": "Eleu Thermals", "station": "Finney Dock", "system": "Eleu"},
        {"commodity": "Onionhead Beta Strain", "station": "la Cosa City", "system": "HIP 112974"},
        {"commodity": "Master Chefs", "station": "Pataarcy Corporate", "system": "Viracocha"},
        {"commodity": "Xihe Biomorphic Companions", "station": "Zhen Dock", "system": "Xihe"},
        {"commodity": "Harma Silver Sea Rum", "station": "Gabriel Enterprise", "system": "Harma"},
        {"commodity": "Karetii Couture", "station": "Sinclair Platform", "system": "Karetii"},
        {"commodity": "Kachirigin Filter Leeches", "station": "Nowak Orbital", "system": "Kachirigin"},
        {"commodity": "Alya Body Soap", "station": "Malaspina Gateway", "system": "Alya"},
        {"commodity": "Mukusubii Chitin-os", "station": "Ledyard Dock", "system": "Mukusubii"},
        {"commodity": "Kamorin Historic Weapons", "station": "Godwin Vision", "system": "Kamorin"},
        {"commodity": "Kinago Violins", "station": "Fozard Ring", "system": "Kinago"},
        {"commodity": "Apa Vietii Forester's Choice", "station": "Upaniklis", "system": "Upaniklis"},
        {"commodity": "Ultra-Compact Processor Prototypes", "station": "Langford Enterprise",
         "system": "17 Lyrae"},
        {"commodity": "Vanayequi Ceratomorpha Fur", "station": "Clauss Hub", "system": "Vanayequi"}
    ]

    # for item in rare_commodities:
    #     api.get_edsm_system(item["system"])


def test_play_audio():
    from PlayAudioFile import PlayAudioFile

    ap = PlayAudioFile()
    ap.affirmative()
    ap.affirmative()
    ap.affirmative()
    ap.affirmative()

# def journal():
#     from ShipAltitudeAndLocation import ShipAltitudeAndLocation
#     from JournalEventHandler import JournalEventHandler
#
#     ship = ShipAltitudeAndLocation()
#     jevent = JournalEventHandler(ship)
#     jevent.parse_one_json_line()

def print_text(text: str):
    print(text)

# def journalv2():
#     from JournalMonitorV2 import JournalMonitorV2
#     from ShipAltitudeAndLocation import ShipAltitudeAndLocation
#     ship = ShipAltitudeAndLocation()
#
#     import time
#
#     monitor = JournalMonitorV2(ship)
#
#     monitor.start()
#
#     try:
#         while True:
#             time.sleep(5)
#     except KeyboardInterrupt:
#         print("\nStopping Journal Monitor...")
#         monitor.stop()
#
# def stt_test(text):
#     from SpeechToText import SpeechToText
#     stt = SpeechToText(text)
#     stt.list_sound_devices()

def poi_test():
    from POIChecker import POIChecker
    poi = POIChecker()

    player_pos = (595.90625, -436.3125, -1211.21875)
    near = poi.get_nearest_poi(player_coords=player_pos)
    for poi in near:
        print(poi["galMapSearch"])
    print(near)

    #
    # poi_result = poi.check_system("CD-23 13397")
    # if poi_result:
    #     for poi in poi_result:
    #         print(poi["type"])
    #         # from bs4 import BeautifulSoup
    #         # soup = BeautifulSoup(poi["descriptionHtml"], "html.parser")
    #         # text = soup.get_text(separator=" ", strip=True)
    #         print(poi["descriptionHtml"])

def find_nearest_rares():
    from DBTools import DBTools
    db = DBTools()
    player_pos = (595.90625, -436.3125, -1211.21875)
    stations = db.find_nearest_rares(player_coords=player_pos, limit=1, current_system="Sol")
    print(stations)


def find_nearest_neutron():
    from DBTools import DBTools
    db = DBTools()
    player_pos = (595.90625, -436.3125, -1211.21875)
    neutrons = db.find_nearest_neutron(player_coords=player_pos, limit=1, current_system="Iwainch FG-Y g2")
    print(neutrons)
    print(neutrons[0]["name"])


def text_fix():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup("Erikson&#39;s Star", "html.parser")

    print(soup.get_text(separator=" ", strip=True))

    soup = BeautifulSoup("The Ammonia Lyceum", "html.parser")
    print(soup.get_text(separator=" ", strip=True))

def list_sound_devices():
    import sounddevice as sd

    print("🎤 Available Audio Devices:\n")
    print(sd.query_devices())

    # Also print just input devices (microphones)
    print("\n" + "=" * 50)
    print("INPUT DEVICES (Microphones):")
    for i, device in enumerate(sd.query_devices()):
        if device['max_input_channels'] > 0:
            print(f"{i:2d} | {device['name']}")

    print("\n" + "=" * 50)
    print("OUTPUT DEVICES (Speakers):")
    for i, device in enumerate(sd.query_devices()):
        if device['max_output_channels'] > 0:
            print(f"{i:2d} | {device['name']}")

if __name__ == "__main__":
    # player_pos = (595.90625, -436.3125, -1211.21875)

    # input_testing()
    # test_ollama()

    # ed = EDSM_API()
    # result = ed.get_edsm_system("Dironii")
    # TTS_testing()
    # status_testing()

    # print(sd.query_devices(6))

    # test_play_audio()
    # api_testing()
    # journalv2()

    # poi_test()
    # text_fix()
    # find_nearest_rares()
    list_sound_devices()
    # status_testing()
    # find_nearest_neutron()