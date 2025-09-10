import clingo
import sys
import re
import subprocess
import os
import time
from datetime import datetime
from collections import defaultdict
import subprocess
import selectors


def get_inst_fasb(modified_file):
    fasb_command = ["fasb", modified_file, "0"]
    try:
        proc = subprocess.Popen(
            fasb_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        return proc    
    except Exception as e:
        print(f"Exception during FASB interaction: {e}")
        return None


def send_input_fasb(user_input,proc):
    output=call_fasb_with_input(user_input,proc)    
    print("\n".join(output))    

    #Dummy call added to flush out pending output line
    mode_cmd=":mode\n"
    output=call_fasb_with_input(mode_cmd,proc)
    for line in output:
        if ("goal oriented" in line or "strictly" in line):
            pass
        else:
            print(line)    

def call_fasb_with_input(user_input,proc):    
    output=[]
    try:      
        sel = selectors.DefaultSelector()
        sel.register(proc.stdout, selectors.EVENT_READ)
        #print(f"Sending to fasb: {user_input.strip()}")
        proc.stdin.write(user_input)
        proc.stdin.flush()
        # Read available output without blocking
        #sleep a bit to allow fasb to respond  
        timeout = 5 if user_input.startswith(("!")) else 2      
        while True:                        
            events = sel.select(timeout=timeout)                   
            if not events:
                #print(f"Waiting time {timeout} and Breaking.")
                break
            for key, _ in events:
                line = key.fileobj.readline()
                if line:
                    output.append(line.strip())
    except Exception as e:
        print(f"Exception during FASB interaction: {e}")
    return output        

        
def close_fasb(proc):
    try:
        proc.stdin.close()
        proc.wait()
    except Exception as e:
        print(f"Exception during closing FASB: {e}")        

if __name__ == "__main__":
    nv_in_atoms=[]
    nv_ex_atoms=[]
    #execute_fasb_with_activate()
    modified_file="taxonomy_ic.lp"
    proc=get_inst_fasb(modified_file)
    if proc is None:
        sys.exit(1)

    # mode_cmd=":mode\n"
    # send_input_fasb(mode_cmd,proc)

    ans_cnt_cmd="#!\n"    
    print(f"\n✅Counting all answer sets")
    send_input_fasb(ans_cnt_cmd,proc)


    enum_all_ans_cmd="!\n"
    print(f"\n✅Enumerating all answer sets")
    send_input_fasb(enum_all_ans_cmd,proc)

    cnt_cmd = "#?\n"
    print(f"\n✅Counting all facets")
    send_input_fasb(cnt_cmd,proc)    

    print_cmd =  "?\n"
    print(f"\n✅Printing all facets")
    send_input_fasb(print_cmd,proc)
    # print("Enter actvate_facet <facet> to activate a facet")
    # act_begin="+ facets"    
    # user_input = input("User Input: ")
    # act_cmd=act_begin+" "+user_input+"\n"                
    # send_input_fasb(act_cmd,proc)
    # send_input_fasb(cnt_cmd,proc)        
    # send_input_fasb(print_cmd,proc)    
    # print("Deactivating previous facet")
    # dact_cmd="- \n"
    # send_input_fasb(dact_cmd,proc)
    # send_input_fasb(cnt_cmd,proc)        
    # send_input_fasb(print_cmd,proc)    
    #use facet-counting strictly goal-oriented mode
    

    print(f"\n✅Facet counts under each facet")
    #mode_cmd="' min#f\n"
    #mode_cmd="' max#f\n"
    mode_cmd="#??\n"
    send_input_fasb(mode_cmd,proc)

    print(f"\n✅Using facet-counting strictly goal-oriented mode")
    #mode_cmd="' min#f\n"
    #mode_cmd="' max#f\n"
    mode_cmd="' go\n"
    send_input_fasb(mode_cmd,proc)


    #perform step (causing highest uncertainty reduction)
    print(f"\n✅Performing step")
    step_cmd="$$\n"
    send_input_fasb(step_cmd,proc)

    # query current route
    print(f"\n✅Query Current route:")
    prnt_route_cmd="@\n"
    send_input_fasb(prnt_route_cmd,proc)

    # enumerate all answer sets under current route
    print(f"\n✅Enumerating all answer sets under current route:")
    enum_cur_route_cmd="!\n"
    send_input_fasb(enum_cur_route_cmd,proc)


    # mode_cmd=":mode\n"
    # send_input_fasb(mode_cmd,proc)
    close_fasb(proc)



