# Does pre-math for noise generator so not doing too much multiplication/handling big numbers

# Should be using "Legacy Random" for exact 1:1, instead will use Terra's Simplex_2 for now
# Based on Blended Noise: https://github.com/misode/deepslate/blob/main/src/math/noise/BlendedNoise.ts
# Using Legacy Random: https://github.com/misode/deepslate/blob/main/src/math/random/LegacyRandom.ts

import os
import yaml

# Default Vanilla resolution is 8, but that can be resource intensive
resolution = 4

xzScale = 0.25
yScale = 0.125
xzFactor = 80
yFactor = 160
smearScaleMultiplier = 8

# Make sure new lines are handled properly
def multiline_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, multiline_representer)

noise_files = os.listdir('python-scripts/input/noise-old')

for noise_file in noise_files:
    # Open and read the JSON file
    with open('python-scripts/input/noise-old/' + noise_file, 'r') as file:
        data = yaml.safe_load(file)
    
    variables = data["sampler"]["samplers"]["mainNoise"]["variables"]

    variables["scaledXZ"] = 684.412 * xzScale
    variables["scaledY"] = 684.412 * yScale
    variables["factoredXZ"] = variables["scaledXZ"] / xzFactor
    variables["factoredY"] = variables["scaledY"] / yFactor
    variables["scaledSmear"] = smearScaleMultiplier * variables["scaledY"]
    variables["factoredSmear"] = variables["scaledSmear"] / yFactor

    data["sampler"]["functions"]["sampling"]["functions"]["clampLerp"]["expression"] = \
        data["sampler"]["functions"]["sampling"]["functions"]["clampLerp"]["expression"].replace("lerpMax", str(1/128))

    data["sampler"]["samplers"]["mainNoise"]["samplers"]["noise"]["octaves"] = resolution
    data["sampler"]["samplers"]["mainNoise"]["samplers"]["noise"]["sampler"]["frequency"] = 1 / 2**(8-resolution) * .5

    data["sampler"]["samplers"]["minNoise"]["samplers"]["noise"]["octaves"] = resolution*2
    data["sampler"]["samplers"]["minNoise"]["samplers"]["noise"]["sampler"]["frequency"] = 1 / 2**(16-2*resolution) * .5

    data["sampler"]["samplers"]["maxNoise"]["samplers"]["noise"]["octaves"] = resolution*2
    data["sampler"]["samplers"]["maxNoise"]["samplers"]["noise"]["sampler"]["frequency"] = 1 / 2**(16-2*resolution) * .5

    with open('python-scripts/output/noise-old/' + noise_file, 'w') as file:
        yaml.dump(data, file)