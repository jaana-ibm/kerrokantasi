from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _


def generate_id():
    return get_random_string(32)


class BaseModel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=32,
        blank=True,
        help_text=_('You may leave this empty to automatically generate an ID')
    )
    created_at = models.DateTimeField(verbose_name=_('Time of creation'), default=timezone.now, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Created by'),
        null=True, blank=True, related_name="%(class)s_created",
        editable=False
    )
    modified_at = models.DateTimeField(verbose_name=_('Time of modification'), default=timezone.now, editable=False)
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Modified by'),
        null=True, blank=True, related_name="%(class)s_modified",
        editable=False
    )
    deleted = models.BooleanField(
        verbose_name=_('Deleted flag'), default=False, db_index=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        pk_type = self._meta.pk.get_internal_type()
        if pk_type == 'CharField':
            if not self.pk:
                self.pk = generate_id()
        elif pk_type == 'AutoField':
            pass
        else:
            raise Exception('Unsupported primary key field: %s' % pk_type)
        self.modified_at = timezone.now()
        super().save(*args, **kwargs)

    def soft_delete(self, using=None):
        self.deleted = True
        self.save(update_fields=("deleted",), using=using, force_update=True)

    def delete(self, using=None):
        raise NotImplementedError("This model does not support hard deletion")

    class Meta:
        abstract = True
