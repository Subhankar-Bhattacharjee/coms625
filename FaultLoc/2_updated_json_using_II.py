import json

# Paths to files
ll_file_path = "minmax.ll"  # Replace with your .ll file path
json_file_path = "minmax.json"  # Replace with your JSON file path
output_json_file = "updated_minmax.json"  # Output JSON file

# Helper function to normalize instructions
def normalize_instruction(instruction):
    # Remove metadata and standardize spacing
    instruction = instruction.split(", !dbg")[0].strip()
    instruction = instruction.replace("ptr", "i32*").replace("noundef ", "").replace("align ", "")
    return " ".join(instruction.split())

# Load the .ll file
try:
    with open(ll_file_path, "r") as f:
        ll_lines = f.readlines()
except FileNotFoundError:
    print(f"Error: File {ll_file_path} not found.")
    exit(1)

# Extract line numbers from .ll file
line_number_mapping = {}
for line in ll_lines:
    if "dbg" in line:
        line_number = None
        if "!dbg !" in line:
            dbg_id = line.split("!dbg !")[1].split()[0]
            for dbg_line in ll_lines:
                if f"!{dbg_id} = !DILocation" in dbg_line and "line:" in dbg_line:
                    line_number = int(dbg_line.split("line:")[1].split(",")[0].strip())
                    break
        if line_number:
            normalized_instruction = normalize_instruction(line)
            line_number_mapping[normalized_instruction] = line_number

# Debugging: Print extracted mappings
print(f"Extracted line number mappings: {line_number_mapping}")

# Load the JSON file
try:
    with open(json_file_path, "r") as f:
        json_data = json.load(f)
except FileNotFoundError:
    print(f"Error: File {json_file_path} not found.")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Invalid JSON format in {json_file_path}.")
    exit(1)

# Update JSON with line numbers
for block in json_data:
    if "instruction" not in block:
        continue  # Skip blocks without "instruction"
    for instruction in block["instruction"]:
        if len(instruction) < 2 or not isinstance(instruction[1], list):
            continue  # Skip invalid instruction format
        inst_details = instruction[1]
        for i, detail in enumerate(inst_details):
            normalized_detail = normalize_instruction(detail)
            if normalized_detail in line_number_mapping:
                line_number = line_number_mapping[normalized_detail]
                inst_details[i] = f"{normalized_detail} (Line {line_number})"
            else:
                print(f"Warning: Instruction '{normalized_detail}' not found in mappings.")

# Save the updated JSON file
try:
    with open(output_json_file, "w") as f:
        json.dump(json_data, f, indent=4)
    print(f"Updated JSON file saved as {output_json_file}")
except IOError as e:
    print(f"Error: Unable to save updated JSON file. {e}")
