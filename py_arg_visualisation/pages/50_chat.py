import base64
import json
import random

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from py_arg.algorithms.relevance.relevance_lister import FourBoolRelevanceLister
from py_arg.algorithms.stability.stability_labeler import StabilityLabeler
from py_arg.import_export.argumentation_system_from_json_reader import ArgumentationSystemFromJsonReader
from py_arg.incomplete_aspic_classes.incomplete_argumentation_theory import IncompleteArgumentationTheory

dash.register_page(__name__, name='Inquiry Dialogue System', title='Inquiry Dialogue System')

layout = html.Div(
    [
        html.H1('Argumentation-based inquiry dialogue system'),
        html.B('Argumentation system'),
        dcc.Upload(dbc.Button('Upload argumentation system'), id='50-chat-as-upload'),
        html.B('Queryables'),
        dcc.Dropdown(multi=True, id='50-queryables-dropdown'),
        html.B('Topic'),
        dcc.Dropdown(id='50-topic-dropdown'),
        html.B('Knowledge base'),
        dcc.Dropdown(id='50-knowledge-base', multi=True),

        html.Br(),
        html.Br(),
        html.B('Topic stability status or next question'),
        html.P(id='50-stability-status')
    ]
)


@callback(
    Output('50-queryables-dropdown', 'options'),
    Output('50-topic-dropdown', 'options'),
    Input('50-chat-as-upload', 'contents')
)
def update_queryable_and_topic_options(argumentation_system_content):
    if not argumentation_system_content:
        raise PreventUpdate
    content_type, content_str = argumentation_system_content.split(',')
    decoded = base64.b64decode(content_str)
    opened_as = ArgumentationSystemFromJsonReader().from_json(json.loads(decoded))
    pos_literals = [{'label': key, 'value': key}
                    for key, value in opened_as.language.items()
                    if value.is_positive]
    all_literals = [{'label': key, 'value': key} for key in opened_as.language.keys()]
    return pos_literals, all_literals


@callback(
    Output('50-knowledge-base', 'options'),
    Input('50-queryables-dropdown', 'value'),
    Input('50-knowledge-base', 'value'),
    State('50-chat-as-upload', 'contents')
)
def update_knowledge_base_options(queryables, current_value, argumentation_system_content):
    if not queryables:
        return []

    content_type, content_str = argumentation_system_content.split(',')
    decoded = base64.b64decode(content_str)
    opened_as = ArgumentationSystemFromJsonReader().from_json(json.loads(decoded))

    result = set()
    for queryable in queryables:
        queryable_literal = opened_as.language[queryable]
        contradictories = [contra
                           for contra in queryable_literal.contraries_and_contradictories]
        if not current_value or all(contra.s1 not in current_value
                                    for contra in contradictories):
            result.add(queryable)
            for contradictory in contradictories:
                contra_contradictories = \
                    [contra_contra
                     for contra_contra in contradictory.contraries_and_contradictories]
                if not current_value or \
                        all(contra_contra.s1 not in current_value
                            for contra_contra in contra_contradictories):
                    result.add(contradictory.s1)
    return [{'label': lit, 'value': lit} for lit in result]


@callback(
    Output('50-stability-status', 'children'),
    State('50-queryables-dropdown', 'value'),
    Input('50-knowledge-base', 'value'),
    State('50-chat-as-upload', 'contents'),
    State('50-topic-dropdown', 'value')
)
def update_knowledge_base_options(queryables, knowledge_base,
                                  argumentation_system_content, topic_str):
    if not queryables or not topic_str:
        return ''

    content_type, content_str = argumentation_system_content.split(',')
    decoded = base64.b64decode(content_str)
    opened_as = ArgumentationSystemFromJsonReader().from_json(json.loads(decoded))

    incomplete_argumentation_theory = IncompleteArgumentationTheory(
        argumentation_system=opened_as,
        queryables=[opened_as.language[q] for q in queryables],
        knowledge_base_axioms=[opened_as.language[k] for k in knowledge_base],
        knowledge_base_ordinary_premises=[]
    )

    stability_labeler_labels = StabilityLabeler().label(incomplete_argumentation_theory)
    topic_literal = opened_as.language[topic_str]
    topic_label = stability_labeler_labels.literal_labeling[topic_literal]
    if topic_label.is_stable:
        return 'Yes, it is ' + topic_label.stability_str + '.'

    relevance_lister = FourBoolRelevanceLister()
    relevance_lister.update(incomplete_argumentation_theory, stability_labeler_labels)
    questions = relevance_lister.relevance_list[topic_literal]
    random_question = random.choice(list(questions))
    return 'No, it is not stable yet. Do you know something about ' + random_question.s1 + '?'
