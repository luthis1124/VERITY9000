import time
from pathlib import Path
from datetime import datetime
import json
from multiprocessing import Queue, Event

JOURNAL_PATH = '/media/ssd/SteamLibrary/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous'

class JournalMonitorV2Q:

    def __init__(self, to_ev: Queue, to_ev_initial: Queue, shutdown_event: Event, shared_state: dict):
        self.to_ev = to_ev
        self.to_ev_initial = to_ev_initial
        self.most_recent_log_file = ""
        self.first_run = True
        self.file_pos = 0
        self.poll_interval=1.0
        self.current_log_file = self.get_most_recent_log_file(JOURNAL_PATH)
        self.shutdown_event = shutdown_event
        self.shared = shared_state


    def run(self):
        while not self.shutdown_event.is_set():
            try:
                # print("first run? " + str(self.shared["first_run"]))
                if self.shared["first_run"]:
                    self.first_run_read()
                try:
                    with open(self.current_log_file, 'rb') as f:
                        f.seek(self.file_pos)
                        for line in f:
                            if not line:
                                break

                            line = line.strip()
                            if not line:
                                continue

                            try:
                                data = json.loads(line)
                                # self.eventhandler.handle_event(data)
                                self.to_ev.put(data)
                                # print("no event handler yet")
                                # print(data)
                            except json.JSONDecodeError:
                                if len(line) > 5:  # avoid warning on empty-ish lines
                                    print(f"[WARN] Malformed: {line[:120]}...")
                            except Exception as e:
                                print(f"[ERROR] {e}")

                            self.file_pos = f.tell()

                except Exception as e:
                    print(f"[Error] {e}")
                    time.sleep(1)

                if datetime.now().second % 10 == 0:
                    if self.current_log_file != self.get_most_recent_log_file(JOURNAL_PATH):
                        # self.first_run = True
                        # self.shared["first_run"] = True
                        self.current_log_file = self.get_most_recent_log_file(JOURNAL_PATH)

                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"jmon Error: {e}")

    def get_most_recent_log_file(self, directory: str=JOURNAL_PATH):

        log_files = list(Path(directory).glob("**/*.log"))

        if not log_files:
            print("No .log files found.")

        # Sort by modification time (newest first)
        return max(log_files, key=lambda f: f.stat().st_mtime)

    def first_run_read(self):
        self.file_pos = 0
        try:
            print("initial loading")
            with open(self.current_log_file, 'rb') as f:
                f.seek(self.file_pos)

                for line in f:
                    if not line:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                        # self.eventhandler.handle_event_initial(data)
                        # print("no event handler yet")
                        # print(data)
                        self.to_ev_initial.put(data)

                    except json.JSONDecodeError:
                        if len(line) > 5:  # avoid warning on empty-ish lines
                            print(f"[WARN] Malformed: {line[:120]}...")
                    except Exception as e:
                        print(f"[ERROR] {e}")

                    self.file_pos = f.tell()

        except Exception as e:
            print(f"[Error] {e}")
            time.sleep(1)

        print("initial loading done")

        # self.first_run = False


