from SpeechToTextQ import SpeechToTextQ
from OllamaRunnerQ import OllamaRunnerQ
from VoiceCommandInterceptQ import VoiceCommandInterceptQ
from JournalMonitorV2Q import JournalMonitorV2Q
from GenerateTTSQ import GenerateTTSQ
from JournalEventHandlerQ import JournalEventHandlerQ
from StatusMonitor import StatusMonitor

import multiprocessing
import time
import sys
from multiprocessing import Process, Queue, Manager
from dataclasses import dataclass
from typing import Callable, List, Tuple, Any

@dataclass
class ProcessConfig:
    name: str
    target_class: type
    queue_args: Tuple

def process_runner(target_class: type, queue_args: Tuple[Any, ...]):
    instance = target_class(*queue_args)
    instance.run()


class Main:
    def __init__(self):

        self.manager = Manager()
        self.shared_state = self.manager.dict()
        # self.shared_state.update({
        #     "status": "running",
        #     "first_run": True,
        # })

        self.shared_state["first_run"] = True

        self.shutdown_event = multiprocessing.Event()

        self.queues = {
            "to_llm": Queue(),
            "to_vci": Queue(),
            "to_stt": Queue(),
            "to_tts": Queue(),
            "to_ev": Queue(),
            "to_ev_initial": Queue(),
        }

        self.process_configs: List[ProcessConfig] = [
            ProcessConfig(
                name="SpeechToTextQ",
                target_class=SpeechToTextQ,
                queue_args=(self.queues["to_vci"], self.shutdown_event)
            ),
            ProcessConfig(
                name="OllamaRunnerQ",
                target_class=OllamaRunnerQ,
                queue_args=(self.queues["to_llm"], self.queues["to_tts"], self.shutdown_event, self.shared_state)
            ),
            ProcessConfig(
                name="VoiceCommandInterceptQ",
                target_class=VoiceCommandInterceptQ,
                queue_args=(self.queues["to_vci"], self.queues["to_llm"], self.queues["to_tts"], self.shutdown_event, self.shared_state)
            ),
            ProcessConfig(
                name="JournalMonitorV2Q",
                target_class=JournalMonitorV2Q,
                queue_args=(self.queues["to_ev"], self.queues["to_ev_initial"], self.shutdown_event, self.shared_state)
            ),
            ProcessConfig(
                name="JournalEventHandlerQ",
                target_class=JournalEventHandlerQ,
                queue_args=(self.queues["to_ev"], self.queues["to_ev_initial"], self.queues["to_tts"], self.shutdown_event, self.shared_state)
            ),
            ProcessConfig(
                name="GenerateTTSQ",
                target_class=GenerateTTSQ,
                queue_args=(self.queues["to_tts"], self.shutdown_event)
            ),
            ProcessConfig(
                name="StatusMonitor",
                target_class=StatusMonitor,
                queue_args=(self.queues["to_llm"], self.shutdown_event, self.shared_state)
            ),
        ]

    def run(self):
        print(f"[Main] Starting in process PID: {multiprocessing.current_process().pid}")

        processes: List[Process] = []

        for config in self.process_configs:
            proc = Process(
                target=process_runner,  # Use top-level function
                # args=(config.target_class, config.queue_args, self.shared_state),
                args=(config.target_class, config.queue_args),
                name=config.name,
                daemon=False
            )
            proc.start()
            processes.append(proc)
            print(f"[Main] Started {config.name} (PID: {proc.pid})")

        print(f"\n[Main] All {len(processes)} processes started successfully.")

        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[Main] Stop signal received (PyCharm Stop button)")
        except Exception as e:
            print(f"[Main] Unexpected error: {e}")
        finally:
            self._shutdown(processes)

    def _shutdown(self, processes: List[Process]):
        self.shutdown_event.set()

        for proc in processes:
            proc.join(timeout=5)
            if proc.is_alive():
                print(f"[Main] Force terminating {proc.name}")
                proc.terminate()
                proc.join(timeout=2)

        self.manager.shutdown()  # Clean up manager
        print("[Main] All processes stopped. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)
    main = Main()
    main.run()
