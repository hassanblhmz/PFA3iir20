from django import forms
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView

from core.forms import (
    ConversationOpenForm, ConversationReplyForm, CreateOrderForm,
    ProductForm, PurchaseRequestForm, PurchaseRequestLineForm,
    ReceptionForm, RequestDecisionForm, StockAdjustmentForm,
    SupplierDeliveryStatusForm, SupplierForm, SupplierOrderResponseForm,
)
from products.models import Product
from purchases.models import (
    AuditLog, Notification,
    PurchaseOrder, PurchaseOrderLine, PurchaseRequest, PurchaseRequestLine,
    Reception, ReceptionLine, SupplierRequestConversation, SupplierRequestMessage,
    ValidationLog,
)
from stock.models import StockMovement
from suppliers.models import Supplier
from users.models import User


DEMO_ACCOUNTS = [
    {'key': 'admin', 'email': 'admin@pfa.ma', 'password': 'admin123', 'role': 'Administrateur'},
    {'key': 'demandeur', 'email': 'demandeur@pfa.ma', 'password': 'test123', 'role': 'Demandeur'},
    {'key': 'validateur', 'email': 'validateur@pfa.ma', 'password': 'test123', 'role': 'Validateur'},
    {'key': 'acheteur', 'email': 'acheteur@pfa.ma', 'password': 'test123', 'role': 'Acheteur'},
    {'key': 'magasinier', 'email': 'magasinier@pfa.ma', 'password': 'test123', 'role': 'Magasinier'},
    {'key': 'fournisseur', 'email': 'fournisseur@pfa.ma', 'password': 'test123', 'role': 'Fournisseur'},
]
DEMO_ACCOUNT_BY_KEY = {account['key']: account for account in DEMO_ACCOUNTS}


MODULE_CATALOG = {
    'users': {
        'title': 'Utilisateurs',
        'description': 'Comptes, roles et acces applicatifs.',
        'href': '/accounts/',
    },
    'requests': {
        'title': 'Demandes d achat',
        'description': 'Creation, suivi et priorisation des besoins.',
        'href': '/requests/',
    },
    'products': {
        'title': 'Articles',
        'description': 'Catalogue, stock actuel, seuils, statuts critique et rupture.',
        'href': '/products/',
    },
    'validation': {
        'title': 'Validation',
        'description': 'Decision, commentaires et journal de validation.',
        'href': '/requests/',
    },
    'orders': {
        'title': 'Commandes',
        'description': 'Bons de commande, envoi et suivi fournisseur.',
        'href': '/orders/',
    },
    'stock': {
        'title': 'Stock',
        'description': 'Receptions, ajustements et articles critiques.',
        'href': '/stock/',
    },
    'suppliers': {
        'title': 'Fournisseurs',
        'description': 'Referentiel, devis et conversations sur rupture.',
        'href': '/suppliers/',
    },
    'conversations': {
        'title': 'Conversations',
        'description': 'Echanges fournisseur et demandeur pour articles critiques ou indisponibles.',
        'href': '/conversations/',
    },
}


ROLE_WORKSPACES = {
    'admin': {
        'title': 'Espace administrateur',
        'subtitle': 'Vue complete sur les achats, utilisateurs, fournisseurs et stocks.',
        'capabilities': [
            'Gerer les utilisateurs et les roles',
            'Superviser toutes les demandes',
            'Acceder aux commandes, receptions et mouvements',
            'Administrer les referentiels',
        ],
        'endpoints': ['/api/users/', '/api/suppliers/', '/api/products/', '/api/purchases/requests/', '/api/stock/movements/'],
        'flags': {'users': True, 'requests': True, 'products': True, 'validation': True, 'orders': True, 'stock': True, 'suppliers': True, 'conversations': True, 'admin': True},
    },
    'demandeur': {
        'title': 'Espace demandeur',
        'subtitle': 'Creation et suivi des demandes d achat de votre departement.',
        'capabilities': [
            'Creer une demande d achat',
            'Suivre le statut de validation',
            'Discuter avec le fournisseur si un article est critique ou indisponible',
        ],
        'endpoints': ['/api/purchases/requests/', '/api/products/', '/api/purchases/supplier-conversations/'],
        'flags': {'requests': True, 'products': True, 'conversations': True},
    },
    'validateur': {
        'title': 'Espace validateur',
        'subtitle': 'Controle, validation et rejet motive des demandes soumises.',
        'capabilities': [
            'Analyser les demandes soumises',
            'Valider ou rejeter avec commentaire',
            'Consulter les historiques de validation',
        ],
        'endpoints': ['/api/purchases/requests/', '/api/purchases/dashboard/'],
        'flags': {'requests': True, 'products': True, 'validation': True},
    },
    'acheteur': {
        'title': 'Espace acheteur',
        'subtitle': 'Consultation fournisseurs, devis et conversion en commandes.',
        'capabilities': [
            'Comparer les fournisseurs',
            'Creer les bons de commande',
            'Piloter les conversations fournisseur/demandeur',
        ],
        'endpoints': ['/api/suppliers/', '/api/purchases/orders/', '/api/purchases/supplier-conversations/'],
        'flags': {'orders': True, 'products': True, 'suppliers': True, 'conversations': True, 'requests': True},
    },
    'magasinier': {
        'title': 'Espace magasinier',
        'subtitle': 'Reception des commandes et fiabilisation des niveaux de stock.',
        'capabilities': [
            'Receptionner les commandes',
            'Ajuster les mouvements de stock',
            'Surveiller les articles critiques',
        ],
        'endpoints': ['/api/purchases/receptions/', '/api/stock/movements/', '/api/stock/movements/critical_products/'],
        'flags': {'stock': True, 'products': True, 'orders': True},
    },
    'direction': {
        'title': 'Espace direction',
        'subtitle': 'Lecture executive du pipeline achats et des risques stock.',
        'capabilities': [
            'Consulter les indicateurs globaux',
            'Suivre les demandes urgentes',
            'Identifier les ruptures et depenses',
        ],
        'endpoints': ['/api/purchases/dashboard/'],
        'flags': {'requests': True, 'products': True, 'orders': True, 'stock': True},
    },
    'fournisseur': {
        'title': 'Espace fournisseur',
        'subtitle': 'Commandes recues, confirmations, devis et suivi livraison.',
        'capabilities': [
            'Voir les commandes envoyees a votre societe',
            'Soumettre un devis ou confirmer une commande',
            'Mettre a jour la preparation et la livraison',
            'Voir les conversations ouvertes avec les demandeurs',
            'Repondre sur disponibilite, delais et alternatives',
        ],
        'endpoints': ['/api/purchases/orders/', '/api/purchases/supplier-conversations/'],
        'flags': {'orders': True, 'conversations': True},
    },
}


