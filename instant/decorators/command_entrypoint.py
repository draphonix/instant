# import inspect

def command_entrypoint(params):
    def decorator(func):
        func._command_params = params
        return func
    return decorator