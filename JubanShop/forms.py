from django import forms
from django.core.exceptions import ValidationError

from JubanShop.models import JubanItemInventory, JubanInventoryHistory, JubanStockInHistory


class JubanUploadFileForm(forms.Form):
    file = forms.FileField()


class JubanItemCodeForm(forms.Form):
    class Meta:
        model = JubanItemInventory
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


class JubanItemInventoryListForm(forms.ModelForm):
    class Meta:
        model = JubanItemInventory
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
            if JubanItemInventory.objects.filter(po_product_name=po_product_name).exists():
                raise ValidationError('PO Product Name already exists. Please use a different name.')

            return po_product_name


class JubanEditRemarksForm(forms.ModelForm):
    class Meta:
        model = JubanInventoryHistory
        fields = ['remarks']  # Only include the remarks field


class JubanItemInventoryQuantityForm(forms.ModelForm):
    class Meta:
        model = JubanItemInventory
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


class JubanItemInventoryBulkForm(forms.ModelForm):
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
        model = JubanItemInventory
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
        super(JubanItemInventoryBulkForm, self).__init__(*args, **kwargs)
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


class JubanStockInHistoryForm(forms.ModelForm):
    particulars = forms.ChoiceField(
        choices=[(p, p) for p in JubanItemInventory.objects.values_list('po_product_name', flat=True).distinct()],
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_particulars'}),
        required=True,
        label='Particulars'
    )

    class Meta:
        model = JubanStockInHistory
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
        super(JubanStockInHistoryForm, self).__init__(*args, **kwargs)
        # Dynamically update the queryset for 'particulars'
        self.fields['particulars'].queryset = JubanItemInventory.objects.values_list('po_product_name', flat=True).distinct()