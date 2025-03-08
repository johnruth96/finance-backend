import calendar
from datetime import datetime, date

from colorfield.fields import ColorField
from dateutil.relativedelta import relativedelta
from django.db import models

CATEGORY_COLOR_FACTOR = 1.1
CATEGORY_FALLBACK_COLOR = "#fafafa"

PAYMENT_CYCLES = [
    {
        "name": "monatlich",
        "value": "m",
        "months": 1,
    },
    {
        "name": "quartalsweise",
        "value": "q",
        "months": 3,
    },
    {
        "name": "halbjährlich",
        "value": "h",
        "months": 6,
    },
    {
        "name": "jährlich",
        "value": "y",
        "months": 12,
    },
]


def get_cycle_months(payment_cycle: str) -> int:
    try:
        return next(cycle["months"] for cycle in PAYMENT_CYCLES if cycle["value"] == payment_cycle)
    except StopIteration:
        raise ValueError(f"Payment cycle with value {payment_cycle} does not exist.")


def get_payment_cycle_choices():
    return [(cycle["value"], cycle["name"]) for cycle in PAYMENT_CYCLES]


# TODO: Add user
class Category(models.Model):
    name = models.CharField(verbose_name="Name", max_length=255, unique=True)
    color = ColorField(null=True)
    parent = models.ForeignKey('Category', models.PROTECT, null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"

    def __str__(self):
        return self.name

    def get_color(self):
        if self.color:
            return self.color
        elif self.parent:
            parent_color = self.parent.get_color()
            rgb = [int(parent_color[1:3], 16), int(parent_color[3:5], 16), int(parent_color[5:7], 16)]
            rgb = [int(x * CATEGORY_COLOR_FACTOR) if x * CATEGORY_COLOR_FACTOR <= 255 else 255 for x in rgb]
            color = "#" + "".join("{0:02x}".format(x) for x in rgb)
            return color
        else:
            return CATEGORY_FALLBACK_COLOR

    def get_level(self):
        if self.parent is None:
            return 0
        else:
            return 1 + self.parent.get_level()

    def subtree(self):
        children = list(Category.objects.filter(parent=self))
        descendants = []
        for c in children:
            descendants.extend(c.subtree())
        return [self] + descendants


# TODO: Add user
class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = (
        ("Girokonto", "Girokonto"),
        ("Tagesgeldkonto", "Tagesgeldkonto"),
        ("Sparkonto", "Sparkonto"),
        ("Depot", "Depot"),
    )

    name = models.CharField(verbose_name="Name", max_length=255)
    type = models.CharField(max_length=255, choices=ACCOUNT_TYPE_CHOICES)
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.name


# TODO: Add user
class Record(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)

    account = models.ForeignKey('Account', models.PROTECT)
    counter_booking = models.OneToOneField('Record', models.PROTECT, null=True, blank=True)

    subject = models.CharField(verbose_name="Name", max_length=255)
    category = models.ForeignKey('Category', models.PROTECT, verbose_name="Kategorie")
    date = models.DateField(verbose_name="Datum")
    amount = models.FloatField(verbose_name="Betrag")

    contract = models.ForeignKey('Contract', models.PROTECT, verbose_name="Vertrag", null=True, blank=True)

    class Meta:
        ordering = ['-date', 'category']
        verbose_name = "Buchung"
        verbose_name_plural = "Buchungen"

    def __str__(self):
        return self.subject

    def __lt__(self, other):
        return self.date < other.date or (self.date == other.date and self.subject < other.subject)


# TODO: Add user
class Contract(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    # Contract information
    date_start = models.DateField(verbose_name="Vertragsstart")
    cancelation_period = models.PositiveIntegerField(verbose_name="Kündigungsfrist (in Monaten)", null=True, blank=True)
    minimum_duration = models.PositiveIntegerField(verbose_name="Mindestlaufzeit (in Monaten)", null=True, blank=True)
    renewal_duration = models.PositiveIntegerField(verbose_name="Verlängerung (in Monaten)", null=True, blank=True)

    # Payment information
    account = models.ForeignKey('Account', models.PROTECT)
    amount = models.FloatField(verbose_name="Betrag")
    payment_date = models.DateField(verbose_name="regulärer Abbuchungstag", null=True)  # TODO: Remove null
    payment_cycle = models.CharField(verbose_name="Turnus", choices=get_payment_cycle_choices(), max_length=4)
    category = models.ForeignKey('Category', models.PROTECT, verbose_name="Kategorie")

    def get_next_payment_date(self):
        today = datetime.now()
        months = get_cycle_months(self.payment_cycle)
        match_month = (today.month - self.payment_date.month) % months == 0
        match_day = today.day >= self.payment_date.day

        if not match_month or not match_day:
            return None

        try:
            # Get payment date in current month
            return date(today.year, today.month, self.payment_date.day)
        except ValueError:
            # If the payment day is after the months end (e.g., February has only 28 days and payment day is 31)
            last_day = calendar.monthrange(today.year, today.month)[1]
            return date(today.year, today.month, last_day)

    def get_amount_yearly(self):
        months = get_cycle_months(self.payment_cycle)
        return self.amount * (12 / months)

    def is_cancelation_shortly(self):
        next_cancelation = self.get_next_cancelation_date()

        if next_cancelation is None:
            return False

        return next_cancelation < datetime.now().date() + relativedelta(months=1)

    def get_next_extension_date(self):
        if not self.minimum_duration or not self.renewal_duration:
            return None

        # Compute first extension date
        extension_date = self.date_start + relativedelta(months=self.minimum_duration)

        # Find extension date after now
        while extension_date < datetime.now().date():
            extension_date += relativedelta(months=self.renewal_duration)

        return extension_date

    def get_next_cancelation_date(self):
        next_extension_date = self.get_next_extension_date()

        if next_extension_date is None:
            return None

        notice_period = dict(days=1)
        if self.cancelation_period:
            notice_period.update(months=self.cancelation_period)

        return next_extension_date - relativedelta(**notice_period)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vertrag"
        verbose_name_plural = "Verträge"
        ordering = ['name']
