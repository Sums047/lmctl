import unittest
from pydantic import ValidationError
from lmctl.environment import EnvironmentGroup, TNCOEnvironment, ArmEnvironment

class TestEnvironmentGroup(unittest.TestCase):

    def test_init_without_name_fails(self):
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name=None, description=None)
        print("*************seeeeee", str(context.exception).split('[type=string_type')[0].strip())
        self.assertEqual(str(context.exception).split('[type=string_type')[0].strip(), '1 validation error for EnvironmentGroup\nname\n  Input should be a valid string')
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name=' ', description=None)
        print("*********eeeeeeeewwwwww", str(context.exception).split('[type=type=string_too_short')[0].strip())
        self.assertEqual(str(context.exception).split('[type=string_too_short')[0].strip(), '1 validation error for EnvironmentGroup\nname\n  String should have at least 1 character')
        
    def test_init_with_invalid_tnco_config_type_fails(self):
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name='test', description=None, tnco='tnco')
        self.assertEqual(str(context.exception).split('[type=string_type')[0].strip(), '1 validation error for EnvironmentGroup\ntnco\n  instance of TNCOEnvironment, tuple or dict expected (type=type_error.dataclass; class_name=TNCOEnvironment)')

    def test_init_with_invalid_arm_config_type_fails(self):
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name='test', description=None, tnco=None, arms='arms')
        self.assertEqual(str(context.exception).split('[type=string_type')[0].strip(), '1 validation error for EnvironmentGroup\narms\n  value is not a valid dict (type=type_error.dict)')
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name='test', description=None, tnco=None, arms={'arm': 'test'})
        self.assertEqual(str(context.exception).split('[type=string_type')[0].strip(), '1 validation error for EnvironmentGroup\narms -> arm\n  instance of ArmEnvironment, tuple or dict expected (type=type_error.dataclass; class_name=ArmEnvironment)')

