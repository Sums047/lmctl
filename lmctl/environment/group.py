from typing import Dict, Optional, Annotated

from pydantic.dataclasses import dataclass
from pydantic import constr, Field, StringConstraints

from lmctl.utils.dcutils.dc_capture import recordattrs

from .lmenv import TNCOEnvironment
from .armenv import ArmEnvironment

@recordattrs
@dataclass
class EnvironmentGroup:
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    description: Optional[str] = Field(default=None)
    tnco: Optional[TNCOEnvironment] = Field(default=None)
    arms: Optional[Dict[str, ArmEnvironment]] = Field(default_factory=dict)

    @property
    def lm(self):
        return self.tnco

    @property
    def has_lm(self):
        return self.has_tnco

    @property
    def has_tnco(self):
        return self.tnco is not None
