import json
from typing import List, Dict

import dash
from dash import html, callback, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import AbstractArgumentationFramework
from py_arg.generators.abstract_argumentation_framework_generators.abstract_argumentation_framework_generator import \
    AbstractArgumentationFrameworkGenerator
from py_arg_visualisation.functions.explanations_functions.explanation_function_options import \
    EXPLANATION_FUNCTION_OPTIONS
from py_arg_visualisation.functions.explanations_functions.get_af_explanations import \
    get_argumentation_framework_explanations
from py_arg_visualisation.functions.extensions_functions.get_accepted_arguments import get_accepted_arguments
from py_arg_visualisation.functions.extensions_functions.get_af_extensions import get_argumentation_framework_extensions
from py_arg_visualisation.functions.graph_data_functions.get_af_graph_data import get_argumentation_framework_graph_data
from py_arg_visualisation.functions.import_functions.read_argumentation_framework_functions import \
    read_argumentation_framework
from py_arg_visualisation.layout_elements.abstract_argumentation_layout_elements import \
    get_abstract_setting_specification_div, get_abstract_evaluation_div, get_abstract_explanation_div, \
    get_abstract_layout

dash.register_page(__name__, name='Visualise AF', title='Visualise AF')

# Create layout elements and compose them into the layout for this page.
abstract_setting = get_abstract_setting_specification_div()
abstract_evaluation = get_abstract_evaluation_div()
abstract_explanation = get_abstract_explanation_div()
layout = get_abstract_layout(abstract_evaluation, abstract_explanation, abstract_setting)


@callback(
    Output('abstract-arguments', 'value'),
    Output('abstract-attacks', 'value'),
    Input('generate-random-af-button', 'n_clicks')
)
def generate_abstract_argumentation_framework(nr_of_clicks: int):
    """
    Generate a random AF after clicking the button and put the result in the text box.
    """
    if nr_of_clicks > 0:
        random_af = AbstractArgumentationFrameworkGenerator(8, 8, True).generate()
        abstract_arguments_value = '\n'.join((str(arg) for arg in random_af.arguments))
        abstract_attacks_value = '\n'.join((f'({str(defeat.from_argument)},{str(defeat.to_argument)})'
                                            for defeat in random_af.defeats))
        return abstract_arguments_value, abstract_attacks_value
    return '', ''


@callback(
    Output('abstract-argumentation-graph', 'data'),
    Input('abstract-arguments', 'value'),
    Input('abstract-attacks', 'value'),
    Input('selected-argument-store-abstract', 'data'),
    prevent_initial_call=True
)
def create_abstract_argumentation_framework(arguments: str, attacks: str,
                                            selected_arguments: Dict[str, List[str]]):
    """
    Send the AF data to the graph for plotting.
    """
    try:
        arg_framework = read_argumentation_framework(arguments, attacks)
    except ValueError:
        arg_framework = AbstractArgumentationFramework()

    if dash.callback_context.triggered_id != 'selected-argument-store-abstract':
        selected_arguments = None

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
    data = get_argumentation_framework_graph_data(arg_framework, blue, green, yellow, red)
    return data


