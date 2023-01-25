from typing import List

import dash
from dash import html, callback, Input, Output, State
from dash.exceptions import PreventUpdate

from py_arg.generators.abstract_argumentation_framework_generators.abstract_argumentation_framework_generator import \
    AbstractArgumentationFrameworkGenerator
from py_arg_visualisation.functions.explanations_functions.explanation_function_options import \
    EXPLANATION_FUNCTION_OPTIONS
from py_arg_visualisation.functions.explanations_functions.get_af_explanations import \
    get_argumentation_framework_explanations
from py_arg_visualisation.functions.extensions_functions.get_af_extensions import get_argumentation_framework_extensions
from py_arg_visualisation.functions.graph_data_functions.get_af_graph_data import get_argumentation_framework_graph_data
from py_arg_visualisation.functions.import_functions.read_argumentation_framework_functions import \
    read_argumentation_framework
from py_arg_visualisation.layout_elements.abstract_argumentation_layout_elements import get_abstract_setting, \
    get_abstract_evaluation, get_abstract_explanation, get_abstract_layout

dash.register_page(__name__)

abstract_setting = get_abstract_setting()
abstract_evaluation = get_abstract_evaluation()
abstract_explanation = get_abstract_explanation()
layout_abstract = get_abstract_layout(abstract_evaluation, abstract_explanation, abstract_setting)
layout = html.Div(
    children=[
        html.H1('Visualisation of abstract argumentation frameworks'),
        layout_abstract
    ]
)


@callback(
    Output('abstract-arg-setting-collapse', 'is_open'),
    [Input('abstract-arg-setting-button', 'n_clicks')],
    [State('abstract-arg-setting-collapse', 'is_open')],
)
def toggle_collapse(n: int, is_open: bool):
    if n:
        return not is_open
    return is_open


@callback(
    Output('abstract-evaluation-collapse', 'is_open'),
    [Input('abstract-evaluation-button', 'n_clicks')],
    [State('abstract-evaluation-collapse', 'is_open')],
)
def toggle_collapse(n: int, is_open: bool):
    if n:
        return not is_open
    return is_open


@callback(
    Output('abstract-explanation-collapse', 'is_open'),
    [Input('abstract-explanation-button', 'n_clicks')],
    [State('abstract-explanation-collapse', 'is_open')],
)
def toggle_collapse(n: int, is_open: bool):
    if n:
        return not is_open
    return is_open


@callback(
    Output('abstract-explanation-function', 'options'),
    [Input('abstract-explanation-type', 'value')],
    prevent_initial_call=True
)
def setting_choice(choice: str):
    return [{'label': i, 'value': i} for i in EXPLANATION_FUNCTION_OPTIONS[choice]]


@callback(
    Output('abstract-arguments', 'value'),
    Output('abstract-attacks', 'value'),
    Input('generate-random-af-button', 'n_clicks')
)
def generate_abstract_argumentation_framework(nr_of_clicks: int):
    if nr_of_clicks > 0:
        random_af = AbstractArgumentationFrameworkGenerator(8, 8, True).generate()
        abstract_arguments_value = '\n'.join((str(arg) for arg in random_af.arguments))
        abstract_attacks_value = '\n'.join((f'({str(defeat.from_argument)},{str(defeat.to_argument)})'
                                            for defeat in random_af.defeats))
        return abstract_arguments_value, abstract_attacks_value
    return '', ''


@callback(
    Output('abstract-arguments-output', 'children'),
    Output('abstract-argumentation-graph', 'data'),
    Input('create-argumentation-framework-button', 'n_clicks'),
    State('abstract-arguments', 'value'),
    State('abstract-attacks', 'value'),
    Input('selected-argument-store-abstract', 'data'),
    prevent_initial_call=True
)
def create_abstract_argumentation_framework(_nr_of_clicks: int, arguments: str, attacks: str,
                                            selected_arguments: List[str]):
    arg_framework = read_argumentation_framework(arguments, attacks)
    data = get_argumentation_framework_graph_data(arg_framework, selected_arguments)
    return html.Div([html.H4('The arguments of the AF:'),
                     html.Ul([html.Li(argument.name) for argument in arg_framework.arguments])]), data


