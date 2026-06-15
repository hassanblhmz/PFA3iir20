from decimal import Decimal

from django import forms
from django.db.models import F, Q

from products.models import Category, Product
from purchases.models import (
    PurchaseOrder, PurchaseOrderLine, PurchaseRequest, PurchaseRequestLine,
    SupplierRequestMessage,
)
from stock.models import StockMovement
from suppliers.models import Supplier


class StyledFormMixin:
    def _style_fields(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class ProductForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'code', 'name', 'description', 'category', 'unit', 'unit_price',
            'current_stock', 'min_stock', 'max_stock', 'suppliers', 'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'suppliers': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('name')
        self.fields['suppliers'].queryset = Supplier.objects.filter(status='actif').order_by('name')
        self.fields['code'].label = 'Reference'
        self.fields['name'].label = 'Designation'
        self.fields['description'].label = 'Description'
        self.fields['category'].label = 'Categorie'
        self.fields['unit'].label = 'Unite'
        self.fields['unit'].choices = Product.UNIT_CHOICES
        self.fields['unit_price'].label = 'Prix unitaire'
        self.fields['current_stock'].label = 'Stock actuel'
        self.fields['min_stock'].label = 'Seuil critique'
        self.fields['max_stock'].label = 'Stock maximum'
        self.fields['suppliers'].label = 'Fournisseurs'
        self.fields['is_active'].label = 'Article actif'
        self._style_fields()


class SupplierForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'code', 'name', 'contact_name', 'email', 'phone', 'address',
            'city', 'country', 'ice', 'payment_terms', 'status', 'notes',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            'code': 'Code fournisseur',
            'name': 'Raison sociale',
            'contact_name': 'Contact',
            'email': 'Email',
            'phone': 'Telephone',
            'address': 'Adresse',
            'city': 'Ville',
            'country': 'Pays',
            'ice': 'ICE',
            'payment_terms': 'Delai paiement (jours)',
            'status': 'Statut',
            'notes': 'Notes',
        }
        for field_name, label in labels.items():
            self.fields[field_name].label = label
        self._style_fields()


class PurchaseRequestForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['title', 'priority', 'needed_date', 'notes']
        widgets = {
            'needed_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Objet'
        self.fields['priority'].label = 'Priorite'
        self.fields['needed_date'].label = 'Date souhaitee'
        self.fields['notes'].label = 'Remarques'
        self._style_fields()


class PurchaseRequestLineForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PurchaseRequestLine
        fields = ['product', 'quantity', 'unit_price', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True).order_by('name')
        self.fields['product'].label = 'Article'
        self.fields['quantity'].label = 'Quantite'
        self.fields['unit_price'].label = 'Prix unitaire estime'
        self.fields['notes'].label = 'Notes'
        self._style_fields()


class RequestDecisionForm(forms.Form):
    comment = forms.CharField(
        label='Commentaire',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
    )


class CreateOrderForm(StyledFormMixin, forms.Form):
    supplier = forms.ModelChoiceField(label='Fournisseur', queryset=Supplier.objects.filter(status='actif').order_by('name'))
    expected_date = forms.DateField(label='Livraison prevue', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class ReceptionForm(StyledFormMixin, forms.Form):
    reference = forms.CharField(label='BL fournisseur', required=False)
    order_line = forms.ModelChoiceField(label='Ligne commande', queryset=PurchaseOrderLine.objects.none())
    quantity_received = forms.DecimalField(label='Quantite recue', min_value=Decimal('0.01'))
    notes = forms.CharField(label='Notes', required=False, widget=forms.Textarea(attrs={'rows': 2}))

    def __init__(self, order, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_line'].queryset = order.order_lines.select_related('product').order_by('product__name')
        self._style_fields()


class SupplierOrderResponseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier_quote_amount', 'supplier_delivery_date',
            'supplier_document_reference', 'supplier_note',
        ]
        widgets = {
            'supplier_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'supplier_note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier_quote_amount'].label = 'Montant propose'
        self.fields['supplier_delivery_date'].label = 'Date de livraison proposee'
        self.fields['supplier_document_reference'].label = 'Reference devis / facture / BL'
        self.fields['supplier_document_reference'].required = False
        self.fields['supplier_note'].label = 'Note fournisseur'
        self.fields['supplier_note'].required = False
        self._style_fields()


class SupplierDeliveryStatusForm(StyledFormMixin, forms.Form):
    status = forms.ChoiceField(label='Statut livraison', choices=[
        ('preparation', 'En preparation'),
        ('expediee', 'Expediee'),
        ('livree', 'Livree'),
    ])
    note = forms.CharField(label='Note', required=False, widget=forms.Textarea(attrs={'rows': 2}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class StockAdjustmentForm(StyledFormMixin, forms.Form):
    product = forms.ModelChoiceField(label='Article', queryset=Product.objects.filter(is_active=True).order_by('name'))
    type = forms.ChoiceField(label='Type', choices=[
        ('entree', 'Entree'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
    ])
    quantity = forms.DecimalField(label='Quantite', min_value=Decimal('0.01'))
    reference = forms.CharField(label='Reference', required=False)
    reason = forms.CharField(label='Motif', widget=forms.Textarea(attrs={'rows': 2}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class ConversationOpenForm(StyledFormMixin, forms.Form):
    request_line = forms.ModelChoiceField(label='Article concerne', queryset=PurchaseRequestLine.objects.none())
    supplier = forms.ModelChoiceField(label='Fournisseur', queryset=Supplier.objects.filter(status='actif').order_by('name'))
    body = forms.CharField(label='Message', widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, request_obj, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['request_line'].queryset = request_obj.lines.select_related('product').filter(
            Q(product__current_stock__lte=F('product__min_stock')) | Q(product__is_active=False)
        )
        self._style_fields()


class ConversationReplyForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SupplierRequestMessage
        fields = ['body']
        widgets = {'body': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
