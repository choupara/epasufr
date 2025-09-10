import clingo
import sys
import re
import subprocess
import os
import time
from datetime import datetime
from collections import defaultdict

# Profiling storage
# Dictionary to accumulate profile durations
profile_data = defaultdict(float)
# Dictionary to store start times per key
profile_start_times = {}

def start_profile(key):
    """Start profiling for a specific key."""
    profile_start_times[key] = time.time()

def record_profile(key):
    """Record elapsed time for a specific key."""
    if key in profile_start_times:
        elapsed = time.time() - profile_start_times[key]
        profile_data[key] += elapsed
        del profile_start_times[key]  # Optional: remove to prevent reuse
    else:
        print(f"Warning: No start time recorded for key '{key}'")    

def print_profile():
    print("\n⏱️  Performance Profile:")    
    total = profile_data.get("Entire program", 0.0)
    if total == 0:
        print("No profiling data recorded for 'Entire program'.")
        return
    for operation, duration in sorted(profile_data.items(), key=lambda x: -x[1]):
        print(f"{operation:<30}: {duration:.4f}s ({duration/total*100:.1f}%)")
    


def extract_show_atoms(content):
    #start_profile("Extract show atoms")
    """Extract atoms from #show directives in the input file."""
    show_atoms = []
    #3 May, updated regex to match "#project in(a24)" and "#project p" both types.
    #show_matches = re.finditer(r'#project\s+(in\([a-zA-Z0-9_]+\))\.', content)
    #show_matches = re.finditer(r'#project\s+(.*\([a-zA-Z0-9_]+\)|[a-zA-Z0-9_]+)\.', content)
    #for match in show_matches:
    #    show_atoms.append(match.group(1))
    for line in content:
        if "#project" in line and not line.strip().startswith("%"):
            match = re.search(r'#project\s+([a-zA-Z_][a-zA-Z0-9_]*\([a-zA-Z0-9_]+\)|[a-zA-Z_][a-zA-Z0-9_]*)\.', line)
            if match:
                show_atoms.append(match.group(1))
    #record_profile("Extract show atoms")
    return show_atoms

def generate_constraints(filtered_ex_atoms, filtered_in_atoms,nv_ex_atoms,nv_in_atoms):
    #start_profile("Generate constraints")
    """Generate constraints based on the answer set and show atoms."""
    constraints = []
    # Convert answer set symbols to string names
    #as_atoms = [str(atom) for atom in answer_set]
    # print("INSIDE generate_constraints: answer_set,", answer_set)
    # print("INSIDE generate_constraints: show_atoms", show_atoms)
    # Check if answer set has all show atoms
    #all_atoms_present = all(atom in as_atoms for atom in show_atoms)
    for atom in filtered_in_atoms:
        constraints.append(f":- not {atom}.")
        # print(":- not ",atom)
    for atom in filtered_ex_atoms:        
        constraints.append(f":- {atom}.")
        # print(":- ",atom)     
    for atom in nv_in_atoms:
        constraints.append(f":- not {atom}.")
        # print(":- not ",atom)    
    #record_profile("Generate constraints")
    return constraints

def create_modified_program(original_file, constraints):
    # start_profile("Create modified program")
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
    # record_profile("Create modified program")
    return temp_filename


def execute_fasb(modified_file):
    start_profile("FASB execution")
    """Execute the fasb command on the modified program."""
    fasb_args = "#?\n"  # REPL-style input as a string
    with open("fct_cnt.fsb", "w") as file:
        file.write(fasb_args)
    fasb_command = ["fasb", modified_file, "0", "fct_cnt.fsb"]
    try:
        result = subprocess.run(fasb_command, capture_output=True, text=True, check=True)
        print("FASB execution output:")
        print(result.stdout)
        record_profile("FASB execution")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing fasb command: {e}")
        print(f"FASB stderr output: {e.stderr}")
        record_profile("FASB execution")
        return None
    #remove temporary fasb file    
    os.remove("fct_cnt.fsb")    

def execute_fasb_bench(modified_file):
    start_profile("FASB execution")
    """Execute the fasb command on the modified program."""
    # if bench_scirpt.fsb not present, print error and return
    if not os.path.isfile("bench_scirpt.fsb"):
        print("Error: bench_scirpt.fsb file not found.")
        return None
    
    fasb_command = ["fasb", modified_file, "0", "bench_scirpt.fsb"]
    try:
        result = subprocess.run(fasb_command, capture_output=True, text=True, check=True)
        print("FASB execution output:")
        print(result.stdout)
        record_profile("FASB execution")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing fasb command: {e}")
        print(f"FASB stderr output: {e.stderr}")
        record_profile("FASB execution")
        return None    

def facet_processing(filtered_ex_atoms, filtered_in_atoms, nv_ex_atoms, nv_in_atoms, projected_file):
    facets_count = 0
    facets_list = []
    print("\nFacet Count Processing:")

    constraints = generate_constraints(filtered_ex_atoms, filtered_in_atoms, nv_ex_atoms, nv_in_atoms)
    modified_file = create_modified_program(projected_file, constraints)
    stdout = execute_fasb(modified_file)

    if stdout is None:
        return []

    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    opt_lines = stdout.splitlines()

    # Remove empty lines
    r_emp_lines = [line for line in opt_lines if line.strip()]

    # Remove ANSI codes and filter out lines starting with "::"
    lines = [
        line for line in r_emp_lines
        if not ansi_escape.sub('', line).strip().startswith("::")
    ]

    try:
        facets_count = int(lines[1])
    except (IndexError, ValueError):
        print("Invalid or missing facet count format.")
        return []

    return facets_count


