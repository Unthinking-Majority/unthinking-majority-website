from django.core.management.base import BaseCommand, CommandError
from django.db.models import ManyToOneRel, ManyToManyRel, OneToOneRel

from account import models


def update_reverse_references(obj, new_obj, exclude=None):
    """
    Update all references to obj with new_obj in database by traversing reverse relations of obj.__class__.
    Handles ForeignKey, m2m, and o2o references to obj.
    """

    if exclude is None:
        exclude = []
    else:
        exclude = [field.lower() for field in exclude]

    fields = [
        field
        for field in obj._meta.get_fields()
        if field.__class__ in (ManyToOneRel, ManyToManyRel, OneToOneRel)
        and field.related_model.__name__.lower() not in exclude
    ]

    for field in fields:
        related_model = field.related_model
        related_field_name = field.field.name
        related_objects = related_model.objects.filter(**{related_field_name: obj.id})
        if field.__class__ is ManyToOneRel:
            for related_obj in related_objects:
                setattr(related_obj, related_field_name, new_obj)
                related_obj.save()
        elif field.__class__ in (ManyToManyRel, OneToOneRel):
            for related_obj in related_objects:
                m2m_field = getattr(related_obj, related_field_name)
                m2m_field.add(new_obj)
                m2m_field.remove(obj)
                related_obj.save()


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("main_account", type=str)
        parser.add_argument("other_accounts", nargs="+", type=str)

    def handle(self, *args, **options):
        try:
            main_account = models.Account.objects.get(name=options["main_account"])
        except models.Account.DoesNotExist:
            raise CommandError(f"No account found with name: {options['main_account']}")
        for account_name in options["other_accounts"]:
            try:
                other_account = models.Account.objects.get(name=account_name)
            except models.Account.DoesNotExist:
                raise CommandError(f"No account found with name: {account_name}")
            update_reverse_references(other_account, main_account, exclude=["hiscores"])
            other_account.delete()
