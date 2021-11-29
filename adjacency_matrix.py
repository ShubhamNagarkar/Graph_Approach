from numpy.lib.type_check import real_if_close
import numpy as np
import yaml, os, csv

REL = os.getcwd()
PATH_1000Genome = REL + '/1000genome-workflow/workflow.yml'

def get_workflow_dict():
    
    f = open(PATH_1000Genome)
    wf_dict = yaml.load(f)
    
    return wf_dict

def get_job_data(job_dict):
    
    job_to_info = {}
    job_ids = []
    for job in job_dict:
        job_id = job['id']
        job_type = job['type']
        job_name  = job['name']
        job_arguments = job['arguments']
        job_uses = job['uses']
        job_ids.append(job_id)
        job_to_info[job_id] = {'name':job_name, 'type': job_type, 'arguments':job_arguments, 'uses':job_uses}
    
    print("Number of jobs in the 1000Genome Workflow: ",len(job_to_info))
    
    return job_to_info, job_ids

def map_parent_children(dependency):
    
    job_to_child = {}

    for row in dependency:
        parent = row['id']
        children = row['children']
        job_to_child[parent] = children
    
    return job_to_child


def create_adjacency_matrix(n_jobs, ind_to_job, job_to_child, fname):
    
    adj_mat = np.zeros((n_jobs, n_jobs))
    for i in range(0, n_jobs):
        for j in range(0, n_jobs):
            parent = ind_to_job[i]
            child = ind_to_job[j]
            if parent not in job_to_child.keys():
                continue
            if child in job_to_child[parent]:
                adj_mat[i][j] += 1
    
    np.save(REL + fname, adj_mat)
    
    return adj_mat

def save_index_to_job_mapping(ind_to_job):
    
    with open(REL + '/index_to_job_id.csv','w') as f:
        w = csv.writer(f)
        w.writerow(['index', 'job_id'])
        for k, v in ind_to_job.items():
            w.writerow([k, v])

if __name__ == "__main__":
    
    wf_dict = get_workflow_dict()
    
    job_dict = wf_dict['jobs']
    dependency = wf_dict['jobDependencies']
    
    job_to_info, job_ids = get_job_data(job_dict)
    
    job_to_child = map_parent_children(dependency)
    
    ind_to_job = {ind:job_idx for ind, job_idx in enumerate(job_ids)}
    n_jobs = len(job_ids)
    
    file_name = '/1000_genome_adjacency_matrix.npy'
    adjacency_matrix = create_adjacency_matrix(n_jobs, ind_to_job, job_to_child, file_name)
    save_index_to_job_mapping(ind_to_job)
   
