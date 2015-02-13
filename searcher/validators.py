from django.core.exceptions import ValidationError
from searcher import models


def entrez_id_validator(value):
    if len(value) > models.ENTREZ_ID_MAX_LENGTH:
        raise ValidationError('Entrez id {} is too long.'.format(value))


def refseq_id_validator(value):
    if len(value) > models.REFSEQ_ID_MAX_LENGTH:
        raise ValidationError('RefSeq id {} is too long.'.format(value))


def symbol_id_validator(value):
    if len(value) > models.SYMBOL_ID_MAX_LENGTH:
        raise ValidationError('Symbol id {} is too long.'.format(value))