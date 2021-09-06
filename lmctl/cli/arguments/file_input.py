import click
import os
from typing import Sequence, Any
from collections import OrderedDict
from lmctl.cli.format import InputFormat, JsonFormat, YamlFormat, BadFormatError

__all__ = (
    'FileInputOption',
    'file_input_option',
    'file_inputs_handler',
    'default_file_inputs_handler',
    'FileInputs'
)

JSON_VALUE = 'json'
YAML_VALUE = 'yaml'

default_param_decls = ['-f', '--file', 'file_content']

class FileInputOption(click.Option):

    def __init__(
            self, 
            param_decls: Sequence[str] = default_param_decls,
            help: str = 'Path to file representing the object data', 
            **kwargs):
        param_decls = [p for p in param_decls]

        self.formatters = {
            JSON_VALUE: JsonFormat(),
            YAML_VALUE: YamlFormat()
        }
        self.wrapped_callback = kwargs.pop('callback', None)

        super().__init__(
            param_decls,
            help=help,
            type=click.Path(exists=True),
            callback=self._callback,
            **kwargs
        )

    def _callback(self, ctx: click.Context, param: click.Parameter, value: Any):
        return_value = None
        if value is not None:
            with open(value) as f:
                content = f.read()
            failures = OrderedDict()
            for name, format_instance in self.formatters.items():
                try:
                    return_value = format_instance.read(content)
                except BadFormatError as e:
                    failures[name] = str(e)
            if return_value is None:
                error_msg = 'Failed to read content to supported formats: '
                for name, error in failures.items():
                    error_msg += f'\n\t{name}: {error}'
                raise click.BadParameter(error_msg, ctx=ctx, param=param)
        if self.wrapped_callback is not None:
            return self.wrapped_callback(return_value)
        else:
            return return_value


def file_input_option(*args, **kwargs):
    def decorator(f):
        param_decls = args
        if len(param_decls) == 0:
            param_decls = default_param_decls
        return click.option(*param_decls, cls=FileInputOption, **kwargs)(f)
    return decorator


class FileInputs:

    def __init__(self):
        self._formats = OrderedDict()

    @property
    def formats(self):
        return self._formats

    def add_format(self, name: str, format_instance: InputFormat) -> 'InputFormats':
        self._formats[name] = format_instance
        return self

    def _callback(self, ctx, param, value):
        if value is None:
            return None
        with open(value) as f:
            content = f.read()
        failures = OrderedDict()
        for name, format_instance in self._formats.items():
            try:
                return format_instance.read(content)
            except BadFormatError as e:
                failures[name] = str(e)
        error_msg = 'Failed to read content to supported formats: '
        for name, error in failures.items():
            error_msg += f'\n\t{name}: {error}'
        raise click.BadParameter(error_msg, ctx=ctx, param=param)

    def option(self, var_name: str = 'file_content', required: bool = False, 
                        help: str = 'Path to file representing the object', options: str = ['-f', '--file']):
        def decorator(f):
            return click.option(*options, var_name, 
                                help=help,
                                required=required,
                                type=click.Path(exists=True),
                                callback=self._callback
                            )(f)
        return decorator

def file_inputs_handler(**kwargs):
    return FileInputs(**kwargs)

def default_file_inputs_handler(**kwargs):
    return file_inputs_handler(**kwargs)\
        .add_format(YAML_VALUE, YamlFormat())\
        .add_format(JSON_VALUE, JsonFormat())

