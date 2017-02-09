# AlexaToPi
Home automation with an Amazon Echo and Raspberry Pi. Includes an AWS Lambda Skill that receives intents from an Alex Skills Kit (ASK) skill created using the `utterances.txt`, `device_states.txt`, and `interaction_model.txt`.

The launcher is a script for running the `control.py`, which runs on the raspberry pi and listens for device shadow updates in AWS IoT.
