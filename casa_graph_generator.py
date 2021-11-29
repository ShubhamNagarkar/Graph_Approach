import csv
import graphviz

casa_nowcast_path = '/home/shubham/graph_approach/casa-nowcast-workflow/casa_nowcast-wf-20190325052900-0.dag'
casa_wind_path = '/home/shubham/graph_approach/casa-nowcast-workflow/casa_wind_wf-20200817T054329Z-0.dag'

def read_dag_file(filepath):
    """
    Reads the dag files
    """
    f = open(filepath, 'r')
    dag_file = f.readlines()
    return dag_file
    
def get_parent_child_mapping_from_dag(dag_file):
    """
    Creates a dictionary of parent job id and children job id mapping.
    :input dag_file: dag txt file
    """
    parent_to_child = {}

    for line in dag_file:
        line = line.split()

        if len(line) > 0 and line[0] == "PARENT":
            if line[1] in parent_to_child.keys():
                parent_to_child[line[1]].append(line[-1])
            else:
                parent_to_child[line[1]] = [line[-1]]
        
    return parent_to_child
    
def plot_workflow(fname, parent_to_child):
    """
    plots the workflow using graphviz
    """
    dot = graphviz.Digraph(comment=fname, format='png')

    for k , v in parent_to_child.items():
        dot.node(k)
        for edges in v:
            dot.node(edges)
            dot.edge(k, edges)
            
    fname = dot.render(fname + '.gv', view=True) 
    
def store_mapping_to_csv(mapping, fname):
    """
    Saves a csv file with parent job id and children job id as two columns.
    """
    with open(fname,'w') as f:
        
        w = csv.writer(f)
        w.writerow(['Parent', 'Child'])
        
        for k, v in mapping.items():
            w.writerow([k, v])
    
    
if __name__ == "__main__":

    nowcast_dag = read_dag_file(casa_nowcast_path)
    wind_dag = read_dag_file(casa_wind_path)

    nowcast_map = get_parent_child_mapping_from_dag(nowcast_dag)
    wind_map = get_parent_child_mapping_from_dag(wind_dag)

    plot_workflow('nowcast', nowcast_map)
    plot_workflow('wind', wind_map)

    store_mapping_to_csv(nowcast_map, 'nowcast_mapping.csv')
    store_mapping_to_csv(wind_map, 'wind_mapping.csv')