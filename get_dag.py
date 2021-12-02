#!/usr/bin/env python3

import json
import os


def read_dag(dag_file):
    jobs = {}
    allChildNodes = set()

    with open(dag_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("JOB"):
                splitted = line.split()
                jobs[splitted[1]] = {
                    "timeline": {"ready": None, "pre_script_start": None, "pre_script_end": None, "submit": None, "execute_start": None, "execute_end": None, "stage_in_start": None, "stage_in_end": None, "stage_out_start": None, "stage_out_end": None, "post_script_start": None, "post_script_end": None}, 
                    "delays": {"wms_delay": None, "pre_script_delay": None, "queue_delay": None, "runtime": None, "post_script_delay": None, "stage_in_delay": None, "stage_out_delay": None}, 
                    "childNodes": [],
                    "parentNodes": []
                }

            if line.startswith("PARENT"):
                splitted = line.split()
                jobs[splitted[1]]["childNodes"].append(splitted[3])
                jobs[splitted[3]]["parentNodes"].append(splitted[1])
                allChildNodes.add(splitted[3])

    root = ""
    for job in jobs:
        if not job in allChildNodes:
            root = job
            break

    return (root, jobs)

def print_dag(root, dag):
    queue = [(root, 0)]

    while queue:
        node, level = queue.pop(0)
        print(node, level)
        for job in dag[node]["childNodes"]:
            if not (job, level+1) in queue:
                queue.append((job, level+1))

def read_braindump(braindump_file):
    wf_uuid = ""
    root_wf_uuid = ""
    with open(braindump_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            splitted = line.split()
            if splitted[0] == "root_wf_uuid":
                root_wf_uuid = splitted[1]
            elif splitted[0] == "wf_uuid":
                wf_uuid = splitted[1]

    return (root_wf_uuid, wf_uuid)

def read_job_log(dag, job_log):
    lines = []

    wf_started = 0
    wf_ended = 0

    with open(job_log, 'r') as f:
        lines = f.readlines()

    for line in lines:
        splitted = line.split()
        
        if splitted[3] == "DAGMAN_STARTED":
            wf_started = int(splitted[0])
            continue
        elif splitted[3] == "DAGMAN_FINISHED":
            wf_ended = int(splitted[0])
            continue

        if splitted[2] == "PRE_SCRIPT_STARTED":
            dag[splitted[1]]["timeline"]["pre_script_start"] = int(splitted[0])
        elif splitted[2] == "PRE_SCRIPT_SUCCESS":
            dag[splitted[1]]["timeline"]["pre_script_end"] = int(splitted[0])
        elif splitted[2] == "SUBMIT":
            dag[splitted[1]]["timeline"]["submit"] = int(splitted[0])
        elif splitted[2] == "EXECUTE":
            dag[splitted[1]]["timeline"]["execute_start"] = int(splitted[0])
        elif splitted[2] == "JOB_SUCCESS":
            dag[splitted[1]]["timeline"]["execute_end"] = int(splitted[0])
        elif splitted[2] == "POST_SCRIPT_STARTED":
            dag[splitted[1]]["timeline"]["post_script_start"] = int(splitted[0])
        elif splitted[2] == "POST_SCRIPT_SUCCESS":
            dag[splitted[1]]["timeline"]["post_script_end"] = int(splitted[0])

    return (wf_started, wf_ended)

def get_dag_json(dag):

    json_file = json.dumps(dag)
    f = open('dag_json/1000_genome_dag.json', 'w')
    f.write(json_file)
    f.close()
    return

def main(workflow_type, workflow_name):
    os.makedirs(os.path.join("output", workflow_type), exist_ok = True)
    workflow_dir = os.path.join("1000genome/submit/panorama/pegasus", workflow_name)

    for sub_folder in os.listdir(workflow_dir):
        print(sub_folder)
        dag_file = os.path.join(workflow_dir, sub_folder, workflow_name + "-0.dag")
        braindump_file = os.path.join(workflow_dir, sub_folder, "braindump.txt")
        job_state = os.path.join(workflow_dir, sub_folder, "jobstate.log")

        (root, dag) = read_dag(dag_file)
        (root_wf_uuid, wf_uuid) = read_braindump(braindump_file)
        (wf_started, wf_ended) = read_job_log(dag, job_state)
        
        get_dag_json(dag)
        # print_dag(root, dag)
        exit()

if __name__ == "__main__":
    with open("config.json", "r") as f:
        workflows = json.load(f)
    for workflow_type in workflows:
        for workflow_name in workflows[workflow_type]:
            main(workflow_type, workflow_name)
     
