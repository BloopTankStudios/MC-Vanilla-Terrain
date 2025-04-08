
import os
import json
import yaml

# Function to convert Vanilla terms to Terra
def noiseFunction(firstOctave, amplitude, index, size):
    frequency = 2**(firstOctave + index)
    amplitude = 1.15 * amplitude * 2**(size - index - 1) / (2**size - 1)
    return [frequency, amplitude]

# Find Files
noise_files = os.listdir('python-scripts/input/noise')

# Output Data
data = {
    "samplers": {}
}

for noise_file in noise_files:
    # Open and read the JSON file
    with open('python-scripts/input/noise/' + noise_file, 'r') as file:
        input = json.load(file)

    # Extract Data
    firstOctave = input["firstOctave"]
    amplitudes = input["amplitudes"]

    dim = 2
    if noise_file.split(".")[0] == "offset":
        dim = 3

    # Use Expression
    data["samplers"][noise_file.split(".")[0]] = {"type": "EXPRESSION", "dimensions": dim}
    sampler = data["samplers"][noise_file.split(".")[0]]
    sampler["samplers"] = {}
    sampler["expression"] = "("

    # Determine Multiplier
    '''
    minA = 100
    maxA = -100
    for i in range(len(amplitudes)):
        if amplitudes[i] != 0:
            minA = min(minA, i)
            maxA = max(maxA, i)
    mult = 5 / (3 * (1 + 1 / (maxA - minA + 1)))
    '''
    mult = 1

    # Sampler Combination
    for i in range(len(amplitudes)):
        if amplitudes[i] > 0:
            perlinParams = noiseFunction(firstOctave, amplitudes[i], i, len(amplitudes))
            #sampler["samplers"]["noise" + str(i)] = {"type": "NORMAL", "mean": 0, "standard-deviation": .325, "dimensions": dim,
            #    "sampler": {"type": "PERLIN", "dimensions": dim}}
            sampler["samplers"]["noise" + str(i)] = {"type": "OPEN_SIMPLEX_2", "dimensions": dim}
            sampler["samplers"]["noise" + str(i)]["frequency"] = perlinParams[0]
            if dim == 2:
                sampler["expression"] += str(perlinParams[1] * mult) + " * noise" + str(i) + "(x, z) + "
            else:
                sampler["expression"] += str(perlinParams[1] * mult) + " * noise" + str(i) + "(x, y, z) + "
    
    # Expression Cleanup
    sampler["expression"] = sampler["expression"][:-3] + ")"

# Write data to new yaml file
with open('python-scripts/output/noise/vanilla.yml', 'w') as file:
    yaml.dump(data, file)