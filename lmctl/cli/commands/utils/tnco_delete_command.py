import click
from typing import Dict, Any, Sequence, Callable
from .identifier import Identifier, determine_identifier, strip_identifiers
from .ignore_missing import IgnoreMissingSafetyNet, DisableIgnoreMissingSafetyNet, tnco_missing_detector
from .tnco_env_command import TNCOEnvironmentCommand
from .constraint import mutually_exclusive
from lmctl.cli.controller import get_global_controller
from lmctl.cli.arguments import FileInputOption, IgnoreMissingOption

__all__ = (
    'TNCODeleteCommand',
)

class TNCODeleteCommand(TNCOEnvironmentCommand):
    
    def __init__(self, 
                type_display_name: str, 
                *args, 
                identifiers: Sequence[Identifier] = None,
                identifier_required: bool = True,
                result_prefix: str = 'Removed: ', 
                additional_help: str = None,
                missing_detector: Callable = tnco_missing_detector,
                allow_file_input: bool = True,
                **kwargs
            ):
        self.type_display_name = type_display_name
        self.identifiers = identifiers
        self.identifier_required = identifier_required
        self.result_prefix = result_prefix
        self.additional_help = additional_help
        self.missing_detector = missing_detector
        self.allow_file_input = allow_file_input
        if 'help' not in kwargs or kwargs['help'] is None:
            kwargs['help'] = self._build_help()
        if 'short_help' not in kwargs or kwargs['short_help'] is None:
            kwargs['short_help'] = f'Delete a {self.type_display_name}'
        super().__init__(*args, **kwargs)
        if self.allow_file_input:
            file_input_option = FileInputOption()
            self.params.append(file_input_option)
        self.params.append(IgnoreMissingOption())

        self.delete_behaviour = self.callback
        self.callback = self._callback

        if len(self.identifiers) > 1 or (allow_file_input and len(self.identifiers) > 0):
            exclusive_params = [(i.param_name, i.get_cli_display_name()) for i in self.identifiers]
            if allow_file_input:
                exclusive_params.append((file_input_option.name, ','.join(file_input_option.opts)))
            self.callback = mutually_exclusive(*exclusive_params)(self.callback)


    def _callback(self, 
                    *args, 
                    environment_name: str = None,
                    pwd: str = None,
                    client_secret: str = None,
                    token: str = None,
                    file_content: Dict[str, Any] = None,
                    ignore_missing: bool = False,
                    **kwargs):
        identity = determine_identifier(self.identifiers, required=self.identifier_required, file_content=file_content, **kwargs)
        tnco_client = self._get_tnco_client(environment_name, pwd, client_secret, token)

        stripped_kwargs = strip_identifiers(self.identifiers, **kwargs)

        ignore_missing_safety_net = IgnoreMissingSafetyNet if ignore_missing else DisableIgnoreMissingSafetyNet

        with ignore_missing_safety_net(missing_detector=self.missing_detector) as ignore_missing_check:
            result = self.delete_behaviour(*args, tnco_client=tnco_client, identity=identity, **stripped_kwargs)
        
        io = get_global_controller().io

        if ignore_missing_check.is_missing:
            io.print(f'(Ignored) {ignore_missing_check.reason}')
        else:
            io = get_global_controller().io
            text = ''
            if self.result_prefix:
                text += str(self.result_prefix)
            text += str(result)
            io.print(text)

    def _build_help(self) -> str:
        help_msg = f'Delete a {self.type_display_name}'
        if self.identifiers is not None and len(self.identifiers) > 0:
            help_msg += '\n\n'
            help_msg += self._produce_identifer_str()
        if self.additional_help:
            help_msg += f'\n\n{self.additional_help}'
        return help_msg

    def _produce_identifer_str(self) -> str:
        identifiers_str = f'Identify the {self.type_display_name} to be deleted'

        if len(self.identifiers) == 1:
            identifiers_str += f' using the "{self.identifiers[0].get_cli_display_name()}" parameter'
        else:
            identifiers_str += ' using one paramter from [' + ', '.join([f'"{p.get_cli_display_name()}"' for p in self.identifiers]) + ']'

        attr_identifiers = [p for p in self.identifiers if p.obj_attribute is not None]
        if len(attr_identifiers) > 1:
            identifiers_str += f' or by including one of the following attributes'
            file_attr_str = ', '.join([f'"{p.obj_attribute}"' for p in attr_identifiers])
            identifiers_str += f' [{file_attr_str}] in the given object/file'
        elif len(attr_identifiers) == 1:
            identifiers_str += f' or by including the "{attr_identifiers[0].obj_attribute}" attribute in the given object/file'
        return identifiers_str
