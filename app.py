from functools import wraps
import importlib
import os
from typing import Any, Callable, List
from flask import stream_with_context, request, Flask
from datetime import datetime

app = Flask(__name__)


from typing import NamedTuple
class DecoratedFunctions(NamedTuple):
    func: Callable
    name: str
    labels: Any
    description: str

decorated_functions: List[DecoratedFunctions] = []

def format_dict(d: dict) -> str:
    """
    Convert a dictionary into a string of the format {key="value", key="value", ...}.
    
    Parameters:
    - d (dict): The dictionary to format.

    Returns:
    - str: A formatted string representing the dictionary.
    """


    if not d:
        return ""
    else:
        # Create a list of formatted key-value pairs
        formatted_pairs = [f'{key.lower()}="{value.lower()}"' for key, value in d.items()]
        
        # Join the pairs with commas and enclose in curly braces
        formatted_string = '{' + ', '.join(formatted_pairs) + '}'
        
        return formatted_string

def create_prometheus(value: float, name: str, labels: dict = {}, description = ""):
    return f"""
# HELP {name} {description}
# TYPE {name} gauge
{name.lower()}{format_dict(labels)} {value}
"""

# Define the decorator that accepts arguments
def metric(name, labels = {}, description = ""):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            """
            The decorated function is the (original) function where the wrapper is being put above 
            """
            # Example of using the arguments
            # print(f"arg1: {arg1}; arg2: {arg2}")
            # print(f"args: {args}")
            # print(f"kwargs: {kwargs}")
            
            # print(f"f: {f}")

            return f(*args, **kwargs)
            
        decorated_functions.append(
            DecoratedFunctions(
                func = decorated_function,
                name = name,
                labels=labels,
                description=description
            )
        )
        return decorated_function
    return decorator



@app.route('/metrics')
def get_metrics():
    def generate():
        start_time = datetime.now()
        
        yield "# Dynamic prometheus metrics generator\n"
        yield "# See: github.com/joepbuhre/script-collector\n"
        for fo in decorated_functions:
            result = create_prometheus(
                fo.func(), fo.name, fo.labels, fo.description
            )
            yield result
            

        diff = datetime.now() - start_time
        yield create_prometheus(
            value = round(diff.microseconds * 0.001, 5),
            name = "script_collector_total_time",
            description = "Total time it took to collect all metrics"
        )

    return app.response_class(stream_with_context(generate()),status=200, mimetype='text/plain')



def dynamic_import(directory: str):
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != '__init__.py':
            module_name = filename[:-3]
            module_path = os.path.join(directory, filename)
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

dynamic_import("metrics")

