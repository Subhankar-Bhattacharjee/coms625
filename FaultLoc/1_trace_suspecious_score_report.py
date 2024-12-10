import subprocess
import re
import os


def generate_address_to_source_mapping(binary):
    """Generate address-to-source-line mapping using llvm-dwarfdump."""
    mapping = {}
    try:
        result = subprocess.run(
            ["llvm-dwarfdump", "--debug-line", binary], capture_output=True, text=True
        )
        output = result.stdout

        for line in output.splitlines():
            match = re.search(r"(0x[0-9a-fA-F]+).*?line\s+(\d+)", line)
            if match:
                address = match.group(1).lower()
                line_number = int(match.group(2))
                mapping[address] = line_number
    except Exception as e:
        print(f"Error generating address-to-source mapping: {e}")
    return mapping


def create_gdb_script(inputs, trace_file):
    """Creates a GDB script to generate trace logs."""
    return f"""
        set logging file {trace_file}
        set logging on

        break main
        run {inputs}

        define step_and_log_ir
        while ($pc != 0)
            if ($pc == 0)
                break
            end
            x/i $pc
            stepi
        end
        end

        step_and_log_ir

        set logging off
        quit
    """


def filter_trace_log(input_log, output_log):
    """Filters the trace log based on the given criteria."""
    with open(input_log, "r") as infile, open(output_log, "w") as outfile:
        for line in infile:
            line = line.strip()
            if line.startswith("Breakpoint") or re.match(r"^\d+", line) and not ("0x" in line or ".c" in line or "./" in line) or line in ["{", "}"]:
                outfile.write(line + "\n")


def run_test_case(binary, test_input, trace_file):
    """Run a single test case and capture execution trace."""
    gdb_script = create_gdb_script(test_input, trace_file)
    with open("trace.gdb", "w") as f:
        f.write(gdb_script)

    result = subprocess.run(["gdb", "-batch", "-x", "trace.gdb", binary], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"GDB failed for input '{test_input}' with error:\n{result.stderr}")
        return []


def calculate_coverage_data(binary, testcase_file, address_map):
    """Calculate coverage data by running test cases."""
    coverage_data = {}
    total_failed = 0
    total_passed = 0

    with open(testcase_file, "r") as f:
        test_cases = f.readlines()

    for idx, line in enumerate(test_cases):
        line = line.strip()
        if not line:
            continue

        result = "failed" if line.startswith("f") else "passed"
        inputs = " ".join(line.split()[1:])
        trace_file = f"trace_{idx}.log"
        filtered_trace_file = f"filtered_trace_{idx}.log"

        # Run the test case and collect trace
        run_test_case(binary, inputs, trace_file)

        # Apply filtering logic to create updated trace logs
        filter_trace_log(trace_file, filtered_trace_file)

        # Parse updated trace log to map executed instructions to source lines
        executed_lines = set()
        with open(filtered_trace_file, "r") as filtered_log:
            for line in filtered_log:
                if re.match(r"^\d+", line):
                    executed_lines.add(int(line.split()[0]))  # Assuming the first token is the line number

        # Update counters
        if result == "failed":
            total_failed += 1
        else:
            total_passed += 1

        # Update coverage data
        for line_num in executed_lines:
            if line_num not in coverage_data:
                coverage_data[line_num] = {"failed": 0, "passed": 0}
            coverage_data[line_num][result] += 1

    return coverage_data, total_failed, total_passed


def calculate_suspiciousness(coverage_data, total_failed, total_passed):
    """Calculate suspiciousness scores using the Tarantula formula."""
    suspiciousness_scores = {}
    for line, counts in coverage_data.items():
        failed_covered = counts["failed"]
        passed_covered = counts["passed"]
        if total_failed > 0 and total_passed > 0:
            numerator = failed_covered / total_failed
            denominator = numerator + (passed_covered / total_passed)
            suspiciousness = numerator / denominator if denominator > 0 else 0
            suspiciousness_scores[line] = suspiciousness
    return suspiciousness_scores


def main():
    binary = "./minmax"
    testcase_file = "testcase"

    # Compile the binary
    compile_result = subprocess.run(["gcc", "-g", "-o", "minmax", "minmax.c"], capture_output=True, text=True)
    if compile_result.returncode != 0:
        print(f"Compilation failed with error:\n{compile_result.stderr}")
        return

    # Generate address-to-source mapping
    address_map = generate_address_to_source_mapping(binary)

    # Calculate coverage data
    coverage_data, total_failed, total_passed = calculate_coverage_data(binary, testcase_file, address_map)

    # Calculate suspiciousness scores
    suspiciousness_scores = calculate_suspiciousness(coverage_data, total_failed, total_passed)
    print("Suspiciousness Scores:")
    lines=''
    with open("score.log", "w") as outfile:
        for line, score in sorted(suspiciousness_scores.items(), key=lambda x: x[1], reverse=True):
            print(f"Line {line}: Suspiciousness {score:.4f}")
            lines=lines + "\n" + f"Line {line}: Suspiciousness {score:.4f}"
        
        outfile.write(lines + "\n")


if __name__ == "__main__":
    main()
