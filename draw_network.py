import graphviz
import os
import visualizer
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
def save_graph_as_svg(dot_string, output_file_name):
    if type(dot_string) is str:
        g = graphviz.Source(dot_string)
    elif isinstance(dot_string, (graphviz.dot.Digraph, graphviz.dot.Graph)):
        g = dot_string
    g.format='png'
    g.filename = output_file_name
    g.directory = "C:/Users/ydy1412/Desktop/pygame/"
    g.render(view=True)
    return g

with open("winner's network",'r') as f:
    string = f.read()
    print(string)
    save_graph_as_svg(string,"winner's network images")