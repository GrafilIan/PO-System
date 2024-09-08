from django import forms
from django.core.exceptions import ValidationError

from .models import PurchaseOrder, ItemInventory, StockInHistory


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            'date',
            'po_number',
            'purchaser',
            'brand',
            'item_code',
            'particulars',
            'quantity',
            'unit',
            'price',
            'total_amount',
            'site_delivered',
            'fbbd_ref_number',
            'remarks',
            'supplier',
            'delivery_ref',
            'delivery_no',
            'invoice_type',
            'invoice_no',
            'payment_req_ref',
            'payment_details',
            'remarks2'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Date'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Price'}),
            'total_amount': forms.NumberInput(
                attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Total Amount'}),
            'quantity': forms.NumberInput(attrs={'min': 0, 'class': 'form-control', 'placeholder': 'Quantity'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Remarks'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO#'}),
            'purchaser': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purchaser'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand'}),
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Code'}),
            'particulars': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Particulars'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit'}),
            'site_delivered': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Site Delivered'}),
            'fbbd_ref_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FBBD Ref#'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier'}),
            'delivery_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery No.'}),
            'invoice_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Invoice Type'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice No.'}),
            'payment_req_ref': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Payment Req Ref#'}),
            'payment_details': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Payment Details'}),
            'remarks2': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Date'})
        self.fields['po_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'PO#'})
        self.fields['purchaser'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Purchaser'})
        self.fields['brand'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Brand'})
        self.fields['item_code'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Item Code'})
        self.fields['particulars'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Particulars'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Quantity'})
        self.fields['unit'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Unit'})
        self.fields['price'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Price'})
        self.fields['total_amount'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Total Amount'})
        self.fields['site_delivered'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Site Delivered'})
        self.fields['fbbd_ref_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'FBBD Ref#'})
        self.fields['remarks'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Remarks'})
        self.fields['supplier'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Supplier'})
        self.fields['delivery_ref'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Delivery Ref#'})
        self.fields['delivery_no'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Delivery No.'})
        self.fields['invoice_type'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Invoice Type'})
        self.fields['invoice_no'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Invoice No.'})
        self.fields['payment_req_ref'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Payment Req Ref#'})
        self.fields['payment_details'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Payment Details'})
        self.fields['remarks2'].widget.attrs.update({'class': 'form-control'})


class PurchaseOrderBulkForm(forms.ModelForm):
    REMARKS2_CHOICES = [
        ('On Hold', 'On Hold'),
        ('For Signature', 'For Signature'),
        ('Cancelled', 'Cancelled'),
        ('Paid', 'Paid'),
    ]

    fbbd_ref_number = forms.CharField(required=False)
    remarks2 = forms.ChoiceField(choices=REMARKS2_CHOICES, required=False,
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = PurchaseOrder
        fields = [
            'date',
            'po_number',
            'purchaser',
            'brand',
            'item_code',
            'particulars',
            'quantity',
            'unit',
            'price',
            'total_amount',
            'site_delivered',
            'fbbd_ref_number',
            'remarks',
            'supplier',
            'delivery_ref',
            'delivery_no',
            'invoice_type',
            'invoice_no',
            'payment_req_ref',
            'payment_details',
            'remarks2'
        ]

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Date'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Price'}),
            'total_amount': forms.NumberInput(
                attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Total Amount'}),
            'quantity': forms.NumberInput(attrs={'min': 0, 'class': 'form-control', 'placeholder': 'Quantity'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Remarks'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO#'}),
            'purchaser': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purchaser'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand'}),
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Code'}),
            'particulars': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Particulars'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit'}),
            'site_delivered': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Site Delivered'}),
            'fbbd_ref_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FBBD Ref#'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier'}),
            'delivery_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery No.'}),
            'invoice_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Invoice Type'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice No.'}),
            'payment_req_ref': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Payment Req Ref#'}),
            'payment_details': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Payment Details'}),
            'remarks2': forms.Select(attrs={'class': 'form-control'})
        }


class UploadFileForm(forms.Form):
    file = forms.FileField()


class ItemCodeForm(forms.Form):
    class Meta:
        model = ItemInventory
        fields = [
            'item_code',
            'po_product_name',
            'unit',
            'quantity_in',
            'quantity_out',
            'stock',
            'supplier',
        ]

        widgets = {
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Code'}),
            'po_product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO Product Name'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit'}),
            'quantity_in': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity In'}),
            'quantity_out': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity Out'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier'}),
        }


class ItemInventoryListForm(forms.ModelForm):
    class Meta:
        model = ItemInventory
        fields = [
            'item_code',
            'po_product_name',
            'unit',
            'quantity_in',
            'quantity_out',
            'stock',
            'supplier',
        ]

        widgets = {
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Code'}),
            'po_product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Particular'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit'}),
            'quantity_in': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Quantity In', 'step': '0.0001'}),
            'quantity_out': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Quantity Out', 'step': '0.0001'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock', 'step': '0.0001'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier'}),
        }

        # Custom validation for po_product_name to avoid duplicates
        def __init__(self):
            self.cleaned_data = None

        def clean_po_product_name(self):
            po_product_name = self.cleaned_data.get('po_product_name')

            # Check if the po_product_name already exists in the database
            if ItemInventory.objects.filter(po_product_name=po_product_name).exists():
                raise ValidationError('PO Product Name already exists. Please use a different name.')

            return po_product_name


class ItemInventoryQuantityForm(forms.ModelForm):
    class Meta:
        model = ItemInventory
        fields = ['po_product_name', 'quantity_in', 'quantity_out', 'stock',
                  'supplier']  # Only include the quantity fields
        widgets = {
            'po_product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity_in': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Quantity In', 'step': '0.0001'}),
            'quantity_out': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Quantity Out', 'step': '0.0001'}),
            'stock': forms.NumberInput(
                attrs={'readonly': True, 'class': 'form-control', 'placeholder': 'Stock', 'step': '0.0001'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Update the stock based on the quantities
        quantity_in = cleaned_data.get('quantity_in', 0)
        quantity_out = cleaned_data.get('quantity_out', 0)

        # Calculate stock
        cleaned_data['stock'] = quantity_in - quantity_out

        return cleaned_data


class ItemInventoryBulkForm(forms.ModelForm):
    LOCATION_CHOICES = [
        ('site', 'Site Delivered'),
        ('client', 'Client'),
    ]

    location_type = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Location Type',
    )
    location_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Site or Client Name'}),
        label='Location Name',
    )

    class Meta:
        model = ItemInventory
        fields = [
            'date',
            'item_code',
            'supplier',
            'po_product_name',
            'new_product_name',
            'unit',
            'quantity_in',
            'quantity_out',
            'stock',
            'price',
            'total_amount',
            'site_delivered',
            'client',
            'location_type',
            'location_name',
            'delivery_ref',
            'delivery_no',
            'invoice_type',
            'invoice_no',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Date'}),
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Code'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier'}),
            'po_product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO Product Name'}),
            'new_product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'New Product Name'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit'}),
            'quantity_in': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Quantity In', 'step': '0.0001'}),
            'quantity_out': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Quantity Out', 'step': '0.0001'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Price'}),
            'total_amount': forms.NumberInput(
                attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Total Amount', 'readonly': True}),
            'stock': forms.NumberInput(
                attrs={'readonly': True, 'class': 'form-control', 'placeholder': 'Stock', 'step': '0.0001'}),
            'delivery_ref': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Delivery Ref#'}),
            'delivery_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery No.'}),
            'invoice_type': forms.Select(attrs={'class': 'form-control'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice No.'}),
        }

    def __init__(self, *args, **kwargs):
        super(ItemInventoryBulkForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['quantity_in', 'quantity_out', 'stock', 'price', 'total_amount']:
                field.required = False
            field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label if field.label else ''})

    def clean(self):
        cleaned_data = super().clean()
        location_type = cleaned_data.get('location_type')
        location_name = cleaned_data.get('location_name')

        if location_type == 'site':
            cleaned_data['site_delivered'] = location_name
            cleaned_data['client'] = None
        elif location_type == 'client':
            cleaned_data['client'] = location_name
            cleaned_data['site_delivered'] = None

        return cleaned_data


