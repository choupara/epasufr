import clingo
import sys
import re
import subprocess
import os
import time
from datetime import datetime
from collections import defaultdict

# Profiling storage
profile_data = defaultdict(float)
last_profile_time = None

def start_profile():
    global last_profile_time
    last_profile_time = time.time()

def record_profile(operation):
    global last_profile_time
    now = time.time()
    profile_data[operation] += now - last_profile_time
    last_profile_time = now

def print_profile():
    print("\n⏱️  Performance Profile:")
    total = sum(profile_data.values())
    for operation, duration in sorted(profile_data.items(), key=lambda x: -x[1]):
        print(f"{operation:<30}: {duration:.4f}s ({duration/total*100:.1f}%)")
    print(f"{'Total':<30}: {total:.4f}s")

def get_user_limits():
    """Ask user what kind of limit they want to set."""
    start_profile()
    print("\nChoose the type of limit you want to set:")
    print("1. Limit by number of answer sets")
    print("2. Limit by time (seconds)")
    print("3. No limits (run to completion)")
    record_profile("User input")

    while True:
        choice = input("Enter your choice (1, 2, or 3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("Invalid choice. Please enter 1, 2, or 3.")

    if choice == '3':
        return None, None

    while True:
        try:
            if choice == '1':
                limit = int(input("Enter maximum number of answer sets to compute: "))
            else:
                limit = int(input("Enter maximum time in seconds: "))
            if limit > 0:
                return choice, limit
            print("Limit must be a positive integer.")
        except ValueError:
            print("Please enter a valid integer.")

def extract_show_atoms(filename):
    start_profile()
    """Extract atoms from #show directives in the input file."""
    show_atoms = []
    with open(filename, 'r') as f:
        content = f.read()
        #3 May, updated regex to match "#project in(a24)" and "#project p" both types.
        #show_matches = re.finditer(r'#project\s+(in\([a-zA-Z0-9_]+\))\.', content)
        show_matches = re.finditer(r'#project\s+(.*\([a-zA-Z0-9_]+\)|[a-zA-Z0-9_]+)\.', content)
        for match in show_matches:
            show_atoms.append(match.group(1))
    record_profile("Extract show atoms")
    return show_atoms

def generate_constraints(answer_set, show_atoms):
    start_profile()
    """Generate constraints based on the answer set and show atoms."""
    constraints = []
    # Convert answer set symbols to string names
    #as_atoms = [str(atom) for atom in answer_set]
    print("INSIDE generate_constraints: answer_set,", answer_set)
    print("INSIDE generate_constraints: show_atoms", show_atoms)

    # Check if answer set has all show atoms
    #all_atoms_present = all(atom in as_atoms for atom in show_atoms)
    all_atoms_present = all(atom in answer_set for atom in show_atoms)

    if all_atoms_present:
        # Case 2.1: If all show atoms are in the answer set
        print("all_atoms_present FLAG set to TRUE")
        for atom in show_atoms:
            constraints.append(f":- not {atom}.")
    else:
        # Case 2.2: Otherwise
        for atom in show_atoms:
            #if atom in as_atoms:
            if atom in answer_set:
                constraints.append(f":- not {atom}.")
                print(":- not ",atom)
            else:
                constraints.append(f":- {atom}.")
                print(":- ",atom)
    record_profile("Generate constraints")
    return constraints

def create_modified_program(original_file, constraints):
    start_profile()
    """Create a new program by removing #show directives and adding constraints."""
    with open(original_file, 'r') as f:
        content = f.readlines()
    #filtered_content = [line for line in content if not line.strip().startswith('#project')]
    filtered_content = [
        line for line in content
        #if not (line.lstrip().startswith('#show') or line.lstrip().startswith('#project'))
        if not (line.lstrip().startswith('#project'))
    ]
    # Add new constraints
    modified_content = ''.join(filtered_content) + '\n' + '\n'.join(constraints)
    temp_filename = "modified.lp"
    with open(temp_filename, 'w') as f:
        f.write(modified_content)
    record_profile("Create modified program")
    return temp_filename


def execute_fasb(modified_file):
    start_profile()
    """Execute the fasb command on the modified program."""
    fasb_command = ["fasb", modified_file, "0", "facet_count.fsb"]
    try:
        result = subprocess.run(fasb_command, capture_output=True, text=True, check=True)
        print("FASB execution output:")
        print(result.stdout)
        record_profile("FASB execution")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing fasb command: {e}")
        print(f"FASB stderr output: {e.stderr}")
        record_profile("FASB error")
        return None

def main(projected_file, limit_type=None, limit_value=None):
    # Record program start time
    program_start = datetime.now()
    print(f"\n🚀 Program started at: {program_start.strftime('%Y-%m-%d %H:%M:%S')}")
    start_profile()

    # Check projection requirements
    with open(projected_file, 'r') as f:
        content = f.readlines()
    show_lines = [line for line in content if "#project" in line]
    all_commented = all(line.strip().startswith('%') for line in show_lines)
    no_show_lines = len(show_lines) == 0
    record_profile("Projection check")

    if all_commented or no_show_lines:
        print("Error: No projection in input ASP. Program bypassed.")
        return

    # Extract show atoms
    show_atoms = extract_show_atoms(projected_file)

    # Initialize solver and counters
    ctl = clingo.Control(["0", "--project"])
    start_profile()
    ctl.load(projected_file)
    ctl.ground([("base", [])])
    record_profile("Clingo initialization")

    total_answer_sets = 0
    last_answer_time = None

    # Solve based on limit type
    if limit_type == '1':
        print(f"\n🔢 Computing up to {limit_value} answer sets...")
        solve_start = time.time()
        with ctl.solve(yield_=True) as handle:
            for model in handle:
                start_profile()
                total_answer_sets += 1
                elapsed = time.time() - solve_start
                last_answer_time = elapsed

                answer_set = model.symbols(shown=True)
                filtered_atoms = [str(atom) for atom in answer_set if str(atom) in show_atoms]
                if not filtered_atoms:
                    print(f"⚠️ Answer Set {total_answer_sets + 1} (Filtered out, no matching atoms)")
                    continue  # Skip further processing for this answer set
                print(f"\n✅ Answer Set {total_answer_sets} (Found at +{elapsed:.2f}s):")
                print(filtered_atoms)

                constraints = generate_constraints(filtered_atoms, show_atoms)
                modified_file = create_modified_program(projected_file, constraints)
                execute_fasb(modified_file)
                #os.remove(modified_file)
                record_profile("Answer set processing")

                if total_answer_sets >= limit_value:
                    break

        print(f"\n📊 Total answer sets found: {total_answer_sets}")

    elif limit_type == '2':
        print(f"\n⏳ Computing answer sets for up to {limit_value} seconds...")
        solve_start = time.time()
        with ctl.solve(yield_=True, async_=True) as handle:
            try:
                for model in handle:
                    start_profile()
                    elapsed = time.time() - solve_start
                    if elapsed >= limit_value:
                        handle.cancel()
                        break

                    total_answer_sets += 1
                    last_answer_time = elapsed

                    answer_set = model.symbols(shown=True)
                    filtered_atoms = [str(atom) for atom in answer_set if str(atom) in show_atoms]
                    if not filtered_atoms:
                        print(f"⚠️ Answer Set {total_answer_sets + 1} (Filtered out, no matching atoms)")
                        continue  # Skip further processing for this answer set
                    print(f"\n✅ Answer Set {total_answer_sets} (Found at +{elapsed:.2f}s):")
                    print(filtered_atoms)

                    constraints = generate_constraints(filtered_atoms, show_atoms)
                    modified_file = create_modified_program(projected_file, constraints)
                    execute_fasb(modified_file)
                    #os.remove(modified_file)
                    record_profile("Answer set processing")

            except Exception as e:
                if "interrupted" in str(e).lower():
                    print(f"\n⏰ Time limit of {limit_value} seconds reached")

        print(f"\n📊 Total answer sets found: {total_answer_sets}")

    else:
        print("\n♾️ Computing all answer sets (no limits)...")
        solve_start = time.time()

        with ctl.solve(yield_=True) as handle:
            for model in handle:
                start_profile()
                total_answer_sets += 1
                elapsed = time.time() - solve_start
                last_answer_time = elapsed
                answer_set = model.symbols(shown=True)
                print ("answer_set", answer_set)
                print ("from main - show_atoms", show_atoms)
                filtered_atoms = [str(atom) for atom in answer_set if str(atom) in show_atoms]
                if not filtered_atoms:
                    print(f"⚠️ Answer Set {total_answer_sets + 1} (Filtered out, no matching atoms)")
                    continue  # Skip further processing for this answer set
                print(f"\n✅ Answer Set {total_answer_sets} (Found at +{elapsed:.2f}s):")
                print("filtered_atoms",filtered_atoms)

                constraints = generate_constraints(filtered_atoms, show_atoms)
                modified_file = create_modified_program(projected_file, constraints)
                execute_fasb(modified_file)
                #os.remove(modified_file)
                record_profile("Answer set processing")

        print(f"\n📊 Total answer sets found: {total_answer_sets}")

    # Final statistics
    solve_end = time.time()
    if total_answer_sets > 0:
        print(f"⏱️  Last answer found at: {last_answer_time:.2f}s")
        print(f"📈 Answer sets per second: {total_answer_sets/(solve_end-solve_start):.2f}")
    print(f"⏱️  Total solving time: {solve_end - solve_start:.2f} seconds")

    # Program completion
    program_end = datetime.now()
    print(f"\n🏁 Program completed at: {program_end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏳ Total execution time: {(program_end - program_start).total_seconds():.2f} seconds")

    # Print detailed profile
    print_profile()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py as_r_file.lp")
        sys.exit(1)

    # Get user preferences
    limit_type, limit_value = get_user_limits()

    # Run the main program with the specified limits
    main(sys.argv[1], limit_type, limit_value)