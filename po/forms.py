from django import forms

from .models import PurchaseOrder, ItemInventory


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


class UploadFileForm(forms.Form):
    file = forms.FileField()


class ItemInventoryForm(forms.ModelForm):
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
            'site_delivered',  # This will be used based on the choice made
            'client',  # This will be used based on the choice made
            'location_type',  # New field for choosing between site and client
            'location_name',  # New field for entering the site or client name
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
            'quantity_in': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity In'}),
            'quantity_out': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity Out'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Price'}),
            'total_amount': forms.NumberInput(
                attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Total Amount', 'readonly': True}),
            'stock': forms.NumberInput(attrs={'readonly': True, 'class': 'form-control', 'placeholder': 'Stock'}),
            'delivery_ref': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery Ref#'}),
            'delivery_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery No.'}),
            'invoice_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Invoice Type'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice No.'}),
        }

    def __init__(self, *args, **kwargs):
        super(ItemInventoryForm, self).__init__(*args, **kwargs)
        # Set widget attributes in init to ensure all fields have the correct attributes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})

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

        # Ensure site_or_client_choice is set
        cleaned_data['site_or_client_choice'] = location_type

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
            'quantity_in': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity In'}),
            'quantity_out': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity Out'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Price'}),
            'total_amount': forms.NumberInput(
                attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Total Amount', 'readonly': True}),
            'stock': forms.NumberInput(attrs={'readonly': True, 'class': 'form-control', 'placeholder': 'Stock'}),
            'delivery_ref': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery Ref#'}),
            'delivery_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery No.'}),
            'invoice_type': forms.Select(attrs={'class': 'form-control'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice No.'}),
        }

    def __init__(self, *args, **kwargs):
        super(ItemInventoryBulkForm, self).__init__(*args, **kwargs)
        # Set widget attributes in init to ensure all fields have the correct attributes
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

        # Ensure site_or_client_choice is set
        cleaned_data['site_or_client_choice'] = location_type

        return cleaned_data


