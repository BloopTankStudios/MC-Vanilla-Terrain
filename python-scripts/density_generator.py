
import os
import yaml

def read_spline(spline, depth):
    sampler = spline["coordinate"].split("/")[1] + "(x, z)"
    points = spline["points"]

    expression_depth = ""
    for i in range(depth):
        expression_depth += "  "

    # Trail Start
    expression = expression_depth + "spline_left_end(" + sampler + ", " + str(points[0]["location"]) + ", " + \
        str(points[0]["derivative"]) + ", " + read_point(points[0]["value"], depth) + ") +\n"

    # Points
    for p in range(len(points) - 1):
        expression += expression_depth + "spline(" + sampler + ", " + str(points[p]["location"]) + ", " + \
        str(points[p]["derivative"]) + ", " + read_point(points[p]["value"], depth) + ", " + \
        str(points[p+1]["location"]) + ", " + str(points[p+1]["derivative"]) + ", " + read_point(points[p+1]["value"], depth) + ") +\n"

    # Trail End
    expression += expression_depth + "spline_right_end(" + sampler + ", " + str(points[-1]["location"]) + ", " + \
        str(points[-1]["derivative"]) + ", " + read_point(points[-1]["value"], depth) + ")"
    
    return expression

def read_point(value, depth):
    if type(value) == float or type(value) == int:
        return str(value)
    else:
        return "\n" + read_spline(value, depth + 1)


density_files = os.listdir('python-scripts/input/density')

for density_file in density_files:
    with open('python-scripts/input/density/' + density_file, 'r') as file:
        input = yaml.safe_load(file)
    
    expression = "\texpression: |\n"

    expression = read_spline(input["spline"], 2)

    with open('python-scripts/output/density/' + density_file, 'w') as file:
        print(expression, file=file)