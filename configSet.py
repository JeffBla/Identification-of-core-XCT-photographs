import json
with open('config.json', 'w') as f:
    json.dump(dict(BrightnessThrehold=50), f)
