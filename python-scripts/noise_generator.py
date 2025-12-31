# Creates the "Noise Generators" which are just advanced FBM noise
# https://misode.github.io/worldgen/noise/


# Should be using XoroshiroRandom for exact 1:1, instead will use Terra's Simplex_2 for now
# Base Function: https://github.com/misode/deepslate/blob/main/src/math/noise/NormalNoise.ts
# Using this Noise: https://github.com/misode/deepslate/blob/main/src/math/random/XoroshiroRandom.ts

# This is where the Noise Router is created w/ XoroshiroRandom
# https://github.com/misode/deepslate/blob/main/src/worldgen/SurfaceSystem.ts


import os
import json
import yaml

noise_3d = ["offset", "spaghetti_roughness_modulator", "spaghetti_roughness", "cave_entrance", "spaghetti_3d_1", "spaghetti_3d_2", "spaghetti_3d_rarity",
            "spaghetti_3d_thickness", "cave_layer", "cave_cheese", "pillar", "pillar_rareness", "pillar_thickness", "noodle", "noodle_thickness",
            "noodle_ridge_a", "noodle_ridge_b"]

# Function to convert Vanilla terms to Terra
def noiseFunction(firstOctave, amplitude, index, size):
    frequency = 2**(firstOctave + index) * .5
    amplitude = 1.15 * amplitude * 2**(size - index - 1) / (2**size - 1)
    return [frequency, amplitude]

def vanillaNoise(noise_files):
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
        if noise_file.split(".")[0] in noise_3d:
            dim = 3

        data["samplers"][noise_file.split(".")[0]] = {
            "type": "VANILLA_PERLIN_FBM",
            "dimensions": dim,
            "first-octave": firstOctave,
            "amplitudes": amplitudes,
            "salt": "minecraft:" + noise_file.split(".")[0]
            }

    # Write data to new yaml file
    with open('python-scripts/output/noise/vanilla.yml', 'w') as file:
        yaml.dump(data, file)

def terraNoise(noise_files):
    # Output Data
    data = {
        "samplers": {}
    }

    salt = 0

    for noise_file in noise_files:
        # Open and read the JSON file
        with open('python-scripts/input/noise/' + noise_file, 'r') as file:
            input = json.load(file)

        # Extract Data
        firstOctave = input["firstOctave"]
        amplitudes = input["amplitudes"]

        dim = 2
        if noise_file.split(".")[0] in noise_3d:
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
                # Add salt per Noise Function
                sampler["samplers"]["noise" + str(i)]["salt"] = salt
                salt += 3

                if dim == 2:
                    sampler["expression"] += str(perlinParams[1] * mult) + " * noise" + str(i) + "(x, z) + "
                else:
                    sampler["expression"] += str(perlinParams[1] * mult) + " * noise" + str(i) + "(x, y, z) + "

        
        # Expression Cleanup
        sampler["expression"] = sampler["expression"][:-3] + ")"

    # Write data to new yaml file
    with open('python-scripts/output/noise/terra.yml', 'w') as file:
        yaml.dump(data, file)


# Find Files
noise_files = os.listdir('python-scripts/input/noise')

terraNoise(noise_files)

vanillaNoise(noise_files)
