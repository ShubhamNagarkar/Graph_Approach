from numpy.lib.type_check import real_if_close
import numpy as np
import os, csv, json

REL = os.getcwd()
PATH = os.path.join(REL, 'dag_json/')


def get_workflow_dict(workflow_name):
    """
    loads the yaml file into a dictionary.
    """
    f = open(PATH+workflow_name)
    wf_dict = json.load(f)
    
    return wf_dict


def create_adjacency_matrix(n_jobs, ind_to_job, wf_info, fname):
    """
    Creates adjacency matrix
    :input n_jobs: number of jobs
    :input ind_to_job: dictionary with index as key and job id as value.
    :input job_to_child: parent children mapping information
    :input fname: file name to save the npy matrix
    """
    adj_mat = np.zeros((n_jobs, n_jobs))
    for i in range(0, n_jobs):
        for j in range(0, n_jobs):
            parent = ind_to_job[i]
            child = ind_to_job[j]

            if child in wf_info[parent]['childNodes']:
                adj_mat[i][j] += 1
    
    np.save(REL + '/adj_matrices'+fname, adj_mat)
    
    return adj_mat

def save_index_to_job_mapping(ind_to_job, wf_name):
    """
    Creates a csv of index number to job number mapping present in the matrix.
    Eg: row 1 of the matrix is job id 12345
        row 2 of the matrix is job id 67891
    """
    with open(REL + '/adj_matrices/'+wf_name+'_index_to_job_id.csv','w') as f:
        w = csv.writer(f)
        w.writerow(['index', 'job_id'])
        for k, v in ind_to_job.items():
            w.writerow([k, v])


if __name__ == "__main__":
    

    workflows = os.listdir(PATH)
    
    for wf_name in workflows:
        wf_dict = get_workflow_dict(wf_name)

        child_key = 'childNodes'
        parent_key = 'parentNodes'

        print("Number of unique jobs: ",len(wf_dict.keys()))
        
        job_ids = wf_dict.keys()

        ind_to_job = {ind:job_idx for ind, job_idx in enumerate(job_ids)}
        n_jobs = len(job_ids)
        
        name = wf_name.split('dag')[0]
        file_name = '/'+name+'_adjacency_matrix.npy'
        adjacency_matrix = create_adjacency_matrix(n_jobs, ind_to_job, wf_dict, file_name)

        save_index_to_job_mapping(ind_to_job, name)
   
