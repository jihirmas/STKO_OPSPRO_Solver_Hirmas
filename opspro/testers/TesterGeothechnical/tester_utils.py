from io import StringIO
import os
import platform
import subprocess


class TensorComponentData:
    STRESS = 1
    STRAIN = 2
    TESTED = 1
    FIXED = 2

    def __init__(self, control=STRAIN, type=FIXED, value=0.0):
        self.control = control
        self.type = type
        self.value = value


def list_to_tcl_buffer(data):
    buffer = StringIO()
    count = 0
    for value in data:
        count += 1
        buffer.write('{} '.format(value))
        if count == 10:
            buffer.write('\\\n')
            count = 0
    return buffer


def list_to_tcl_string(data):
    buffer = list_to_tcl_buffer(data)
    try:
        return buffer.getvalue()
    finally:
        buffer.close()


def get_tensor_from_tokens(strain_size, tokens):
    n = len(tokens)
    if strain_size == 3:
        if n >= 6:
            indices = [0, 1, 3]
            return [float(tokens[i]) for i in indices]
        if n >= 3:
            return [float(tokens[i]) for i in range(3)]
        raise ValueError('Wrong number of output components ({})'.format(n))
    if strain_size == 6 and n >= 6:
        return [float(tokens[i]) for i in range(6)]
    raise ValueError('Wrong number of strain size/components ({}/{})'.format(strain_size, n))


def parse_result_line(line, strain_size=6):
    if not line.startswith('__R__'):
        return None
    tokens = line[5:].split('|')
    if len(tokens) != 3:
        raise ValueError('Malformed tester result line: {}'.format(line))
    percentage = float(tokens[0])
    strain = get_tensor_from_tokens(strain_size, tokens[1].split())
    stress = get_tensor_from_tokens(strain_size, tokens[2].split())
    return percentage, strain, stress


def execute_async(command, working_dir):
    kwargs = {
        'shell': False,
        'stdout': subprocess.PIPE,
        'stderr': subprocess.STDOUT,
        'cwd': working_dir,
    }
    if platform.system() == 'Windows':
        kwargs['creationflags'] = 0x08000000

    process = subprocess.Popen(command, **kwargs)
    while process.poll() is None:
        raw_line = process.stdout.readline()
        if not raw_line:
            continue
        try:
            yield raw_line.decode(errors='replace').rstrip()
        except Exception:
            yield str(raw_line)

    output = process.communicate()[0]
    decoded_output = output.decode(errors='replace') if output else ''
    for line in decoded_output.splitlines():
        yield line
    if process.returncode != 0:
        raise RuntimeError('{} exited with code {}'.format(command, process.returncode))


def normalize_path(path):
    return os.path.abspath(path).replace('\\', '/')


def get_standard_tester_dir():
    try:
        from PyMpc import MpcStandardPaths

        base = MpcStandardPaths.getStandardPathDataLocation()
        return normalize_path(os.path.join(base, 'TesterGeotechnical'))
    except Exception:
        import tempfile

        return normalize_path(os.path.join(tempfile.gettempdir(), 'TesterGeotechnical'))
