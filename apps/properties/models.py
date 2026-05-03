from django.db import models, transaction
from django.core.exceptions import ValidationError
import re


class Property(models.Model):
    # 🌟 NEW: Standardized choices for data consistency
    class PropertyType(models.TextChoices):
        FLAT = "Flat", "Flat"
        HOUSE = "House", "House"

    class PropertyStatus(models.TextChoices):
        AVAILABLE = "Available", "Available"
        RENTED = "Rented", "Rented"
        WITHDRAWN = "Withdrawn", "Withdrawn"

    property_no = models.CharField(max_length=10, primary_key=True, editable=False, blank=True)
    title = models.CharField(
        max_length=200,
        help_text="e.g. Stunning 2-Bed Flat in City Centre",
        default="A Property for Rent",
    )
    description = models.TextField(
        help_text="Full description of the property features and area.",
        default="A Property",
    )
    street = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)

    # 🌟 UPDATED: Apply choices
    property_type = models.CharField(max_length=50, choices=PropertyType.choices)
    no_of_rooms = models.IntegerField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=PropertyStatus.choices,
        default=PropertyStatus.AVAILABLE,
    )

    # Relationships
    # 🌟 UPDATED: Ensure only clients with the 'Owner' role can be assigned here
    owner_no = models.ForeignKey(
        "users.Client",
        on_delete=models.CASCADE,
        related_name="owned_properties",
        limit_choices_to={"role": "Owner"},
    )

    staff_no = models.ForeignKey(
        "users.Staff",
        on_delete=models.SET_NULL,
        null=True,
        related_name="managed_properties",
    )
    branch_no = models.ForeignKey(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="properties",
    )
    date_withdrawn = models.DateField(
        blank=True,
        null=True,
        help_text="Date the property was removed from the market.",
    )

    class Meta:
        verbose_name_plural = "Properties for Rent"

    def __str__(self):
        return f"{self.property_no} - {self.street}, {self.city}"

    def clean(self):
        super().clean()

        # 🌟 BUSINESS RULE: A staff member can manage a max of 20 properties
        if self.staff_no:
            current_managed_count = (
                Property.objects.filter(
                    staff_no=self.staff_no,
                    status__in=[self.PropertyStatus.AVAILABLE, self.PropertyStatus.RENTED],
                )
                .exclude(status=self.PropertyStatus.WITHDRAWN)
                .count()
            )

            if not self.pk or Property.objects.get(pk=self.pk).staff_no != self.staff_no:
                if current_managed_count >= 20:
                    raise ValidationError(
                        {
                            "staff_no": f"{self.staff_no.first_name} {self.staff_no.last_name} already manages the maximum of 20 active properties."
                        }
                    )

    def save(self, *args, **kwargs):
        """
        Auto-generate property_no as PG001, PG002, ...
        Ensures new properties created via API/admin always get a real ID.
        """
        if not self.property_no:
            with transaction.atomic():
                # Lock table rows to avoid duplicates if two creates happen at once
                last = (
                    Property.objects.select_for_update()
                    .filter(property_no__regex=r"^PG\d{3}$")
                    .order_by("-property_no")
                    .first()
                )

                next_num = int(last.property_no[2:]) + 1 if last else 1
                self.property_no = f"PG{next_num:03d}"

        super().save(*args, **kwargs)


class PropertyViewing(models.Model):
    property_no = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="viewings",
        db_column="property_no",
        null=True,  # Allow null to handle cases where the property might be deleted or unavailable
    )

    renter_no = models.ForeignKey(
        "users.Client",
        on_delete=models.CASCADE,
        related_name="viewings",
        limit_choices_to={"role": "Renter"},
        db_column="renter_no",
        null=True,  # Allow null to handle cases where the renter might be deleted
    )

    view_date = models.DateField()
    comments = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["property_no", "renter_no", "view_date"],
                name="unique_property_viewing",
            )
        ]

    def __str__(self):
        return f"Viewing for {self.property_no} on {self.view_date}"


class PropertyInspection(models.Model):
    property_no = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="inspections",
        db_column="property_no",
        null=True,  # Allow null to handle cases where the property might be deleted or unavailable
    )

    staff_no = models.ForeignKey(
        "users.Staff",
        on_delete=models.CASCADE,
        related_name="inspections",
        db_column="staff_no",
        null=True,  # Allow null to handle cases where the staff might be deleted
    )

    inspection_date = models.DateField()
    comments = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["property_no", "inspection_date"],
                name="unique_property_inspection",
            )
        ]

    def __str__(self):
        return f"Inspection for {self.property_no} on {self.inspection_date}"


class Advertisement(models.Model):
    property_no = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="advertisements",
        db_column="property_no",
        null=True,
    )

    newspaper_name = models.CharField(max_length=150)
    advert_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["property_no", "newspaper_name", "advert_date"],
                name="unique_property_advert",
            )
        ]

    def __str__(self):
        # Note: you reference advertisement_no here but that field isn't in this model.
        # Keeping your original behavior would error if __str__ is called.
        return f"{self.property_no} in {self.newspaper_name}"