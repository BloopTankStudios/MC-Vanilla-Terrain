
import os
import yaml

def read_spline(spline):
    sampler = spline["coordinate"].split("/")[1] + "(x, z)"
    points = spline["points"]

    sub_splines = []

    # Trail Start
    if True or points[0]["derivative"] == 0:
        expression = "if(" + sampler + " < " + str(points[0]["location"]) + ", " + \
            read_point(points[0]["value"], sub_splines) + ", 0) +\n"
    else:
        expression = "spline_left_end(" + sampler + ", " + str(points[0]["location"]) + ", " + \
            str(points[0]["derivative"]) + ", " + read_point(points[0]["value"], sub_splines) + ") +\n"

    # Points
    for p in range(len(points) - 1):
        if True:
            expression += "lerp(" + sampler + ", " + str(points[p]["location"]) + ", " + \
                read_point(points[p]["value"], sub_splines) + ", " + str(points[p+1]["location"]) + ", " + \
                read_point(points[p+1]["value"], sub_splines) + ") +\n"
        elif points[p]["derivative"] == 0 and points[p+1]["derivative"] == 0:
            expression += "spline0(" + sampler + ", " + str(points[p]["location"]) + ", " + \
                read_point(points[p]["value"], sub_splines) + ", " + str(points[p+1]["location"]) + ", " + \
                read_point(points[p+1]["value"], sub_splines) + ") +\n"
        else:
            expression += "spline(" + sampler + ", " + str(points[p]["location"]) + ", " + \
                str(points[p]["derivative"]) + ", " + read_point(points[p]["value"], sub_splines) + ", " + \
                str(points[p+1]["location"]) + ", " + str(points[p+1]["derivative"]) + ", " + \
                read_point(points[p+1]["value"], sub_splines) + ") +\n"

    # Trail End
    if True or points[0]["derivative"] == 0:
        expression += "if(" + sampler + " >= " + str(points[-1]["location"]) + ", " + \
            read_point(points[-1]["value"], sub_splines) + ", 0)"
    else:
        expression += "spline_right_end(" + sampler + ", " + str(points[-1]["location"]) + ", " + \
            str(points[-1]["derivative"]) + ", " + read_point(points[-1]["value"], sub_splines) + ")"
    
    # Store Data
    data = {
        "dimensions": 2,
        "type": "EXPRESSION"
    }
    sampler = sampler[:-6]

    data["expression"] = expression
    #data["samplers"][sampler] = "$biomes/vanilla/abstract/terrain/density-functions/" + sampler + ".yml:sampler"
    if len(sub_splines) > 0:
        data["samplers"] = {}

    # Handles Sub Splines
    for i in range(len(sub_splines)):
        data["samplers"]["spline_" + str(i)] = read_spline(sub_splines[i])

    return data

def read_point(value, sub_splines):
    # Just a Number
    if type(value) == float or type(value) == int:
        return str(value)
    else:
        # Add to Sub Splines
        if value not in sub_splines:
            sub_splines.append(value)
        return "spline_" + str(sub_splines.index(value)) + "(x, z)"


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
        "sampler": {}
    }

    data["sampler"] = read_spline(input["spline"])

    with open('python-scripts/output/density/' + density_file, 'w') as file:
        yaml.dump(data, file)