import json
from typing import List, Dict

import dash
import dash_bootstrap_components as dbc
import visdcc
from dash import html, callback, Input, Output, State, ALL, dcc
from dash.exceptions import PreventUpdate

from py_arg.aba_classes.rule import Rule
from py_arg.aba_classes.aba_framework import ABAF
from py_arg.aba_classes.instantiated_argument import InstantiatedArgument
import py_arg_visualisation.functions.extensions_functions.get_accepted_assumptions as get_accepted_assumptions
import py_arg_visualisation.functions.extensions_functions.get_abaf_extensions as get_abaf_extensions
import py_arg_visualisation.functions.graph_data_functions.get_aba_graph_data as get_aba_graph_data


dash.register_page(__name__, name='Visualise ABA Framework', title='Visualise ABA Framework')


def get_aba_layout(abaf, aba_evaluation):
    left_column = dbc.Col(
        dbc.Accordion([
            dbc.AccordionItem(abaf, title='ABA Framework'),
            dbc.AccordionItem(aba_evaluation, title='Evaluation', item_id='23-ABA-Evaluation'),
        ], id='23-ABA-evaluation-accordion')
    )
    right_column = dbc.Col([
        dbc.Row([
            dbc.Card(visdcc.Network(data={'nodes': [], 'edges': []}, id='23-ABA-instantiated-graph',
                                    options={'height': '500px'}), body=True),
        ])
    ])
    return dbc.Row([left_column, right_column])


def get_aba_setting_specification_div():
    return html.Div(children=[
        dcc.Store(id='23-selected-argument-store-structured'),
        dbc.Col([
            dbc.Row(dbc.Button('Generate random', id='23-generate-random-arg-theory-button', n_clicks=0)),
            dbc.Row([
                dbc.Col([html.B('Atoms')]),
                dbc.Col([html.B('Rules')]),
            ]),
            dbc.Row([
                dbc.Col([dbc.Textarea(id='23-ABA-L',
                                      placeholder='Add ordinary atom per line. For example:\n a \n b \n p \n q',
                                      value='', style={'height': '200px'})]),
                dbc.Col([dbc.Textarea(id='23-ABA-R',
                                      placeholder='Add one rule per line. For example:\n p <- a, b \n q <- p',
                                      value='', style={'height': '200px'}), ]),
            ]),
            dbc.Row([
                dbc.Col([html.B('Assumptions')]),
                dbc.Col([html.B('Contraries')]),
            ]),
            dbc.Row([
                dbc.Col([dbc.Textarea(id='23-ABA-A',
                                      placeholder='Add one assumption per line. For example:\n a \n b',
                                      value='', style={'height': '200px'})]),
                dbc.Col([dbc.Textarea(id='23-ABA-C',
                                      placeholder='Add one assignment of a contrary per line. '
                                                  'For example:\n (a,p) \n (b,q)',
                                      value='', style={'height': '200px'}), ]),
            ]),
        ])
    ])


def get_aba_evaluation_specification_div():
    return html.Div([
        html.Div([
            dbc.Row([
                dbc.Col(html.B('Semantics')),
                dbc.Col(dbc.Select(options=[
                    {'label': 'Stable', 'value': 'Stable'},
                    {'label': 'Preferred', 'value': 'Preferred'},
                    {'label': 'Conflict-Free', 'value': 'Conflict-Free'},
                    {'label': 'Naive', 'value': 'Naive'},
                    {'label': 'Grounded', 'value': 'Grounded'},
                    {'label': 'Admissible', 'value': 'Admissible'},
                    {'label': 'Complete', 'value': 'Complete'},
                ],
                    value='Complete', id='23-ABA-evaluation-semantics')),
            ]),

            dbc.Row([
                dbc.Col(html.B('Evaluation Strategy')),
                dbc.Col(dbc.Select(
                    options=[
                        {'label': 'Credulous', 'value': 'Credulous'},
                        {'label': 'Skeptical', 'value': 'Skeptical'}
                    ],
                    value='Credulous', id='23-ABA-evaluation-strategy')),
            ]),
            dbc.Row(id='23-ABA-evaluation')
        ]),
    ])


layout = html.Div(
    children=[
        html.H1('Visualisation of ABA Frameworks'),
        get_aba_layout(get_aba_setting_specification_div(), get_aba_evaluation_specification_div())
    ]
)