def workspace_for(user):
    workspace = ROLE_WORKSPACES.get(user.role, ROLE_WORKSPACES['demandeur']).copy()
    workspace['flags'] = workspace.get('flags', {}).copy()
    workspace['modules'] = [
        module for key, module in MODULE_CATALOG.items()
        if workspace['flags'].get(key)
    ]
    return workspace


def has_role(user, *roles):
    return user.is_authenticated and (user.role == 'admin' or user.role in roles)


def require_role(user, *roles):
    if not has_role(user, *roles):
        raise PermissionDenied


def create_audit_log(user, action, entity, entity_id=None, description=''):
    AuditLog.objects.create(
        user=user if getattr(user, 'is_authenticated', False) else None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        description=description,
    )


def notify_user(user, title, message='', link=''):
    if user and user.is_active:
        Notification.objects.create(user=user, title=title, message=message, link=link)


def notify_roles(roles, title, message='', link='', exclude_user=None):
    users = User.objects.filter(role__in=roles, is_active=True)
    if exclude_user:
        users = users.exclude(pk=exclude_user.pk)
    Notification.objects.bulk_create([
        Notification(user=user, title=title, message=message, link=link)
        for user in users
    ])


def safe_notification_redirect(link):
    return link if link and link.startswith('/') and not link.startswith('//') else '/'


