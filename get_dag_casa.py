#!/usr/bin/env python3

import json
import os
from time import sleep


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

def get_dag_json(dag, w_type):

    json_file = json.dumps(dag)
    f = open('dag_json/'+w_type+'_dag.json', 'w')
    f.write(json_file)
    f.close()
    return

def main(anomaly_type, workflow_type):
    os.makedirs(os.path.join("output", anomaly_type), exist_ok = True)
    workflow_dirs = workflow_type + "/" + anomaly_type + "/panorama/pegasus"

    for workflow_dir in os.listdir(workflow_dirs):
        workflow_name = workflow_dir
        workflow_dir = workflow_dirs + "/" + workflow_dir
        for sub_folder in os.listdir(workflow_dir):
            dag_file = os.path.join(workflow_dir, sub_folder, workflow_name + "-0.dag")
            braindump_file = os.path.join(workflow_dir, sub_folder, "braindump.txt")
            job_state = os.path.join(workflow_dir, sub_folder, "jobstate.log")

            (root, dag) = read_dag(dag_file)
            (root_wf_uuid, wf_uuid) = read_braindump(braindump_file)
            (wf_started, wf_ended) = read_job_log(dag, job_state)
            get_dag_json(dag, workflow_type)
            # print_dag(root, dag)
            return

if __name__ == "__main__":
    anomaly_type = ["normal", "cpu_2", "cpu_3", "hdd_50", "hdd_60", "hdd_70", "hdd_80", "hdd_90", "hdd_100", "loss_0.1", "loss_0.5", "loss_1", "loss_3", "loss_5"]
    workflow_type = ["wind-noclustering", "wind-clustering", "nowcast-clustering-8", "nowcast-clustering-16"]
    for a_type in anomaly_type:
        for w_type in workflow_type:
            main(a_type, w_type)

        exit()
