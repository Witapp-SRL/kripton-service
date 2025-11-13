from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Il router crea automaticamente gli URL per i ViewSet
router = DefaultRouter()
router.register(r'gateways', views.GatewayViewSet)
router.register(r'channels', views.ChannelViewSet)
router.register(r'logs', views.KfeLogEventViewSet)
# Aggiungere altri router per PdaStats, ExportPda, etc.

urlpatterns = [
    # Rotte automatiche del router
    path('', include(router.urls)),
    
    # Endpoint di Ingestion (pubblico, ma da proteggere)
    path('ingest-metrics/', views.MetricsIngestionView.as_view(), name='ingest-metrics'),
    
    # Endpoint della Dashboard
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Endpoint per Grafici
    path('metrics/mirth/history/', views.MirthMetricsHistoryView.as_view(), name='mirth-history'),
    
    # Endpoint Azioni e Integrazioni (protetti da Auth)
    path('actions/create/', views.CreateActionView.as_view(), name='create-action'),
    path('integrations/mantis/create-ticket/', views.MantisTicketView.as_view(), name='mantis-create'),
]