def app_context(request, **extra):
    notifications = Notification.objects.none()
    unread_notifications_count = 0
    if request.user.is_authenticated:
        notifications = request.user.notifications.order_by('-created_at')[:5]
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
    context = {
        'workspace': workspace_for(request.user),
        'can_manage_products': has_role(request.user, 'acheteur'),
        'can_manage_suppliers': has_role(request.user, 'acheteur'),
        'can_create_requests': has_role(request.user, 'demandeur'),
        'can_validate_requests': has_role(request.user, 'validateur'),
        'can_manage_orders': has_role(request.user, 'acheteur'),
        'can_supplier_manage_orders': request.user.is_authenticated and request.user.role == 'fournisseur',
        'can_manage_stock': has_role(request.user, 'magasinier'),
        'can_use_conversations': request.user.is_authenticated and request.user.role == 'demandeur',
        'recent_notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    context.update(extra)
    return context


@login_required(login_url='login')
def notification_open(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    return redirect(safe_notification_redirect(notification.link))


@login_required(login_url='login')
@require_POST
def notifications_mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, 'Notifications marquees comme lues.')
    return redirect(safe_notification_redirect(request.POST.get('next')))


class EmailAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs.update({
            'autocomplete': 'email',
            'placeholder': 'admin@pfa.ma',
        })
        self.fields['password'].label = 'Mot de passe'
        password_attrs = self.fields['password'].widget.attrs
        password_attrs.update({
            'autocomplete': 'current-password',
            'placeholder': 'admin123',
        })
        self.fields['password'].widget = forms.PasswordInput(
            attrs=password_attrs,
            render_value=True,
        )


class GestAchatsLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True
    next_page = reverse_lazy('home')

    def get_initial(self):
        initial = super().get_initial()
        account = DEMO_ACCOUNT_BY_KEY.get(self.request.GET.get('demo'))
        if account:
            initial.update({
                'username': account['email'],
                'password': account['password'],
            })
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['demo_accounts'] = DEMO_ACCOUNTS
        context['selected_demo'] = self.request.GET.get('demo', '')
        return context


class GestAchatsLogoutView(LogoutView):
    next_page = 'login'


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(app_context(self.request))
        workspace = workspace_for(self.request.user)
        recent_orders = PurchaseOrder.objects.select_related('supplier', 'ordered_by').order_by('-created_at')
        if self.request.user.role == 'fournisseur':
            if self.request.user.supplier_id:
                recent_orders = recent_orders.filter(supplier=self.request.user.supplier).exclude(status='brouillon')
            else:
                recent_orders = recent_orders.none()
        context['workspace'] = workspace
        context['metrics'] = {
            'total_requests': PurchaseRequest.objects.count(),
            'open_requests': PurchaseRequest.objects.filter(status__in=['soumis', 'en_validation']).count(),
            'approved_requests': PurchaseRequest.objects.filter(status='valide').count(),
            'rejected_requests': PurchaseRequest.objects.filter(status='rejete').count(),
            'sent_orders': PurchaseOrder.objects.filter(status__in=['envoyee', 'confirmee', 'expediee', 'recue_partielle']).count(),
            'critical_products': Product.objects.filter(
                Q(current_stock__lte=F('min_stock')) | Q(is_active=False)
            ).count(),
            'conversations': SupplierRequestConversation.objects.exclude(status='cloturee').count(),
            'suppliers': Supplier.objects.filter(status='actif').count(),
            'users': User.objects.filter(is_active=True).count(),
        }
        order_counts = PurchaseOrder.objects.values('status').annotate(total=Count('id')).order_by('status')
        context['order_status_counts'] = {
            dict(PurchaseOrder.STATUS_CHOICES).get(row['status'], row['status']): row['total']
            for row in order_counts
        }
        context['critical_products'] = Product.objects.filter(
            Q(current_stock__lte=F('min_stock')) | Q(is_active=False)
        ).select_related('category').order_by('current_stock')[:5]
        context['recent_requests'] = PurchaseRequest.objects.select_related('requested_by').order_by('-created_at')[:5]
        context['recent_orders'] = recent_orders[:5]
        context['recent_conversations'] = SupplierRequestConversation.objects.select_related(
            'supplier', 'demandeur', 'request_line__product'
        ).order_by('-updated_at')[:4]
        context['recent_audit_logs'] = AuditLog.objects.select_related('user').order_by('-created_at')[:6]
        return context


class AccountsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts.html'
    login_url = 'login'
    raise_exception = True

    def test_func(self):
        return self.request.user.role == 'admin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(app_context(self.request))
        context['demo_accounts'] = DEMO_ACCOUNTS
        context['users'] = User.objects.order_by('role', 'email')
        context['active_users_count'] = User.objects.filter(is_active=True).count()
        context['inactive_users_count'] = User.objects.filter(is_active=False).count()
        context['recent_audit_logs'] = AuditLog.objects.select_related('user').order_by('-created_at')[:10]
        return context


@login_required(login_url='login')
def product_list(request):
    require_role(request.user, 'demandeur', 'validateur', 'acheteur', 'magasinier', 'direction')
    products = Product.objects.select_related('category').prefetch_related('suppliers').order_by('name')
    status_filter = request.GET.get('status')
    if status_filter == 'critique':
        products = products.filter(current_stock__lte=F('min_stock'), current_stock__gt=0, is_active=True)
    elif status_filter == 'rupture':
        products = products.filter(current_stock__lte=0, is_active=True)
    elif status_filter == 'indisponible':
        products = products.filter(is_active=False)
    elif status_filter == 'normal':
        products = products.filter(current_stock__gt=F('min_stock'), is_active=True)
    return render(request, 'products/list.html', app_context(
        request,
        products=products,
        status_filter=status_filter or '',
    ))


@login_required(login_url='login')
def product_create(request):
    require_role(request.user, 'acheteur')
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save()
        create_audit_log(request.user, 'product_creation', 'Product', product.id, f"Article {product.code} cree.")
        messages.success(request, f"Article {product.code} cree.")
        return redirect('/products/')
    return render(request, 'products/form.html', app_context(
        request, form=form, title='Nouvel article', submit_label='Creer article'
    ))


@login_required(login_url='login')
def product_edit(request, pk):
    require_role(request.user, 'acheteur')
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        create_audit_log(request.user, 'product_update', 'Product', product.id, f"Article {product.code} mis a jour.")
        messages.success(request, f"Article {product.code} mis a jour.")
        return redirect('/products/')
    return render(request, 'products/form.html', app_context(
        request, form=form, product=product, title=f'Modifier {product.code}', submit_label='Enregistrer'
    ))


@login_required(login_url='login')
def supplier_list(request):
    require_role(request.user, 'acheteur')
    suppliers = Supplier.objects.prefetch_related('products', 'purchase_orders').order_by('name')
    return render(request, 'suppliers/list.html', app_context(request, suppliers=suppliers))


@login_required(login_url='login')
def supplier_create(request):
    require_role(request.user, 'acheteur')
    form = SupplierForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        supplier = form.save()
        create_audit_log(request.user, 'supplier_creation', 'Supplier', supplier.id, f"Fournisseur {supplier.code} cree.")
        messages.success(request, f"Fournisseur {supplier.code} cree.")
        return redirect('/suppliers/')
    return render(request, 'suppliers/form.html', app_context(
        request, form=form, title='Nouveau fournisseur', submit_label='Creer fournisseur'
    ))


@login_required(login_url='login')
def supplier_edit(request, pk):
    require_role(request.user, 'acheteur')
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=supplier)
    if request.method == 'POST' and form.is_valid():
        form.save()
        create_audit_log(request.user, 'supplier_update', 'Supplier', supplier.id, f"Fournisseur {supplier.code} mis a jour.")
        messages.success(request, f"Fournisseur {supplier.code} mis a jour.")
        return redirect('/suppliers/')
    return render(request, 'suppliers/form.html', app_context(
        request, form=form, supplier=supplier, title=f'Modifier {supplier.code}', submit_label='Enregistrer'
    ))


