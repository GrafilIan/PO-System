from django.db import models
from django.utils import timezone

class ArchiveFolder(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    DELIVERY_REF_CHOICES = [
        ('PL', 'PL'),
        ('DR', 'DR'),
        ('TR', 'TR')
    ]

    INVOICE_CHOICES = [
        ('SI', 'SI'),
        ('Invoice', 'Invoice'),
        ('CI', 'CI')
    ]

    REMARKS2_CHOICES = [
        ('On Hold', 'On Hold'),
        ('For Signature', 'For Signature'),
        ('Cancelled', 'Cancelled'),
        ('Paid', 'Paid')
    ]

    id = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name='Date')
    po_number = models.CharField(max_length=255, verbose_name='PO#')
    purchaser = models.CharField(max_length=255, verbose_name='Purchaser')
    brand = models.CharField(max_length=255, verbose_name='Brand', null=True, blank=True)
    item_code = models.CharField(max_length=255, blank=True, null=True, verbose_name='Item Code')
    particulars = models.CharField(max_length=255, verbose_name='Particulars')
    quantity = models.IntegerField(verbose_name='Quantity')
    unit = models.CharField(max_length=255, verbose_name='Unit', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total Amount')
    site_delivered = models.CharField(max_length=255, verbose_name='Site Delivered', null=True, blank=True)
    fbbd_ref_number = models.CharField(max_length=255, blank=True, null=True, verbose_name='FBBD Ref#')
    remarks = models.TextField(blank=True, null=True, verbose_name='Remarks')
    supplier = models.CharField(max_length=255, verbose_name='Supplier',null=True, blank=True)
    delivery_ref = models.CharField(max_length=2, choices=DELIVERY_REF_CHOICES, verbose_name='Delivery Ref#',null=True)
    delivery_no = models.CharField(max_length=255, verbose_name='Delivery No.',null=True)
    invoice_type = models.CharField(max_length=10, choices=INVOICE_CHOICES, verbose_name='Invoice#',null=True, blank=True)
    invoice_no = models.CharField(max_length=255, verbose_name='Invoice No.',null=True, blank=True)
    payment_req_ref = models.CharField(max_length=255, verbose_name='Payment Req Ref#',null=True, blank=True)
    payment_details = models.TextField(blank=True, null=True, verbose_name='Payment Details')
    remarks2 = models.CharField(max_length=20, choices=REMARKS2_CHOICES, verbose_name='Remarks2',null=True)
    folder = models.ForeignKey(ArchiveFolder, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def remarks2_badge(self):
        # Define a dictionary that maps remarks2 choices to corresponding background colors
        remarks2_colors = {
            'On Hold': '#ff0000',  # Red
            'For Signature': '#ffa500',  # Orange
            'Cancelled': '#808080',  # Grey
            'Paid': '#008000',  # Green
        }
        # Return the color associated with the remarks2 value
        return remarks2_colors.get(self.remarks2, '#000000')  # Default to black if not found

    def __str__(self):
        return self.po_number


