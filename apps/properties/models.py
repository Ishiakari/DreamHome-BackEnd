from datetime import timedelta
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import re


def default_advertisement_start_date():
    return timezone.localdate()


def default_advertisement_end_date():
    return timezone.localdate() + timedelta(days=30)


class Property(models.Model):
    # 🌟 NEW: Standardized choices for data consistency
    class PropertyType(models.TextChoices):
        FLAT = "Flat", "Flat"
        HOUSE = "House", "House"

    class PropertyStatus(models.TextChoices):
        PENDING = "Pending Approval", "Pending Approval"
        REJECTED = "Rejected", "Rejected"
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
        default=PropertyStatus.PENDING,
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
        db_table = 'property'

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
    class ViewingStatus(models.TextChoices):
        REQUESTED = "Requested", "Requested"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"
        CANCELLED = "Cancelled", "Cancelled"

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

    status = models.CharField(
        max_length=20,
        choices=ViewingStatus.choices,
        default=ViewingStatus.REQUESTED,
    )
    decided_by = models.ForeignKey(
        "users.Staff",
        on_delete=models.SET_NULL,
        related_name="decided_viewings",
        db_column="decided_by",
        null=True,
        blank=True,
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["property_no", "renter_no", "view_date"],
                name="unique_property_viewing",
            )
        ]
        db_table = 'property_viewing'

    def __str__(self):
        return f"Viewing for {self.property_no} on {self.view_date}"


class PropertyInspection(models.Model):
    class InspectionStatus(models.TextChoices):
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"

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
    status = models.CharField(
        max_length=20,
        choices=InspectionStatus.choices,
        default=InspectionStatus.SCHEDULED,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["property_no", "inspection_date"],
                name="unique_property_inspection",
            )
        ]
        db_table = 'property_inspection'
    def __str__(self):
        return f"Inspection for {self.property_no} on {self.inspection_date}"


class Advertisement(models.Model):
    class AdvertisementStatus(models.TextChoices):
        DRAFT = "Draft", "Draft"
        ACTIVE = "Active", "Active"
        ARCHIVED = "Archived", "Archived"

    class AdvertisementPlacement(models.TextChoices):
        POPUP = "Popup", "Popup"
        BANNER = "Banner", "Banner"
        SECTION = "Section", "Section"

    property_no = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="advertisements",
        db_column="property_no",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=200, default="Untitled Advertisement")
    message = models.TextField(default="Legacy advertisement (please update)")
    status = models.CharField(
        max_length=20,
        choices=AdvertisementStatus.choices,
        default=AdvertisementStatus.DRAFT,
    )
    start_date = models.DateField(default=default_advertisement_start_date)
    end_date = models.DateField(default=default_advertisement_end_date)
    priority = models.IntegerField(default=0)
    placement = models.CharField(
        max_length=20,
        choices=AdvertisementPlacement.choices,
        default=AdvertisementPlacement.POPUP,
    )
    assigned_by = models.ForeignKey(
        "users.Staff",
        on_delete=models.SET_NULL,
        related_name="assigned_advertisements",
        db_column="assigned_by",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'advertisement'

    def __str__(self):
        placement = self.placement or "Ad"
        title = self.title or "Untitled"
        return f"{placement}: {title}"