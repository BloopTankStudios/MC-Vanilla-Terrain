# Picks apart the spline from Density Functions into a hopefully efficient mathematical Terra equivalent
# https://misode.github.io/worldgen/density-function/

import os
import yaml

spline_import = {
    "spline": "$math/functions/spline.yml:functions.spline",
    "spline_left_end": "$math/functions/spline.yml:functions.spline_left_end",
    "spline_right_end": "$math/functions/spline.yml:functions.spline_right_end",
    "spline0": "$math/functions/spline.yml:functions.spline0"
}

def read_spline(spline):
    all_samplers = {spline["coordinate"].split("/")[1]}
    sampler = spline["coordinate"].split("/")[1] + "_f"
    points = spline["points"]

    sub_splines = []

    # Trail Start
    expression = "if(" + sampler + " < " + str(points[0]["location"]) + ",\n"
    if points[0]["derivative"] == 0:
        expression += read_point(points[0]["value"], sub_splines) + ",\n"
    else:
        expression += "spline_left_end(" + sampler + ", " + str(points[0]["location"]) + ", " + \
            str(points[0]["derivative"]) + ", " + read_point(points[0]["value"], sub_splines) + "),\n"

    # Points
    for p in range(len(points) - 1):
        expression += "if(" + sampler + " < " + str(points[p+1]["location"]) + ",\n"
        if points[p]["derivative"] == 0 and points[p+1]["derivative"] == 0:
            expression += "spline0(" + sampler + ", " + str(points[p]["location"]) + ", " + \
                read_point(points[p]["value"], sub_splines) + ", " + str(points[p+1]["location"]) + ", " + \
                read_point(points[p+1]["value"], sub_splines) + "),\n"
        else:
            expression += "spline(" + sampler + ", " + str(points[p]["location"]) + ", " + \
                str(points[p]["derivative"]) + ", " + read_point(points[p]["value"], sub_splines) + ", " + \
                str(points[p+1]["location"]) + ", " + str(points[p+1]["derivative"]) + ", " + \
                read_point(points[p+1]["value"], sub_splines) + "),\n"

    # Trail End
    if points[-1]["derivative"] == 0:
        expression += read_point(points[-1]["value"], sub_splines)
    else:
        expression += "spline_right_end(" + sampler + ", " + str(points[-1]["location"]) + ", " + \
            str(points[-1]["derivative"]) + ", " + read_point(points[-1]["value"], sub_splines) + ")"
    
    for p in range(len(points)):
        expression += ")"
    
    # Store Data
    sampler = sampler[:-6]

    data = {
        "expression": expression,
        "functions": {}
    }
    #if len(sub_splines) > 0:
    #    data["functions"] = {}

    # Handles Sub Splines
    for i in range(len(sub_splines)):
        [data["functions"]["spline_" + str(i)], sub_samplers] = read_spline(sub_splines[i])
        all_samplers.update(sub_samplers)
    
    return [data, all_samplers]

def read_point(value, sub_splines):
    # Just a Number
    if type(value) == float or type(value) == int:
        return str(value)
    else:
        # Add to Sub Splines
        if value not in sub_splines:
            sub_splines.append(value)
        return "spline_" + str(sub_splines.index(value)) + "({SAMPLERS_F})"

def add_arguments(data, samplers, samplersStr):
    data["arguments"] = samplers
    data["expression"] = data["expression"].replace("{SAMPLERS_F}", samplersStr)
    if "functions" in data:
        for sub_data in data["functions"]:
            #if sub_data not in ["spline", "spline_left_end", "spline_right_end", "spline0"]:
                data["functions"][sub_data] = add_arguments(data["functions"][sub_data], samplers, samplersStr)
    data["functions"] |= spline_import
    return data


# Make sure new lines are handled properly
def multiline_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, multiline_representer)

# Start the Process
density_files = os.listdir('python-scripts/input/density')

for density_file in density_files:
    with open('python-scripts/input/density/' + density_file, 'r') as file:
        input = yaml.safe_load(file)
    
    data = {
        "sampler": {
            "dimensions": 2,
            "type": "EXPRESSION",
            "functions": {
                "spline_func": {
                }
            }
        }
    }

    [data["sampler"]["functions"]["spline_func"], all_samplers] = read_spline(input["spline"])
    all_samplers = list(all_samplers)

    # Add samplers to Functions
    samplerStr = "spline_func("
    samplerSubStr = ""
    for i in range(len(all_samplers)):
        samplerStr += all_samplers[i] + "(x, z), "
        all_samplers[i] += "_f"
        samplerSubStr += all_samplers[i] + ", "
    data["sampler"]["expression"] = samplerStr[:-2] + ")"
    data["sampler"]["functions"]["spline_func"] = add_arguments(data["sampler"]["functions"]["spline_func"], all_samplers, samplerSubStr[:-2])

    with open('python-scripts/output/density/' + density_file, 'w') as file:
        yaml.dump(data, file)
