import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.cayley_table_actions import CayleyTableActions

cayley_table = CayleyTableActions()
cayley_table.data = {
    "1": {"1": "1", "b": "b", "aa": "aa", "ba": "ba"},
    "b": {"1": "b", "b": "ba", "aa": "aa", "ba": "aa"},
    "aa": {"1": "aa", "b": "aa", "aa": "aa", "ba": "aa"},
    "ba": {"1": "ba", "b": "aa", "aa": "aa", "ba": "aa"},
}
# test = {
#     "1": {"1": "1", "a": "a", "aa": "aa", "ba": "ba"},
#     "a": {"1": "a", "a": "aa", "aa": "aa", "ba": "aa"},
#     "aa": {"1": "aa", "a": "aa", "aa": "aa", "ba": "aa"},
#     "ba": {"1": "ba", "a": "aa", "aa": "aa", "ba": "aa"},
# }
algebra = TransformationAlgebra(name="loaded_cayley_table_directly")
algebra.cayley_table_actions = cayley_table
algebra.check_properties()
algebra.print_properties(False)
