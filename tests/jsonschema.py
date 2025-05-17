class ValidationError(Exception):
    pass

def validate(instance, schema):
    if schema.get('type') != 'object':
        raise ValidationError('Only object schemas supported')
    required = schema.get('required', [])
    for prop in required:
        if prop not in instance:
            raise ValidationError(f'Missing required property: {prop}')
    properties = schema.get('properties', {})
    for prop, rules in properties.items():
        if prop not in instance:
            continue
        value = instance[prop]
        allowed_types = rules.get('type')
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        type_ok = False
        for t in allowed_types:
            if t == 'string' and isinstance(value, str):
                type_ok = True
            if t == 'null' and value is None:
                type_ok = True
        if not type_ok:
            raise ValidationError(f'Property {prop} has invalid type {type(value)}')
        if rules.get('format') == 'uri' and value is not None:
            from urllib.parse import urlparse
            parsed = urlparse(value)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(f'Property {prop} is not a valid uri')