@callback(
    Output('structured-argumentation-graph', 'data'),
    Input('ABA-L', 'value'),
    Input('ABA-R', 'value'),
    Input('ABA-A', 'value'),
    Input('ABA-C', 'value'),
    Input('selected-argument-store-structured', 'data'),
    State('color-blind-mode', 'on'),
    prevent_initial_call=True
)
def create_abaf(aba_l_str: str, aba_r_str: str, aba_a_str: str, aba_c_str: str,
                selected_arguments: Dict[str, List[str]], color_blind_mode: bool):
    # Read ABA
    l = {atom for atom in aba_l_str.replace(' ', '').replace('.', '').split('\n')}
    r = {Rule(r, set(r.split('<-')[2].split(',')), r.split('<-')[1])
         for r in aba_r_str.replace(' ', '').replace('.', '').split('\n')}
    a = {atom for atom in aba_a_str.replace(' ', '').replace('.', '').split('\n')}
    c = {}
    for con in aba_c_str.replace(' ', '').replace('.', '').replace('(', '').replace(')', '').split(','):
        c[con[1]] = con[2]

    abaf = ABAF(l, r, a, c)
    # Generate the graph data for this argumentation theory
    return get_aba_graph_data.apply(abaf, abaf.generate_af(), selected_arguments, color_blind_mode)


@callback(
    Output('ABA-evaluation', 'children'),
    State('ABA-L', 'value'),
    State('ABA-R', 'value'),
    State('ABA-A', 'value'),
    State('ABA-C', 'value'),
    Input('ABA-evaluation-accordion', 'active_item'),
    Input('ABA-evaluation-semantics', 'value'),
    Input('ABA-evaluation-strategy', 'value'),
    prevent_initial_call=True
)
def evaluate_abaf(aba_l_str: str, aba_r_str: str, aba_a_str: str, aba_c_str: str,
                  active_item: str, semantics_specification: str, acceptance_strategy_specification: str):
    if active_item != 'Evaluation':
        raise PreventUpdate

    # Read the argumentation theory
    try:
        # Read ABA
        l = {atom for atom in aba_l_str.replace(' ', '').replace('.', '').split('\n')}
        r = {Rule(r, set(r.split('<-')[2].split(',')), r.split('<-')[1])
             for r in aba_r_str.replace(' ', '').replace('.', '').split('\n')}
        a = {atom for atom in aba_a_str.replace(' ', '').replace('.', '').split('\n')}
        c = {}
        for con in aba_c_str.replace(' ', '').replace('.', '').replace('(', '').replace(')', '').split(','):
            c[con[1]] = con[2]

        abaf = ABAF(l, r, a, c)
    except ValueError:
        abaf = ABAF(set(), set(), set(), {})

    af = abaf.generate_af()
    extensions = get_abaf_extensions.apply(abaf, semantics_specification)
    accepted_assumptions = get_accepted_assumptions.apply(extensions, acceptance_strategy_specification)

    extension_buttons = []
    formula_arguments = af.arguments
    for extension in extensions:
        for argument in extension:
            assert isinstance(argument, InstantiatedArgument)
            accepted_formula = argument.conclusion
            formula_arguments[accepted_formula.s1].append(argument.name)

        out_arguments = {attacked for attacked in af.arguments
                         if any(argument in af.get_incoming_defeat_arguments(attacked)
                                for argument in extension)}
        undecided_arguments = {argument for argument in af.arguments
                               if argument not in extension and argument not in out_arguments}
        extension_readable_str = '{' + ', '.join(argument.short_name for argument in extension) + '}'

        extension_in_str = '+'.join(argument.name for argument in sorted(extension))
        extension_out_str = '+'.join(argument.name for argument in sorted(out_arguments))
        extension_undecided_str = '+'.join(argument.name for argument in sorted(undecided_arguments))
        extension_long_str = '|'.join([extension_in_str, extension_undecided_str, extension_out_str])
        extension_buttons.append(dbc.Button([extension_readable_str], color='secondary',
                                            id={'type': 'extension-button', 'index': extension_long_str}))

    accepted_assumptions_buttons = [dbc.Button(assumption.s1, color='secondary',
                                               id={'type': 'formula-button-structured',
                                                   'index': '+'.join(formula_arguments[assumption.s1])})
                                    for assumption in sorted(accepted_assumptions)]

    return [html.B('The extension(s):'),
            html.Div(extension_buttons),
            html.B('The accepted assumptions(s):'),
            html.Div(accepted_assumptions_buttons)]


@callback(
    Output('selected-argument-store-structured', 'data'),
    Input({'type': 'extension-button', 'index': ALL}, 'n_clicks'),
    Input({'type': 'formula-button-structured', 'index': ALL}, 'n_clicks'),
    State('selected-argument-store-structured', 'data'),
)
def mark_extension_in_graph(_nr_of_clicks_values_extension, _nr_of_clicks_values_formula,
                            old_selected_data: List[str]):
    button_clicked_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if button_clicked_id == '':
        return old_selected_data
    button_clicked_id_content = json.loads(button_clicked_id)
    button_clicked_id_type = button_clicked_id_content['type']
    button_clicked_id_index = button_clicked_id_content['index']
    if button_clicked_id_type == 'extension-button':
        in_part, undecided_part, out_part = button_clicked_id_index.split('|', 3)
        return {'green': in_part.split('+'), 'yellow': undecided_part.split('+'), 'red': out_part.split('+')}
    elif button_clicked_id_type == 'formula-button-structured':
        return {'blue': button_clicked_id_index.split('+')}
    return []
