from django.db import models
from django.utils import timezone
class SiteInventoryFolder(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class ClientInventoryFolder(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class SupplierFolder(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class ItemInventory(models.Model):
    SITE_OR_CLIENT_CHOICES = (
        ('site', 'Site Delivered'),
        ('client', 'Client'),
    )

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

    date = models.DateField(verbose_name='Date', null=True)
    item_code = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.CharField(max_length=100, blank=True, null=True)
    po_product_name = models.CharField(max_length=100, blank=True, null=True)
    new_product_name = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    quantity_in = models.IntegerField()
    quantity_out = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    site_or_client_choice = models.CharField(max_length=10, choices=SITE_OR_CLIENT_CHOICES, blank=True, null=True)
    site_delivered = models.CharField(max_length=255, verbose_name='Site Delivered', null=True, blank=True)
    client = models.CharField(max_length=255, verbose_name='Client', null=True, blank=True)
    site_inventory_folder = models.ForeignKey(SiteInventoryFolder, on_delete=models.CASCADE, null=True, blank=True)
    client_inventory_folder = models.ForeignKey(ClientInventoryFolder, on_delete=models.CASCADE, null=True, blank=True)
    delivery_ref = models.CharField(max_length=2, choices=DELIVERY_REF_CHOICES, verbose_name='Delivery Ref#', null=True)
    delivery_no = models.CharField(max_length=255, verbose_name='Delivery No.', null=True)
    invoice_type = models.CharField(max_length=10, choices=INVOICE_CHOICES, verbose_name='Invoice#', null=True,
                                    blank=True)
    invoice_no = models.CharField(max_length=255, verbose_name='Invoice No.', null=True, blank=True)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location_type = kwargs.get('location_type', None)

    def save(self, *args, **kwargs):
        if self.pk:
            # Fetch the previous record from the database
            previous = ItemInventory.objects.get(pk=self.pk)

            # The current input is how much more we want to subtract from stock
            quantity_out_delta = self.quantity_out

            # Update the cumulative quantity_out by adding the new quantity to the previous total
            new_quantity_out = previous.quantity_out + quantity_out_delta
            self.quantity_out = new_quantity_out
            self.stock = self.quantity_in - new_quantity_out
            self.total_amount = self.quantity_out * self.price  # Updated calculation

            # Create a history entry with the current quantity_out input (delta), not the cumulative
            InventoryHistory.objects.create(
                item=self,
                date=self.date,
                item_code=self.item_code,
                supplier=self.supplier,
                po_product_name=self.po_product_name,
                new_product_name=self.new_product_name,
                unit=self.unit,
                quantity_in=self.quantity_in,
                quantity_out=quantity_out_delta,  # Log the delta/change, not the cumulative
                stock=self.stock,
                price=self.price,
                total_amount=quantity_out_delta * self.price,  # Correctly log the delta amount
                site_delivered=self.site_delivered if self.site_or_client_choice == 'site' else None,
                client=self.client if self.site_or_client_choice == 'client' else None,
                delivery_ref=self.delivery_ref,
                delivery_no=self.delivery_no,
                invoice_type=self.invoice_type,
                invoice_no=self.invoice_no,
            )
        else:
            # For new records, set initial stock and total_amount
            self.stock = self.quantity_in - self.quantity_out
            self.total_amount = self.quantity_out * self.price  # Updated calculation

        if self.site_or_client_choice == 'site':
            self.site_delivered = self.site_delivered
            self.client = None
        elif self.site_or_client_choice == 'client':
            self.client = self.client
            self.site_delivered = None

        # Ensure site_or_client_choice is set correctly
        self.site_or_client_choice = self.site_or_client_choice or self.location_type

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.po_product_name} ({self.supplier})"



class InventoryHistory(models.Model):
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

    item = models.ForeignKey(ItemInventory, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    item_code = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.CharField(max_length=100, blank=True, null=True)
    po_product_name = models.CharField(max_length=100, blank=True, null=True)
    new_product_name = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    quantity_in = models.IntegerField()
    quantity_out = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    site_delivered = models.CharField(max_length=255, verbose_name='Site Delivered', null=True, blank=True)
    site_inventory_folder = models.ForeignKey(SiteInventoryFolder, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.CharField(max_length=255, verbose_name='Client', null=True, blank=True)
    client_inventory_folder = models.ForeignKey(ClientInventoryFolder, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_ref = models.CharField(max_length=2, choices=DELIVERY_REF_CHOICES, verbose_name='Delivery Ref#', null=True)
    delivery_no = models.CharField(max_length=255, verbose_name='Delivery No.', null=True)
    invoice_type = models.CharField(max_length=10, choices=INVOICE_CHOICES, verbose_name='Invoice#', null=True,
                                    blank=True)
    invoice_no = models.CharField(max_length=255, verbose_name='Invoice No.', null=True, blank=True)

    def __str__(self):
        return f"{self.po_product_name} ({self.item_code}) - {self.quantity_out}"

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

    PAYMENT_DETAILS_CHOICES = [
        ('Check Voucher', 'Check Voucher'),
        ('Cash Voucher', 'Cash Voucher')
    ]

    REMARKS2_CHOICES = [
        ('On Hold', 'On Hold'),
        ('For Signature', 'For Signature'),
        ('Cancelled', 'Cancelled'),
        ('Paid', 'Paid')
    ]

    id = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name='Date', null=True)
    po_number = models.CharField(max_length=255, verbose_name='PO#', null=True)
    purchaser = models.CharField(max_length=255, verbose_name='Purchaser', null=True)
    brand = models.CharField(max_length=255, verbose_name='Brand', null=True, blank=True)
    item_code = models.CharField(max_length=255, blank=True, null=True, verbose_name='Item Code')
    particulars = models.CharField(max_length=255, verbose_name='Particulars', null=True)
    quantity = models.IntegerField(verbose_name='Quantity', null=True)
    unit = models.CharField(max_length=255, verbose_name='Unit', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price', null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total Amount', null=True)
    site_delivered = models.CharField(max_length=255, verbose_name='Site Delivered', null=True, blank=True)
    fbbd_ref_number = models.CharField(max_length=255, blank=True, null=True, verbose_name='FBBD Ref#')
    remarks = models.TextField(blank=True, null=True, verbose_name='Remarks')
    supplier = models.CharField(max_length=255, verbose_name='Supplier',null=True, blank=True)
    delivery_ref = models.CharField(max_length=2, choices=DELIVERY_REF_CHOICES, verbose_name='Delivery Ref#',null=True)
    delivery_no = models.CharField(max_length=255, verbose_name='Delivery No.',null=True)
    invoice_type = models.CharField(max_length=10, choices=INVOICE_CHOICES, verbose_name='Invoice#',null=True, blank=True)
    invoice_no = models.CharField(max_length=255, verbose_name='Invoice No.',null=True, blank=True)
    payment_req_ref = models.CharField(max_length=255, verbose_name='Payment Req Ref#',null=True, blank=True)
    payment_details = models.TextField(max_length=20, choices=PAYMENT_DETAILS_CHOICES, blank=True, null=True, verbose_name='Payment Details')
    remarks2 = models.CharField(max_length=20, choices=REMARKS2_CHOICES, verbose_name='Remarks2',null=True)
    folder = models.ForeignKey(ArchiveFolder, on_delete=models.SET_NULL, null=True, blank=True)
    archived = models.BooleanField(default=False)
    supplier_folder = models.ForeignKey(SupplierFolder, on_delete=models.SET_NULL, null=True, blank=True)

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




