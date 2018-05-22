from apistar.types import Type
from apistar.exceptions import ValidationError


class CoercingType(Type):

    def __init__(self, *args, **kwargs):
        definitions = None
        allow_coerce = True

        if args:
            assert len(args) == 1
            definitions = kwargs.pop('definitions', definitions)
            allow_coerce = kwargs.pop('allow_coerce', allow_coerce)
            assert not kwargs

            if args[0] is None or isinstance(args[0], (bool, int, float, list)):
                raise ValidationError('Must be an object.')

            elif isinstance(args[0], dict):
                # Instantiated with a dict.
                value = args[0]
            else:
                # Instantiated with an object instance.
                value = {
                    key: getattr(args[0], key)
                    for key in self.validator.properties.keys()
                }
        else:
            # Instantiated with keyword arguments.
            value = kwargs

        value = self.validator.validate(value, allow_coerce=allow_coerce)
        object.__setattr__(self, '_dict', value)