class StockInHistoryForm(forms.ModelForm):
    particulars = forms.ChoiceField(
        choices=[(p, p) for p in ItemInventory.objects.values_list('po_product_name', flat=True).distinct()],
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_particulars'}),
        required=True,
        label='Particulars'
    )

    class Meta:
        model = StockInHistory
        fields = [
            'date',
            'po_number',
            'purchaser',
            'item_code',
            'particulars',
            'quantity_in',
            'unit',
            'fbbd_ref_number',
            'remarks',
            'supplier',
            'delivery_ref',
            'delivery_no',
            'invoice_type',
            'invoice_no',
            'payment_req_ref',
            'payment_details',
            'remarks2'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Date'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO#'}),
            'purchaser': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purchaser'}),
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Code'}),
            'quantity_in': forms.NumberInput(attrs={'min': 0, 'class': 'form-control', 'placeholder': 'Quantity In', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit'}),
            'fbbd_ref_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FBBD Ref#'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Remarks'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier'}),
            'delivery_ref': forms.Select(attrs={'class': 'form-control'}),
            'delivery_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery No.'}),
            'invoice_type': forms.Select(attrs={'class': 'form-control'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice No.'}),
            'payment_req_ref': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Payment Req Ref#'}),
            'payment_details': forms.Select(attrs={'class': 'form-control'}),
            'remarks2': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(StockInHistoryForm, self).__init__(*args, **kwargs)
        # Dynamically update the queryset for 'particulars'
        self.fields['particulars'].queryset = ItemInventory.objects.values_list('po_product_name', flat=True).distinct()