@callback(
    Output('abstract-evaluation', 'children'),
    Input('evaluate-argumentation-framework-button', 'n_clicks'),
    State('abstract-arguments', 'value'),
    State('abstract-attacks', 'value'),
    State('abstract-evaluation-semantics', 'value'),
    State('abstract-evaluation-strategy', 'value'),
    prevent_initial_call=True
)
def evaluate_abstract_argumentation_framework(_nr_of_clicks: int, arguments: str, attacks: str, semantics: str,
                                              strategy: str):
    arg_framework = read_argumentation_framework(arguments, attacks)
    frozen_extensions = get_argumentation_framework_extensions(arg_framework, semantics)
    extensions = [set(frozen_extension) for frozen_extension in frozen_extensions]
    if strategy == 'Skeptical':
        accepted = set.intersection(*extensions)
    elif strategy == 'Credulous':
        accepted = set.union(*extensions)
    else:
        raise NotImplementedError

    extension_list_items = []
    for extension in extensions:
        extension_readable_str = '{' + ', '.join(argument.name for argument in extension) + '}'
        extension_long_str = '+'.join(argument.name for argument in extension)
        extension_with_link = html.A(children=extension_readable_str,
                                     id={'type': 'extension-button-abstract', 'index': extension_long_str})
        extension_list_items.append(html.Li(extension_with_link))

    return html.Div([html.H4('The extension(s):'),
                     html.Ul(extension_list_items),
                     html.H4('The accepted argument(s):'),
                     html.Ul([html.Li(argument.name) for argument in accepted])
                     ])


@callback(
    Output('abstract-explanation', 'children'),
    Input('abstract-explanation-button', 'n_clicks'),
    State('abstract-arguments', 'value'),
    State('abstract-attacks', 'value'),
    State('abstract-evaluation-semantics', 'value'),
    State('abstract-explanation-function', 'value'),
    State('abstract-explanation-type', 'value'),
    State('abstract-explanation-strategy', 'value'),
    prevent_initial_call=True
)
def derive_explanations_abstract_argumentation_framework(_nr_of_clicks: int, arguments: str, attacks: str,
                                                         semantics: str, explanation_function: str,
                                                         explanation_type: str, explanation_strategy: str):
    if semantics == '':
        return html.Div([html.H4('Error', className='error'),
                         'Choose a semantics under "Evaluation" before deriving explanations.'])
    else:
        arg_framework = read_argumentation_framework(arguments, attacks)
        frozen_extensions = get_argumentation_framework_extensions(arg_framework, semantics)
        extensions = [set(frozen_extension) for frozen_extension in frozen_extensions]
        if explanation_strategy == 'Skeptical':
            accepted_arguments = set.intersection(*extensions)
        elif explanation_strategy == 'Credulous':
            accepted_arguments = set.union(*extensions)
        else:
            raise NotImplementedError

        explanations = get_argumentation_framework_explanations(
            arg_framework, semantics, extensions, accepted_arguments,
            explanation_function, explanation_type, explanation_strategy)

        return html.Div([html.H4('The explanation(s):'),
                         html.Ul([html.Li(str(explanation)) for explanation in explanations])])


