import re

with open("women_safety_cli.py", "r") as f:
    code = f.read()

# Fix bare excepts
code = code.replace("except:", "except Exception:")

# Fix == True
code = code.replace("== True", "")

# Fix unused globals by removing them if they are in global statement
# "global is_siren_playing" inside background_siren_loop
code = code.replace("    global is_siren_playing\n    while is_siren_playing:", "    while is_siren_playing:")
# "global current_contacts" on line 255
code = code.replace("    global current_contacts\n", "")

# Strip trailing whitespace on each line
lines = code.split("\n")
lines = [line.rstrip() for line in lines]
code = "\n".join(lines)

with open("women_safety_cli.py", "w") as f:
    f.write(code)

print("Done")