@login_required(login_url='login')
def request_list(request):
    require_role(request.user, 'demandeur', 'validateur', 'acheteur', 'direction')
    requests = PurchaseRequest.objects.select_related('requested_by').prefetch_related('lines__product')
    if request.user.role == 'demandeur':
        requests = requests.filter(requested_by=request.user)
    return render(request, 'requests/list.html', app_context(
        request, requests=requests.order_by('-created_at')
    ))


@login_required(login_url='login')
def request_create(request):
    require_role(request.user, 'demandeur')
    request_form = PurchaseRequestForm(request.POST or None, prefix='request')
    line_form = PurchaseRequestLineForm(request.POST or None, prefix='line')
    if request.method == 'POST' and request_form.is_valid() and line_form.is_valid():
        with transaction.atomic():
            purchase_request = request_form.save(commit=False)
            purchase_request.requested_by = request.user
            purchase_request.department = request.user.department
            purchase_request.save()
            line = line_form.save(commit=False)
            line.request = purchase_request
            if not line.unit_price:
                line.unit_price = line.product.unit_price
            line.save()
            create_audit_log(
                request.user,
                'request_creation',
                'PurchaseRequest',
                purchase_request.id,
                f"Demande {purchase_request.reference} creee.",
            )
            messages.success(request, f"Demande {purchase_request.reference} creee.")
        return redirect(f'/requests/{purchase_request.pk}/')
    return render(request, 'requests/form.html', app_context(
        request,
        request_form=request_form,
        line_form=line_form,
        title='Nouvelle demande achat',
    ))


@login_required(login_url='login')
def request_detail(request, pk):
    purchase_request = get_object_or_404(
        PurchaseRequest.objects.select_related('requested_by').prefetch_related(
            'lines__product__suppliers', 'logs__performed_by', 'supplier_conversations__supplier'
        ),
        pk=pk,
    )
    if request.user.role == 'demandeur' and purchase_request.requested_by_id != request.user.id:
        raise PermissionDenied
    if request.user.role not in ['admin', 'demandeur', 'validateur', 'acheteur', 'direction']:
        raise PermissionDenied
    line_form = PurchaseRequestLineForm()
    decision_form = RequestDecisionForm()
    order_form = CreateOrderForm()
    conversation_form = ConversationOpenForm(purchase_request)
    return render(request, 'requests/detail.html', app_context(
        request,
        purchase_request=purchase_request,
        line_form=line_form,
        decision_form=decision_form,
        order_form=order_form,
        conversation_form=conversation_form,
    ))


@login_required(login_url='login')
def request_add_line(request, pk):
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)
    if purchase_request.status != 'brouillon' or not (purchase_request.requested_by_id == request.user.id or request.user.role == 'admin'):
        raise PermissionDenied
    form = PurchaseRequestLineForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        line = form.save(commit=False)
        line.request = purchase_request
        if not line.unit_price:
            line.unit_price = line.product.unit_price
        line.save()
        messages.success(request, 'Ligne ajoutee.')
    return redirect(f'/requests/{pk}/')


@login_required(login_url='login')
def request_submit(request, pk):
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)
    if purchase_request.status != 'brouillon' or not (purchase_request.requested_by_id == request.user.id or request.user.role == 'admin'):
        raise PermissionDenied
    old_status = purchase_request.status
    purchase_request.status = 'soumis'
    purchase_request.submitted_at = timezone.now()
    purchase_request.save(update_fields=['status', 'submitted_at', 'updated_at'])
    ValidationLog.objects.create(
        request=purchase_request, action='soumission', performed_by=request.user,
        old_status=old_status, new_status='soumis'
    )
    create_audit_log(
        request.user,
        'request_submission',
        'PurchaseRequest',
        purchase_request.id,
        f"Demande {purchase_request.reference} soumise pour validation.",
    )
    notify_roles(
        ['validateur', 'admin'],
        'Nouvelle demande a valider',
        f"{purchase_request.reference} - {purchase_request.title}",
        f"/requests/{purchase_request.pk}/",
        exclude_user=request.user,
    )
    messages.success(request, f"Demande {purchase_request.reference} soumise.")
    return redirect(f'/requests/{pk}/')


