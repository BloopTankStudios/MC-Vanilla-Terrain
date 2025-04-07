
import os
import json
import yaml

# Function to convert Vanilla terms to Terra
def noiseFunction(firstOctave, amplitude, index, size):
    frequency = 2**(firstOctave + index)
    amplitude = 1.04 * 2 * amplitude * 2**(size - index - 1) / (2**size - 1)
    return [frequency, amplitude]

# Find Files
noise_files = os.listdir('python-scripts/input/noise')
print(noise_files)

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

    # Sampler Combination
    for i in range(len(amplitudes)):
        perlinParams = noiseFunction(firstOctave, amplitudes[i], i, len(amplitudes))
        sampler["samplers"]["noise" + str(i)] = {"type": "PERLIN", "dimensions": dim}
        sampler["samplers"]["noise" + str(i)]["frequency"] = perlinParams[0]
        if dim == 2:
            sampler["expression"] += str(perlinParams[1]) + " * noise" + str(i) + "(x, z) + "
        else:
            sampler["expression"] += str(perlinParams[1]) + " * noise" + str(i) + "(x, y, z) + "
    
    # Expression Cleanup
    sampler["expression"] = sampler["expression"][:-3] + ")"

# Write data to new yaml file
with open('python-scripts/output/noise/vanilla.yml', 'w') as file:
    yaml.dump(data, file)