from graphql import GraphQLError


def validate_length(value, field_name, min_length, max_length):
    if min_length <= len(value) <= max_length:
        raise GraphQLError('{} length error'.format(field_name))

    return True


def validate_digital_values(value, field_name):
    if not value.isdigit():
        raise GraphQLError('{} contains no digit character(s)'.format(field_name))

    return True


def validate_last4digit(last4digit):
    field_name = 'last4digit'
    validate_length(last4digit, field_name, 4, 4)
    validate_digital_values(last4digit, field_name)

    return True


def validate_code(code):
    field_name = 'code'
    validate_length(code, field_name, 3, 4)
    validate_digital_values(code, field_name)

    return True


def validate_login(login):
    validate_length(login, 'login', 6, 128)

    return True