def import_module_with_exec(file_path):
    with open(file_path, 'r') as f:
        code = compile(f.read(), file_path, 'exec')
        module = {}
        exec(code, module)
    return module