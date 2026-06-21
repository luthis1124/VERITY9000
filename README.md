# VERITY9000
Linux based, voice controlled, local AI for Elite Dangerous

tl;dr: Core framework is ready, some basic functions exist (voice controls, AI functions, ship controls etc)

I gave up trying to get EDCopilot to work on Linux, so I decided to build my own solution that uses a local AI.

Remember Farscape? What if your ship was alive and autonomous?

This project is not meant to be a 1:1 copy of EDCopilot, rather, the goal is to increase immersion and make your ship a character you can interact with, that will grow and change over time.

Built as an exercise to learn how to build AI solutions that include:

- Local AI (Ollama)
- Monitoring log and config files
- Reacting to specific logs
- Accessing and updating a MongoDB
- API calls
- Speech to Text
- Text to Speech generation
- UI controls via key presses
- Retrieval Augmented Generation (RAG) for providing game context specific information

I've gone through *many* optimisation / function iterations to reach a point where the base structure is now fast and modular enough to start building out the AI tools.

It is not too far off from parity with VoiceAttack, but still a significant way behind EDCopilot.

CURRENT FUNCTIONALITY:

Voice controls for ship functions
Alerts when you enter a system with a point of interest
Providing next closest station when doing a Rare Commodities run

FUTURE PLANS:

Neutron star plotting
AI tool implementations for ship controls

EXAMPLES:

say: "Night vision" > night vision is activated
say: "Verity, when I say 'green googles' I want you to activate night vision"
say: "Where is the closest point of interest?"
say: "What is the point of interest in this system?"
say: "Give me a history of the Thargoids"
say: "Stop acting like an AI, add some enthusiasm and sarcasm to your personality"

FINAL NOTES:

This is not ready for deployment yet, not included in this repo is a properly indexed mongoDB with system information, POI locations, and a RAG db with the full context of the Elite Wiki that are not included here (pending license checks etc)