@callback(
    Output('abstract-evaluation', 'children'),
    State('abstract-arguments', 'value'),
    State('abstract-attacks', 'value'),
    Input('abstract-evaluation-accordion', 'active_item'),
    Input('abstract-evaluation-semantics', 'value'),
    Input('abstract-evaluation-strategy', 'value'),
    prevent_initial_call=True
)
def evaluate_abstract_argumentation_framework(arguments: str, attacks: str,
                                              active_item: str,
                                              semantics: str, strategy: str):
    if active_item != 'Evaluation':
        raise PreventUpdate

    # Read the abstract argumentation framework.
    arg_framework = read_argumentation_framework(arguments, attacks)

    # Compute the extensions and put them in a list of sets.
    frozen_extensions = get_argumentation_framework_extensions(arg_framework, semantics)
    extensions = [set(frozen_extension) for frozen_extension in frozen_extensions]

    # Make a button for each extension.
    extension_buttons = []
    for extension in sorted(extensions):
        out_arguments = {attacked for attacked in arg_framework.arguments
                         if any(argument in arg_framework.get_incoming_defeat_arguments(attacked)
                                for argument in extension)}
        undecided_arguments = {argument for argument in arg_framework.arguments
                               if argument not in extension and argument not in out_arguments}
        extension_readable_str = '{' + ', '.join(argument.name for argument in sorted(extension)) + '}'
        extension_in_str = '+'.join(argument.name for argument in sorted(extension))
        extension_out_str = '+'.join(argument.name for argument in sorted(out_arguments))
        extension_undecided_str = '+'.join(argument.name for argument in sorted(undecided_arguments))
        extension_long_str = '|'.join([extension_in_str, extension_undecided_str, extension_out_str])
        extension_buttons.append(dbc.Button([extension_readable_str], color='secondary',
                                            id={'type': 'extension-button-abstract', 'index': extension_long_str}))

    # Based on the extensions, get the acceptance status of arguments.
    accepted_arguments = get_accepted_arguments(extensions, strategy)

    # Make a button for each accepted argument.
    accepted_argument_buttons = [dbc.Button(argument.name, color='secondary', id={'type': 'argument-button-abstract',
                                                                                  'index': argument.name})
                                 for argument in sorted(accepted_arguments)]

    return html.Div([html.B('The extension(s):'), html.Div(extension_buttons),
                     html.B('The accepted argument(s):'), html.Div(accepted_argument_buttons),
                     html.P('Click on the extension/argument buttons to display the corresponding argument(s) '
                            'in the graph.')])


@callback(
    Output('selected-argument-store-abstract', 'data'),
    Input({'type': 'extension-button-abstract', 'index': ALL}, 'n_clicks'),
    Input({'type': 'argument-button-abstract', 'index': ALL}, 'n_clicks'),
    State('selected-argument-store-abstract', 'data'),
)
def mark_extension_or_argument_in_graph(_nr_of_clicks_extension_values, _nr_of_clicks_argument_values,
                                        old_selected_data: List[str]):
    button_clicked_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if button_clicked_id == '':
        return old_selected_data
    button_clicked_id_content = json.loads(button_clicked_id)
    button_clicked_id_type = button_clicked_id_content['type']
    button_clicked_id_index = button_clicked_id_content['index']
    if button_clicked_id_type == 'extension-button-abstract':
        in_part, undecided_part, out_part = button_clicked_id_index.split('|', 3)
        return {'green': in_part.split('+'), 'yellow': undecided_part.split('+'), 'red': out_part.split('+')}
    elif button_clicked_id_type == 'argument-button-abstract':
        return {'blue': [button_clicked_id_index]}
    return []


@callback(
    Output('abstract-explanation-function', 'options'),
    Output('abstract-explanation-function', 'value'),
    [Input('abstract-explanation-type', 'value')]
)
def setting_choice(choice: str):
    return EXPLANATION_FUNCTION_OPTIONS[choice], EXPLANATION_FUNCTION_OPTIONS[choice][0]['value']


@callback(
    Output('abstract-explanation', 'children'),
    Input('abstract-evaluation-accordion', 'active_item'),
    State('abstract-arguments', 'value'),
    State('abstract-attacks', 'value'),
    State('abstract-evaluation-semantics', 'value'),
    Input('abstract-explanation-function', 'value'),
    Input('abstract-explanation-type', 'value'),
    State('abstract-evaluation-strategy', 'value'),
    prevent_initial_call=True
)
def derive_explanations_abstract_argumentation_framework(active_item,
                                                         arguments: str, attacks: str,
                                                         semantics: str, explanation_function: str,
                                                         explanation_type: str, explanation_strategy: str):
    if active_item != 'Explanation':
        raise PreventUpdate

    # Compute the explanations based on the input.
    arg_framework = read_argumentation_framework(arguments, attacks)
    frozen_extensions = get_argumentation_framework_extensions(arg_framework, semantics)
    extensions = [set(frozen_extension) for frozen_extension in frozen_extensions]
    accepted_arguments = get_accepted_arguments(extensions, explanation_strategy)
    explanations = get_argumentation_framework_explanations(arg_framework, extensions, accepted_arguments,
                                                            explanation_function, explanation_type)

    # Print the explanations for each of the arguments.
    return html.Div([html.B('The explanation(s):')] +
                    [html.Div([
                        html.B(explanation_key),
                        html.Ul([html.Li(str(explanation_value)) for explanation_value in explanation_values])])
                     for explanation_key, explanation_values in explanations.items()])