@callback(
    Output('abstract-argumentation-graph-output', 'children'),
    Output('abstract-argumentation-graph-evaluation', 'children'),
    Output('abstract-argumentation-graph-explanation', 'children'),
    Input('abstract-argumentation-graph', 'selection'),
    State('abstract-arguments', 'value'),
    State('abstract-attacks', 'value'),
    State('abstract-evaluation-semantics', 'value'),
    State('abstract-evaluation-strategy', 'value'),
    State('abstract-explanation-function', 'value'),
    State('abstract-explanation-type', 'value'),
    prevent_initial_call=True
)
def handle_selection_in_abstract_argumentation_graph(selection, arguments, attacks, semantics, strategy, function,
                                                     explanation_type):
    while selection is not None:
        arg_framework = read_argumentation_framework(arguments, attacks)
        for arg in arg_framework.arguments:
            if str(arg) == str(selection['nodes'][0]):
                argument = arg
        arg_ext = []
        output_arg = html.Div(
            [html.H4('The selected argument:'), html.H6('{}'.format(str(argument)))])
        output_accept = ''
        explanation_output = ''
        output_evaluation = ''
        if semantics != '':
            frozen_extensions = get_argumentation_framework_extensions(arg_framework, semantics)
            if strategy != '':
                skeptically_accepted = False
                credulously_accepted = False
                if semantics != 'Grounded':
                    extensions = [set(frozen_extension) for frozen_extension in frozen_extensions]
                    skeptically_accepted_arguments = set.intersection(*extensions)
                    credulously_accepted_arguments = set.union(*extensions)
                    for ext in extensions:
                        if argument in ext:
                            arg_ext.append(ext)
                    if arg_ext == extensions:
                        skeptically_accepted = True
                    if arg_ext:
                        credulously_accepted = True
                elif semantics == 'Grounded':
                    extensions = frozen_extensions
                    if argument in extensions:
                        arg_ext.append(extensions)
                        skeptically_accepted_arguments = extensions
                        credulously_accepted_arguments = extensions
                        skeptically_accepted = True
                        credulously_accepted = True
                if skeptically_accepted:
                    output_accept += str(argument) + ' is skeptically and credulously accepted.'
                    if function is not None and explanation_type == 'Acceptance':
                        skeptical_explanation = get_argumentation_framework_explanations(
                            arg_framework, semantics, extensions, skeptically_accepted_arguments,
                            function, explanation_type, 'Skeptical')
                        credulous_explanation = get_argumentation_framework_explanations(
                            arg_framework, semantics, extensions, credulously_accepted_arguments,
                            function, explanation_type, 'Credulous')
                        explanation_output = html.Div([html.H4(
                            'The skeptical acceptance explanation for {}:'.format(str(argument))),
                            html.H6('\n {}'.format(
                                str(skeptical_explanation.get(str(argument))).replace('set()', '{}'))), html.H4(
                                'The credulous acceptance explanation for {}:'.format(str(argument))),
                            html.H6('\n {}'.format(
                                str(credulous_explanation.get(str(argument))).replace('set()', '{}')))])
                    elif function is not None and explanation_type == 'NonAcceptance':
                        explanation_output = html.Div(
                            [html.H4('Error', className='error'),
                             'There is no non-acceptance explanation for argument {}, since it is '
                             'skeptically accepted.'.format(argument)])
                elif credulously_accepted:
                    output_accept += str(argument) + ' is credulously but not skeptically accepted.'
                    if function is not None and explanation_type == 'Acceptance':
                        credulous_explanation = get_argumentation_framework_explanations(
                            arg_framework, semantics, extensions, credulously_accepted_arguments,
                            function, explanation_type, 'Credulous')
                        explanation_output = html.Div(
                            [html.H4('The credulous acceptance explanation for {}:'.format(str(argument))),
                             html.H6('\n {}'.format(
                                 str(credulous_explanation.get(str(argument))).replace('set()', '{}')))])
                    elif function is not None and explanation_type == 'NonAcceptance':
                        skeptical_explanation = get_argumentation_framework_explanations(
                            arg_framework, semantics, extensions, skeptically_accepted_arguments,
                            function, explanation_type, 'Skeptical')
                        explanation_output = html.Div(
                            [html.H4('The not skeptical acceptance explanation for {}:'.format(str(argument))),
                             html.H6('\n {}'.format(
                                 str(skeptical_explanation.get(str(argument))).replace('set()', '{}')))])
                elif not skeptically_accepted and not credulously_accepted:
                    output_accept += str(argument) + ' is neither  credulously nor skeptically accepted.'
                    if function is not None and explanation_type == 'NonAcceptance':
                        skeptical_explanation = get_argumentation_framework_explanations(
                            arg_framework, semantics, extensions, skeptically_accepted_arguments,
                            function, explanation_type, 'Skeptical')
                        credulous_explanation = get_argumentation_framework_explanations(
                            arg_framework, semantics, extensions, credulously_accepted_arguments,
                            function, explanation_type, 'Credulous')
                        explanation_output = html.Div([html.H4(
                            'The not skeptical acceptance explanation for {}:'.format(str(argument))),
                            html.H6('\n {}'.format(str(skeptical_explanation.get(str(argument))).replace('set()', '{}'))), html.H4(
                                'The not credulous acceptance explanation for {}:'.format(str(argument))),
                            html.H6('\n {}'.format(str(credulous_explanation.get(str(argument))).replace('set()', '{}')))])
                    elif function is not None and explanation_type == 'Acceptance':
                        explanation_output = html.Div(
                            [html.H4('Error', className='error'),
                             'There is no acceptance explanation for argument {}, since it is not '
                             'credulously accepted.'.format(argument)])
            output_evaluation = html.Div(
                [html.H4('The extensions with argument {}:'.format(str(argument))),
                 html.H6('{}'.format(arg_ext)), html.H6('{}'.format(output_accept))])
        return output_arg, output_evaluation, explanation_output
    raise PreventUpdate

