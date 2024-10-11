import sys

filename = sys.argv[1]
var_name = sys.argv[2]

with open(filename, "r") as f:
    for line in f.readlines():
        if line.startswith(var_name):
            _, args = line.split("=")
            print(args.lstrip(" ").rstrip("\n").rstrip(" "))
