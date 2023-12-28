from typing import TypeVar, Set, FrozenSet

from py_arg.abstract_argumentation.classes.abstract_argumentation_framework \
    import AbstractArgumentationFramework
from py_arg.abstract_argumentation.classes.argument import Argument
from py_arg.abstract_argumentation.semantics.get_admissible_sets \
    import get_admissible_sets
from py_arg.abstract_argumentation.semantics.get_complete_extensions import \
    get_complete_extensions
from py_arg.abstract_argumentation.semantics.get_conflict_free_extensions \
    import get_conflict_free_extensions
from py_arg.abstract_argumentation.semantics.get_eager_extension \
    import get_eager_extensions
from py_arg.abstract_argumentation.semantics.get_grounded_extension \
    import get_grounded_extensions
from py_arg.abstract_argumentation.semantics.get_ideal_extension \
    import get_ideal_extensions
from py_arg.abstract_argumentation.semantics.get_naive_extensions import \
    get_naive_extensions
from py_arg.abstract_argumentation.semantics.get_preferred_extensions import \
    get_preferred_extensions
from py_arg.abstract_argumentation.semantics.get_semistable_extensions \
    import get_semi_stable_extensions
from py_arg.abstract_argumentation.semantics.get_stable_extensions \
    import get_stable_extensions


T = TypeVar('T', bound=Argument)


def get_argumentation_framework_extensions(
        argumentation_framework: AbstractArgumentationFramework,
        semantics_specification: str) -> Set[FrozenSet[T]]:
    """
    Calculate the set of extensions from the given abstract argumentation
    framework and chosen semantics

    :param argumentation_framework: The abstract argumentation framework.
    :param semantics_specification: The chosen semantics.
    """
    if semantics_specification == 'Admissible':
        return get_admissible_sets(argumentation_framework)
    if semantics_specification == 'Complete':
        return get_complete_extensions(argumentation_framework)
    if semantics_specification == 'Grounded':
        return get_grounded_extensions(argumentation_framework)
    if semantics_specification == 'Preferred':
        return get_preferred_extensions(argumentation_framework)
    if semantics_specification == 'Ideal':
        return get_ideal_extensions(argumentation_framework)
    if semantics_specification == 'Stable':
        return get_stable_extensions(argumentation_framework)
    if semantics_specification == 'SemiStable':
        return get_semi_stable_extensions(argumentation_framework)
    if semantics_specification == 'Eager':
        return get_eager_extensions(argumentation_framework)
    if semantics_specification == 'ConflictFree':
        return get_conflict_free_extensions(argumentation_framework)
    if semantics_specification == 'Naive':
        return get_naive_extensions(argumentation_framework)
