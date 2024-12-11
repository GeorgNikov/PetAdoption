from django.core.exceptions import ValidationError


def validate_letters_only(value):
    if not value.isalpha() :
        raise ValidationError(
            'This field can only contain letters!'
        )


def validate_type_user(value):
    allowed_values = ['Adopter', 'Shelter']
    if value not in allowed_values:
        raise ValidationError(f"Invalid user type: {value}. Must be 'Adopter' or 'Shelter'.")


# def validate_letters_and_spaces_only(value):
#     if not all(char.isalpha() or char.isspace() for char in value):
#         raise ValidationError(
#             'This field can only contain letters and spaces!'
#         )


def validate_organization_name(value):
    if not all(c.isalnum() or c.isspace() for c in value):
        raise ValidationError('This field must only contain letters, digits, and spaces.')


def validate_phone_number(value):
    if not all(c.isdigit() or c.isspace() or c in "()-" for c in value):
        raise ValidationError('Phone number must contain only digits, spaces, parentheses, and dashes.')
    if len(value) < 10 or len(value) > 13:
        raise ValidationError('Phone number must have at least 10 digits.')