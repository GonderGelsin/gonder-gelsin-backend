from django.db import models
from django.utils.translation import gettext_lazy as _

from authentication.models import CustomUser


class BillingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='billing_addresses')
    address_line_1 = models.CharField(_('address line 1'), max_length=255)
    address_line_2 = models.CharField(
        _('address line 2'), max_length=255, blank=True, null=True)
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100)
    is_default = models.BooleanField(_('default address'), default=False)

    def __str__(self):
        return f'{self.address_line_1}, {self.city}, {self.country}'

    class Meta:
        verbose_name = _('Billing Address')
        verbose_name_plural = _('Billing Addresses')
