# reve_de_l-automate
Déployé dans le cadre du festival Recto VRso @LavaL 2025. Dispositif d'expérimentation de rêves collectivement construits.

## requierements

- `pip install flask flask-socketio python-osc gTTS`
- [ollama](https://ollama.com/)

## Ollama

For this project we only used the Modelfile to pre-prompt the model. Can find in `ollama/model/ModelFile`. All details [here](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)

The base model we used is gemma3.

## Machine setup

### MCU

Thanks to [SpotlightKid](https://github.com/SpotlightKid/micropython-osc)

We used a simple Raspberry Pico and [encoder from dfrobot](https://wiki.dfrobot.com/Incremental_Photoelectric_Rotary_Encoder_-_400P_R_SKU__SEN0230)

All details in `upython/encoder`

### Engineering

[PHOTO][3D]