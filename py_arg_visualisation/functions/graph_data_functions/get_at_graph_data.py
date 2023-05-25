from typing import List

from py_arg.aspic_classes.argumentation_theory import ArgumentationTheory
from py_arg_visualisation.functions.ordering_functions.get_ordering_by_specification \
    import get_ordering_by_specification


def get_argumentation_theory_graph_data(argumentation_theory: ArgumentationTheory, ordering_specification: str,
                                        selected_arguments: List[str]):
    """
    Calculate the data needed for the graphical representation of the argumentation theory and ordering

    :param argumentation_theory: The argumentation_theory that needs to be visualized.
    :param ordering_specification: The chosen ordering, combining both last/weakest link and democratic/elitist.
    :param selected_arguments: Arguments to be marked with a different color (e.g. because they are in some extension)
    """
    if selected_arguments and 'blue' in selected_arguments:
        blue = selected_arguments['blue']
    else:
        blue = []
    if selected_arguments and 'green' in selected_arguments:
        green = selected_arguments['green']
    else:
        green = []
    if selected_arguments and 'yellow' in selected_arguments:
        yellow = selected_arguments['yellow']
    else:
        yellow = []
    if selected_arguments and 'red' in selected_arguments:
        red = selected_arguments['red']
    else:
        red = []

    argument_long_str_to_id = {}
    data_nodes = []
    for argument_id, argument in enumerate(argumentation_theory.all_arguments):
        readable_id = 'A' + str(argument_id + 1)
        argument_long_str_to_id[argument.name] = readable_id
        if argument.name in blue:
            color = '#6DCDE3'
        elif argument.name in green:
            color = '#2ac2ab'
        elif argument.name in yellow:
            color = '#fff2cc'
        elif argument.name in red:
            color = '#e60c3f'
        else:
            color = '#AAAAAA'
        data_nodes.append({'id': readable_id, 'label': argument.short_name, 'color': color})

    ordering = get_ordering_by_specification(argumentation_theory, ordering_specification)
    data_edges = []
    for defeat in argumentation_theory.recompute_all_defeats(ordering):
        argument_a_id = argument_long_str_to_id[defeat.from_argument.name]
        argument_b_id = argument_long_str_to_id[defeat.to_argument.name]

        data_edges.append({'id': str(argument_a_id) + '-' + str(argument_b_id),
                           'from': argument_a_id, 'to': argument_b_id, 'arrows': 'to'})

    data = {'nodes': data_nodes, 'edges': data_edges}
    return data