def f_bench_processing(filtered_ex_atoms, filtered_in_atoms, nv_ex_atoms, nv_in_atoms, projected_file):
    constraints = generate_constraints(filtered_ex_atoms, filtered_in_atoms, nv_ex_atoms, nv_in_atoms)
    modified_file = create_modified_program(projected_file, constraints)
    stdout = execute_fasb_bench(modified_file)
    return stdout

def main(projected_file, limit_type, limit_value, mode):   
    
    with open(projected_file, 'r') as f:
        content = f.readlines()
            
    #--- Extract show atoms
    show_atoms = extract_show_atoms(content)
    if not show_atoms:
        print("Error: No projection in input ASP. Program bypassed.")
        return
    else:
        print(f"\nProjected atoms extracted: {show_atoms}")

    # Initialize solver and counters
    ctl = clingo.Control(["0", "--project"])
    start_profile("Clingo initialization")
    ctl.load(projected_file)
    ctl.ground([("base", [])])
    record_profile("Clingo initialization")
 
    # Solve and process answer sets
    ans_solve_start = time.time()
    all_ans_sets=[]
    all_ans_facets=[]
    all_filtered_in_atoms=[]
    all_filtered_ex_atoms=[]
    nv_in_atoms=[]
    nv_ex_atoms=[]

    start_profile("Answer set processing")  
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            if limit_type =="c":
                if len(all_ans_sets) >= limit_value:
                    #print(f"\n🔢 Answer set limit of {limit_value} reached")
                    break
            if limit_type =="t":
                elapsed = time.time() - ans_solve_start
                if elapsed >= limit_value:
                    print(f"\n⏰ Time limit of {limit_value} seconds reached")
                    break              
            answer_set = model.symbols(shown=True)
            if answer_set:                 
                answer_set_strs = set(map(str, answer_set))
                filtered_in_atoms = [atom for atom in show_atoms if atom in answer_set_strs]
                filtered_ex_atoms = [atom for atom in show_atoms if atom not in answer_set_strs]      
                all_ans_sets.append(answer_set)
                all_filtered_in_atoms.append(filtered_in_atoms)
                all_filtered_ex_atoms.append(filtered_ex_atoms)
    # End of solving            
    record_profile("Answer set processing")      
    start_profile("Projected facet counting")                  
    if len(all_ans_sets) == 0:
        print("No answer sets found with the specified projected atoms.")
        return  
    else:
        print(f"\nTotal answer sets found: {len(all_ans_sets)}")
        #for all_ans_index in enumerate(all_ans_sets)
        for ans_idx, ans_sets in enumerate(all_ans_sets):
            facet_count=facet_processing(all_filtered_ex_atoms[ans_idx],
                                        all_filtered_in_atoms[ans_idx],
                                        nv_ex_atoms,
                                        nv_in_atoms,
                                        projected_file)
            print(f"\n✅ Projected answer Set {ans_idx + 1}: {ans_sets}")        
            print("Inclusive Projected Atoms: ", all_filtered_in_atoms[ans_idx])
            print("Exclusive Projected Atoms: ", all_filtered_ex_atoms[ans_idx])
            print("Facet Count: ",facet_count)
            all_ans_facets.append(facet_count)
    record_profile("Projected facet counting")

    # Start navigation mode   
    start_profile("Navigation") 
    print("\n Navigation mode started:")
    if mode == "max":
        nav_idx= all_ans_facets.index(max(all_ans_facets))
    elif mode == "min":
        nav_idx= all_ans_facets.index(min(all_ans_facets))
    elif mode == "one":
        nav_idx=0
    else:
        print("Invalid mode. Use 'max' , 'min' or 'one'.")
        return            

    f_bench_processing(all_filtered_ex_atoms[nav_idx],
                                    all_filtered_in_atoms[nav_idx],
                                    nv_ex_atoms,
                                    nv_in_atoms,
                                    projected_file)
    record_profile("Navigation")
                              


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py as_r_file.lp")
        sys.exit(1)
    projected_file=sys.argv[1]        
    # Usage: python script.py as_r_file.lp [limit_type=c/t] [limit_value] [mode=max/min]
    # if limit type is # then limit value is number of answer sets
    # if limit type is t then limit value is time in seconds
    # default limit type is #
    # default limit value is 100
    # default mode is max
    # Parse command line arguments    


    if len(sys.argv) >= 3:
        limit_type = sys.argv[2]
        if limit_type not in ['c', 't']:
            print("Invalid limit type. Use '#' for answer set count or 't' for time limit.")
            sys.exit(1)
    else:
        print("No limit type provided. Using default limit by answer count.")
        limit_type ='c'  # Default limit type


    if len(sys.argv) >= 4:
        limit_value =sys.argv[3]
        try:
            limit_value = int(limit_value)
            if limit_value <= 0:
                raise ValueError
        except ValueError:
            print("Limit value must be a positive integer.")
            sys.exit(1)
    else:
        print("No limit value provided. Using default limit of 100.")
        limit_value =100  # Default limit value



    if len(sys.argv) >= 5:
        mode = sys.argv[4]  
        if mode not in ['max', 'min', 'one']:
            print("Invalid mode. Use 'max' , 'min' or 'one'.")
            sys.exit(1)
    else:
        print("No mode provided. Using default mode 'max' facet count under projection.")
        mode ='max'  # Default mode       


    if mode == 'one':
        limit_type = "c"
        limit_value = 1
    # Run the main program     
    # print projected_file, limit_type, limit_value, mode
    print(f"\n🚀 Starting program with file: {projected_file}, limit_type: {limit_type}, limit_value: {limit_value}, mode: {mode}\n")

    start_profile("Entire program")
    main(projected_file, limit_type, limit_value, mode)
    record_profile("Entire program")
    # Print detailed profile    
    print_profile()
