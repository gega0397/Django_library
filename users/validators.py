from django.core.exceptions import ValidationError

def validate_personal_number(value):
    check = all(char.isdigit() for char in str(value))
    if not check:
        raise ValidationError('Personal number must be a positive number.')
    if len(str(value)) != 11 and len(str(value)) != 8:
        raise ValidationError('Personal number must be 11 digits long for citizens and 8 digits long for companies')