@login_required(login_url='login')
def request_validate(request, pk):
    require_role(request.user, 'validateur')
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)
    form = RequestDecisionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid() and purchase_request.status in ['soumis', 'en_validation']:
        old_status = purchase_request.status
        purchase_request.status = 'valide'
        purchase_request.save(update_fields=['status', 'updated_at'])
        ValidationLog.objects.create(
            request=purchase_request, action='validation', performed_by=request.user,
            comment=form.cleaned_data['comment'], old_status=old_status, new_status='valide'
        )
        create_audit_log(
            request.user,
            'request_validation',
            'PurchaseRequest',
            purchase_request.id,
            f"Demande {purchase_request.reference} validee.",
        )
        notify_user(
            purchase_request.requested_by,
            'Demande validee',
            f"{purchase_request.reference} est prete pour la commande.",
            f"/requests/{purchase_request.pk}/",
        )
        notify_roles(
            ['acheteur'],
            'Demande validee a commander',
            f"{purchase_request.reference} - {purchase_request.title}",
            f"/requests/{purchase_request.pk}/",
        )
        messages.success(request, f"Demande {purchase_request.reference} validee.")
    return redirect(f'/requests/{pk}/')


@login_required(login_url='login')
def request_reject(request, pk):
    require_role(request.user, 'validateur')
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)
    form = RequestDecisionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid() and purchase_request.status in ['soumis', 'en_validation']:
        comment = form.cleaned_data['comment']
        if not comment:
            messages.error(request, 'Le rejet exige un commentaire.')
            return redirect(f'/requests/{pk}/')
        old_status = purchase_request.status
        purchase_request.status = 'rejete'
        purchase_request.save(update_fields=['status', 'updated_at'])
        ValidationLog.objects.create(
            request=purchase_request, action='rejet', performed_by=request.user,
            comment=comment, old_status=old_status, new_status='rejete'
        )
        create_audit_log(
            request.user,
            'request_rejection',
            'PurchaseRequest',
            purchase_request.id,
            f"Demande {purchase_request.reference} rejetee.",
        )
        notify_user(
            purchase_request.requested_by,
            'Demande rejetee',
            f"{purchase_request.reference}: {comment}",
            f"/requests/{purchase_request.pk}/",
        )
        messages.success(request, f"Demande {purchase_request.reference} rejetee.")
    return redirect(f'/requests/{pk}/')


@login_required(login_url='login')
def request_create_order(request, pk):
    require_role(request.user, 'acheteur')
    purchase_request = get_object_or_404(PurchaseRequest.objects.prefetch_related('lines__product'), pk=pk)
    form = CreateOrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid() and purchase_request.status == 'valide':
        if hasattr(purchase_request, 'order'):
            messages.error(request, 'Cette demande a deja une commande.')
            return redirect(f'/requests/{pk}/')
        with transaction.atomic():
            order = PurchaseOrder.objects.create(
                purchase_request=purchase_request,
                supplier=form.cleaned_data['supplier'],
                ordered_by=request.user,
                expected_date=form.cleaned_data['expected_date'],
            )
            for line in purchase_request.lines.all():
                PurchaseOrderLine.objects.create(
                    order=order,
                    product=line.product,
                    quantity_ordered=line.quantity,
                    unit_price=line.unit_price or line.product.unit_price,
                )
            purchase_request.status = 'commande'
            purchase_request.save(update_fields=['status', 'updated_at'])
            create_audit_log(
                request.user,
                'order_creation',
                'PurchaseOrder',
                order.id,
                f"Commande {order.reference} creee depuis la demande {purchase_request.reference}.",
            )
            notify_roles(
                ['magasinier'],
                'Nouvelle commande a suivre',
                f"{order.reference} - {order.supplier.name}",
                f"/orders/{order.pk}/",
            )
        messages.success(request, f"Commande {order.reference} creee.")
        return redirect(f'/orders/{order.pk}/')
    messages.error(request, 'Impossible de creer une commande depuis cette demande.')
    return redirect(f'/requests/{pk}/')


def require_supplier_order_access(user, order):
    if user.role == 'fournisseur':
        if not user.supplier_id or order.supplier_id != user.supplier_id:
            raise PermissionDenied
    elif not has_role(user, 'acheteur', 'magasinier', 'direction'):
        raise PermissionDenied


@login_required(login_url='login')
def order_list(request):
    require_role(request.user, 'acheteur', 'magasinier', 'direction', 'fournisseur')
    orders = PurchaseOrder.objects.select_related('supplier', 'ordered_by', 'purchase_request').prefetch_related('order_lines__product')
    if request.user.role == 'fournisseur':
        if not request.user.supplier_id:
            orders = orders.none()
        else:
            orders = orders.filter(supplier=request.user.supplier).exclude(status='brouillon')
    return render(request, 'orders/list.html', app_context(request, orders=orders.order_by('-created_at')))


@login_required(login_url='login')
def order_detail(request, pk):
    order = get_object_or_404(
        PurchaseOrder.objects.select_related('supplier', 'ordered_by', 'purchase_request').prefetch_related(
            'order_lines__product', 'receptions__received_by', 'receptions__lines__order_line__product'
        ),
        pk=pk,
    )
    require_supplier_order_access(request.user, order)
    reception_form = ReceptionForm(order)
    supplier_response_form = SupplierOrderResponseForm(instance=order)
    supplier_status_form = SupplierDeliveryStatusForm(initial={'status': order.supplier_response_status})
    return render(request, 'orders/detail.html', app_context(
        request,
        order=order,
        reception_form=reception_form,
        supplier_response_form=supplier_response_form,
        supplier_status_form=supplier_status_form,
    ))


