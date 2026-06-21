# VERITY9000
Linux based, voice controlled, local AI for Elite Dangerous

tl;dr: Core framework is ready, some basic functions exist (voice controls, AI functions, ship controls etc)

I gave up trying to get EDCopilot to work on Linux, so I decided to build my own solution that uses a local AI.

Remember Farscape? What if your ship was alive and autonomous?

Built as an exercise to learn how to build AI solutions that include:

- Local AI (Ollama)
- Monitoring log and config files
- Reacting to specific logs
- Accessing and updating a MongoDB
- API calls
- Speech to Text
- Text to Speech generation
- UI controls via key presses

I've gone through many optimisation / function steps to reach a point where it is now fast and modular enough to start building out the AI tools.

It is not too far off from parity with VoiceAttack, but still a significant way behind EDCopilot.