@login_required(login_url='login')
def order_send(request, pk):
    require_role(request.user, 'acheteur')
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST' and order.status == 'brouillon':
        order.status = 'envoyee'
        order.sent_at = timezone.now()
        order.save(update_fields=['status', 'sent_at', 'updated_at'])
        create_audit_log(request.user, 'order_sent', 'PurchaseOrder', order.id, f"Commande {order.reference} envoyee.")
        for supplier_user in order.supplier.users.filter(is_active=True):
            notify_user(
                supplier_user,
                'Commande recue',
                f"{order.reference} attend votre reponse.",
                f"/orders/{order.pk}/",
            )
        messages.success(request, f"Commande {order.reference} envoyee.")
    return redirect(f'/orders/{pk}/')


@login_required(login_url='login')
def order_supplier_quote(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.user.role != 'fournisseur' or not request.user.supplier_id or order.supplier_id != request.user.supplier_id:
        raise PermissionDenied
    if order.status not in ['envoyee', 'confirmee']:
        messages.error(request, 'Cette commande ne peut pas recevoir une reponse fournisseur.')
        return redirect(f'/orders/{pk}/')
    form = SupplierOrderResponseForm(request.POST or None, instance=order)
    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.supplier_response_status = 'devis_envoye'
        order.supplier_responded_at = timezone.now()
        order.save(update_fields=[
            'supplier_quote_amount', 'supplier_delivery_date',
            'supplier_document_reference', 'supplier_note',
            'supplier_response_status', 'supplier_responded_at', 'updated_at',
        ])
        create_audit_log(request.user, 'supplier_quote', 'PurchaseOrder', order.id, f"Devis fourni pour {order.reference}.")
        notify_roles(
            ['acheteur'],
            'Devis fournisseur recu',
            f"{order.reference} - {order.supplier.name}",
            f"/orders/{order.pk}/",
        )
        messages.success(request, 'Devis fournisseur envoye.')
    return redirect(f'/orders/{pk}/')


@login_required(login_url='login')
def order_supplier_confirm(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.user.role != 'fournisseur' or not request.user.supplier_id or order.supplier_id != request.user.supplier_id:
        raise PermissionDenied
    if request.method == 'POST' and order.status in ['envoyee', 'confirmee']:
        order.status = 'confirmee'
        order.supplier_response_status = 'confirmee'
        order.supplier_responded_at = timezone.now()
        order.save(update_fields=['status', 'supplier_response_status', 'supplier_responded_at', 'updated_at'])
        create_audit_log(request.user, 'supplier_confirmation', 'PurchaseOrder', order.id, f"Commande {order.reference} confirmee par fournisseur.")
        notify_roles(
            ['acheteur', 'magasinier'],
            'Commande confirmee',
            f"{order.reference} - {order.supplier.name}",
            f"/orders/{order.pk}/",
        )
        messages.success(request, f"Commande {order.reference} confirmee.")
    return redirect(f'/orders/{pk}/')


@login_required(login_url='login')
def order_supplier_reject(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.user.role != 'fournisseur' or not request.user.supplier_id or order.supplier_id != request.user.supplier_id:
        raise PermissionDenied
    if request.method == 'POST' and order.status in ['envoyee', 'confirmee']:
        order.status = 'annulee'
        order.supplier_response_status = 'refusee'
        order.supplier_note = request.POST.get('supplier_note', order.supplier_note)
        order.supplier_responded_at = timezone.now()
        order.save(update_fields=['status', 'supplier_response_status', 'supplier_note', 'supplier_responded_at', 'updated_at'])
        create_audit_log(request.user, 'supplier_rejection', 'PurchaseOrder', order.id, f"Commande {order.reference} refusee par fournisseur.")
        notify_roles(
            ['acheteur'],
            'Commande refusee par fournisseur',
            f"{order.reference} - {order.supplier.name}",
            f"/orders/{order.pk}/",
        )
        messages.success(request, f"Commande {order.reference} refusee.")
    return redirect(f'/orders/{pk}/')


@login_required(login_url='login')
def order_supplier_status(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.user.role != 'fournisseur' or not request.user.supplier_id or order.supplier_id != request.user.supplier_id:
        raise PermissionDenied
    form = SupplierDeliveryStatusForm(request.POST or None)
    if request.method == 'POST' and form.is_valid() and order.status in ['confirmee', 'expediee']:
        supplier_status = form.cleaned_data['status']
        order.supplier_response_status = supplier_status
        if supplier_status == 'expediee':
            order.status = 'expediee'
        note = form.cleaned_data.get('note')
        if note:
            order.supplier_note = note
        order.supplier_responded_at = timezone.now()
        order.save(update_fields=['status', 'supplier_response_status', 'supplier_note', 'supplier_responded_at', 'updated_at'])
        create_audit_log(request.user, 'supplier_delivery_update', 'PurchaseOrder', order.id, f"Statut fournisseur {supplier_status} pour {order.reference}.")
        notify_roles(
            ['acheteur', 'magasinier'],
            'Statut livraison mis a jour',
            f"{order.reference}: {order.get_supplier_response_status_display()}",
            f"/orders/{order.pk}/",
        )
        messages.success(request, 'Statut livraison mis a jour.')
    return redirect(f'/orders/{pk}/')


@login_required(login_url='login')
def order_receive(request, pk):
    require_role(request.user, 'magasinier')
    order = get_object_or_404(PurchaseOrder.objects.prefetch_related('order_lines__product'), pk=pk)
    if order.status not in ['envoyee', 'confirmee', 'expediee', 'recue_partielle']:
        messages.error(request, 'Cette commande ne peut pas etre receptionnee.')
        return redirect(f'/orders/{pk}/')
    form = ReceptionForm(order, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order_line = form.cleaned_data['order_line']
        quantity = form.cleaned_data['quantity_received']
        remaining = order_line.quantity_ordered - order_line.quantity_received
        if quantity <= 0 or quantity > remaining:
            messages.error(request, 'Quantite recue invalide.')
            return redirect(f'/orders/{pk}/')
        with transaction.atomic():
            reception = Reception.objects.create(
                order=order,
                received_by=request.user,
                reference=form.cleaned_data['reference'],
                notes=form.cleaned_data['notes'],
            )
            ReceptionLine.objects.create(
                reception=reception,
                order_line=order_line,
                quantity_received=quantity,
                notes=form.cleaned_data['notes'],
            )
            order_line.quantity_received += quantity
            order_line.save(update_fields=['quantity_received'])

            product = order_line.product
            stock_before = product.current_stock
            product.current_stock += quantity
            product.save(update_fields=['current_stock', 'updated_at'])

            StockMovement.objects.create(
                product=product,
                type='entree',
                quantity=quantity,
                stock_before=stock_before,
                stock_after=product.current_stock,
                reference=reception.reference or order.reference,
                reason=f"Reception {reception.reference or reception.id}",
                performed_by=request.user,
            )
            create_audit_log(
                request.user,
                'reception_validation',
                'Reception',
                reception.id,
                f"Reception {reception.reference or reception.id} pour {order.reference}.",
            )
            create_audit_log(
                request.user,
                'stock_update',
                'Product',
                product.id,
                f"Stock {product.code}: {stock_before} -> {product.current_stock}.",
            )

            has_remaining_lines = order.order_lines.filter(
                quantity_received__lt=F('quantity_ordered')
            ).exists()
            if not has_remaining_lines:
                order.status = 'recue'
            else:
                order.status = 'recue_partielle'
            order.save(update_fields=['status', 'updated_at'])
            notify_roles(
                ['acheteur'],
                'Reception enregistree',
                f"{order.reference} - {product.name} ({quantity})",
                f"/orders/{order.pk}/",
            )
            if order.purchase_request_id:
                notify_user(
                    order.purchase_request.requested_by,
                    'Reception achat',
                    f"{product.name} receptionne pour {order.purchase_request.reference}.",
                    f"/orders/{order.pk}/",
                )
        messages.success(request, f"Reception enregistree pour {product.name}.")
    return redirect(f'/orders/{pk}/')


@login_required(login_url='login')
def stock_dashboard(request):
    require_role(request.user, 'magasinier', 'direction')
    movements = StockMovement.objects.select_related('product', 'performed_by').order_by('-created_at')[:30]
    critical_products = Product.objects.select_related('category').filter(
        Q(current_stock__lte=F('min_stock')) | Q(is_active=False)
    ).order_by('current_stock')
    form = StockAdjustmentForm()
    return render(request, 'stock/dashboard.html', app_context(
        request, movements=movements, critical_products=critical_products, form=form
    ))


@login_required(login_url='login')
def stock_adjust(request):
    require_role(request.user, 'magasinier')
    form = StockAdjustmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        quantity = form.cleaned_data['quantity']
        move_type = form.cleaned_data['type']
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=form.cleaned_data['product'].pk)
            stock_before = product.current_stock
            if move_type == 'entree':
                product.current_stock += quantity
            elif move_type == 'sortie':
                if product.current_stock < quantity:
                    messages.error(request, 'Stock insuffisant.')
                    return redirect('/stock/')
                product.current_stock -= quantity
            elif move_type == 'ajustement':
                product.current_stock = quantity
            product.save(update_fields=['current_stock', 'updated_at'])
            StockMovement.objects.create(
                product=product,
                type=move_type,
                quantity=quantity,
                stock_before=stock_before,
                stock_after=product.current_stock,
                reference=form.cleaned_data['reference'],
                reason=form.cleaned_data['reason'],
                performed_by=request.user,
            )
            create_audit_log(
                request.user,
                'stock_update',
                'Product',
                product.id,
                f"Mouvement {move_type} sur {product.code}: {stock_before} -> {product.current_stock}.",
            )
            if product.current_stock <= product.min_stock:
                notify_roles(
                    ['acheteur', 'magasinier'],
                    'Alerte stock critique',
                    f"{product.code} - {product.name}: stock {product.current_stock}, seuil {product.min_stock}.",
                    f"/products/?status={product.stock_status}",
                    exclude_user=request.user,
                )
        messages.success(request, f"Stock de {product.name} mis a jour.")
    return redirect('/stock/')


def require_conversation_access(user, conversation, write=False):
    if user.role == 'demandeur':
        if conversation.demandeur_id != user.id:
            raise PermissionDenied
        return
    if user.role == 'fournisseur':
        if not user.supplier_id or conversation.supplier_id != user.supplier_id:
            raise PermissionDenied
        return
    if not write and has_role(user, 'acheteur'):
        return
    raise PermissionDenied


@login_required(login_url='login')
def conversation_list(request):
    require_role(request.user, 'demandeur', 'acheteur', 'fournisseur')
    conversations = SupplierRequestConversation.objects.select_related(
        'purchase_request', 'request_line__product', 'supplier', 'demandeur'
    ).prefetch_related('messages').order_by('-updated_at')
    if request.user.role == 'demandeur':
        conversations = conversations.filter(demandeur=request.user)
    elif request.user.role == 'fournisseur':
        if not request.user.supplier_id:
            conversations = conversations.none()
        else:
            conversations = conversations.filter(supplier=request.user.supplier)
    return render(request, 'conversations/list.html', app_context(request, conversations=conversations))


@login_required(login_url='login')
def conversation_detail(request, pk):
    conversation = get_object_or_404(
        SupplierRequestConversation.objects.select_related(
            'purchase_request', 'request_line__product', 'supplier', 'demandeur'
        ).prefetch_related('messages__sender_user', 'messages__sender_supplier'),
        pk=pk,
    )
    require_conversation_access(request.user, conversation)
    form = ConversationReplyForm()
    can_reply_conversation = request.user.role in ['demandeur', 'fournisseur']
    return render(request, 'conversations/detail.html', app_context(
        request,
        conversation=conversation,
        form=form,
        can_reply_conversation=can_reply_conversation,
    ))


@login_required(login_url='login')
def conversation_reply(request, pk):
    conversation = get_object_or_404(SupplierRequestConversation, pk=pk)
    if conversation.status == 'cloturee':
        messages.error(request, 'Conversation cloturee.')
        return redirect(f'/conversations/{pk}/')
    require_conversation_access(request.user, conversation, write=True)
    form = ConversationReplyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        message = form.save(commit=False)
        message.conversation = conversation
        if request.user.role == 'demandeur':
            message.sender_type = 'demandeur'
            message.sender_user = request.user
        else:
            message.sender_type = 'fournisseur'
            message.sender_supplier = request.user.supplier
        message.save()
        create_audit_log(
            request.user,
            'supplier_conversation_message',
            'SupplierRequestConversation',
            conversation.id,
            f"Message ajoute dans la conversation {conversation.subject}.",
        )
        if message.sender_type == 'demandeur':
            for supplier_user in conversation.supplier.users.filter(is_active=True):
                notify_user(supplier_user, 'Nouveau message demandeur', conversation.subject, f"/conversations/{conversation.pk}/")
        else:
            notify_user(conversation.demandeur, 'Nouveau message fournisseur', conversation.subject, f"/conversations/{conversation.pk}/")
        messages.success(request, 'Message ajoute.')
    return redirect(f'/conversations/{pk}/')


@login_required(login_url='login')
def request_open_conversation(request, pk):
    purchase_request = get_object_or_404(PurchaseRequest.objects.prefetch_related('lines__product'), pk=pk)
    if request.user.role != 'demandeur':
        raise PermissionDenied
    if purchase_request.requested_by_id != request.user.id:
        raise PermissionDenied
    form = ConversationOpenForm(purchase_request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        line = form.cleaned_data['request_line']
        supplier = form.cleaned_data['supplier']
        trigger = SupplierRequestConversation.trigger_for_product(line.product)
        conversation = SupplierRequestConversation.objects.filter(
            request_line=line,
            supplier=supplier,
            status__in=['ouverte', 'en_cours']
        ).first()
        created = conversation is None
        if created:
            conversation = SupplierRequestConversation.objects.create(
                purchase_request=purchase_request,
                demandeur=purchase_request.requested_by,
                trigger=trigger,
                request_line=line,
                supplier=supplier,
            )
        if created:
            SupplierRequestMessage.objects.create(
                conversation=conversation,
                sender_type='demandeur',
                sender_user=purchase_request.requested_by,
                body=form.cleaned_data['body'],
            )
            create_audit_log(
                request.user,
                'supplier_conversation_opened',
                'SupplierRequestConversation',
                conversation.id,
                f"Conversation ouverte avec {supplier.name} pour {line.product.name}.",
            )
            for supplier_user in supplier.users.filter(is_active=True):
                notify_user(
                    supplier_user,
                    'Conversation fournisseur ouverte',
                    conversation.subject,
                    f"/conversations/{conversation.pk}/",
                )
            messages.success(request, 'Conversation fournisseur ouverte.')
        else:
            messages.info(request, 'Une conversation ouverte existe deja pour ce fournisseur et cette ligne.')
        return redirect(f'/conversations/{conversation.pk}/')
    messages.error(request, 'Impossible d ouvrir la conversation.')
    return redirect(f'/requests/{pk}/')
