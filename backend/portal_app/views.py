import os
import requests
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from .models import (
    Gateways, KfeLogEvent, Channels, ExportPda, PdaStatsV6, ErroriDaImportare,
    MirthMetrics, CheckStatusMetrics, GatewayPendingActions
)
from .serializers import (
    GatewaySerializer, KfeLogEventSerializer, ChannelSerializer, ExportPdaSerializer,
    PdaStatsV6Serializer, ErroriDaImportareSerializer, MirthMetricsSerializer,
    CheckStatusMetricsSerializer, GatewayPendingActionSerializer,
    CreateActionSerializer, MantisTicketSerializer
)

# --- API di Ingestion (Accesso consentito solo ai Gateway) ---
# NB: Questa API dovrebbe avere un suo sistema di autenticazione
# (es. API Key) diverso da quello degli utenti. Per ora, usiamo AllowAny
# ma in produzione andrebbe blindata.

class MetricsIngestionView(APIView):
    permission_classes = [AllowAny] # CAMBIARE in produzione con un TokenAuth
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            gtw_uid = data['gtw_uid']
            timestamp = data['timestamp']
            
            # 1. Trova il gateway
            try:
                gateway = Gateways.objects.get(gtw_uid=gtw_uid)
            except Gateways.DoesNotExist:
                return Response({"error": "Gateway non valido"}, status=status.HTTP_404_NOT_FOUND)

            # 2. Salva Mirth Metrics
            mirth_metrics_data = data.get('mirth', {})
            mirth_objs = [
                MirthMetrics(
                    gateway=gateway,
                    gateway_timestamp=timestamp,
                    channel_name=name,
                    channel_id=details['channelId'],
                    received=metrics['received'], sent=metrics['sent'],
                    error=metrics['error'], filtered=metrics['filtered'],
                    queued=metrics['queued']
                )
                for name, details in mirth_metrics_data.items()
                for metrics in [details['metrics']]
            ]
            MirthMetrics.objects.bulk_create(mirth_objs)

            # 3. Salva Check Status Metrics
            check_status_data = data.get('CheckStatus', {})
            check_objs = [
                CheckStatusMetrics(
                    gateway=gateway,
                    gateway_timestamp=timestamp,
                    check_name=name,
                    level=details['level'],
                    description=details.get('description', ''),
                    actual_value=details['act'],
                    limit_value=details['limit'],
                    operator=details['operator'],
                    query_time_sec=details.get('query_time_sec')
                )
                for name, details in check_status_data.items()
            ]
            CheckStatusMetrics.objects.bulk_create(check_objs)

            # 4. Aggiorna 'last_date_call' sul gateway
            gateway.last_date_call = timezone.now()
            gateway.save(update_fields=['last_date_call'])

            # 5. Cerca azioni in sospeso per questo gateway
            pending_actions = GatewayPendingActions.objects.filter(
                gateway=gateway, 
                status='PENDING'
            )
            actions_data = GatewayPendingActionSerializer(pending_actions, many=True).data
            
            # Segna le azioni come "Consegnate"
            action_ids = [a['id'] for a in actions_data]
            GatewayPendingActions.objects.filter(id__in=action_ids).update(status='DELIVERED')

            return Response({
                "status": "success", 
                "mirth_records": len(mirth_objs), 
                "check_records": len(check_objs),
                "pending_actions": actions_data # Invia i comandi al gateway
            }, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response({"error": f"Campo JSON mancante: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Errore durante l'elaborazione: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- API per la Dashboard (Solo Utenti Autenticati) ---

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Endpoint aggregato che raccoglie tutti i KPI per la dashboard.
        """
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        # 1. KPI Gateways
        active_gateways = Gateways.objects.filter(
            last_date_call__gte=now - timedelta(minutes=15) # Attivo negli ultimi 15 min
        ).count()
        total_gateways = Gateways.objects.count()

        # 2. KPI Canali
        channels_to_update = Channels.objects.filter(to_update=1).count()
        channels_to_delete = Channels.objects.filter(to_delete=1).count()

        # 3. KPI Errori (ultime 24h)
        errors_last_24h = KfeLogEvent.objects.filter(
            datetime__gte=last_24h,
            level__in=['ERROR', 'WARNING'] # Includiamo entrambi
        ).count()
        
        # 4. KPI Errori da Importare
        import_errors_count = ErroriDaImportare.objects.count()

        # 5. Stato Ultime Esportazioni
        recent_exports = ExportPda.objects.order_by('-insert_time')[:5]
        
        # 6. Errori per Batch (ultime 24h)
        # Questo è costoso, potremmo volerlo in un'API separata
        errors_by_batch = KfeLogEvent.objects.filter(
            datetime__gte=last_24h, 
            level='ERROR'
        ).values('description') # Prendiamo la descrizione
        
        # Semplice aggregazione in Python (per l'API con `batch_name`)
        batch_counts = {}
        for log in errors_by_batch:
            desc = log['description']
            if desc:
                batch_name = desc.split(' - ', 1)[0].strip()
                batch_counts[batch_name] = batch_counts.get(batch_name, 0) + 1
        
        # Ordina e prendi i top 5
        top_5_batch_errors = sorted(batch_counts.items(), key=lambda item: item[1], reverse=True)[:5]

        return Response({
            "kpi": {
                "active_gateways": active_gateways,
                "total_gateways": total_gateways,
                "channels_to_update": channels_to_update,
                "channels_to_delete": channels_to_delete,
                "errors_last_24h": errors_last_24h,
                "import_errors_count": import_errors_count,
            },
            "recent_exports": ExportPdaSerializer(recent_exports, many=True).data,
            "top_batch_errors": top_5_batch_errors,
        })

class CreateActionView(APIView):
    """
    Crea una nuova azione in sospeso per un gateway.
    """
    permission_classes = [IsAuthenticated] # Solo utenti loggati (e autorizzati)

    def post(self, request, *args, **kwargs):
        serializer = CreateActionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                gateway = Gateways.objects.get(gtw_uid=data['gtw_uid'])
                
                GatewayPendingActions.objects.create(
                    gateway=gateway,
                    action_command=data['action_command'],
                    payload=data.get('payload'),
                    created_by=request.user # Tracciamento utente!
                )
                return Response({"status": "azione creata"}, status=status.HTTP_201_CREATED)
            except Gateways.DoesNotExist:
                return Response({"error": "Gateway non trovato"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MantisTicketView(APIView):
    """
    Proxy API per creare un ticket in MantisBT.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MantisTicketSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        mantis_data = serializer.validated_data
        
        # Prendi l'API Key e URL dal settings/.env
        api_key = os.getenv('MANTIS_API_KEY')
        api_url = os.getenv('MANTIS_API_URL') + '/issues'
        
        if not api_key or not api_url:
            return Response({"error": "Configurazione Mantis mancante sul server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        
        # Struttura il payload come richiesto da Mantis (esempio)
        payload = {
            "summary": mantis_data['summary'],
            "description": mantis_data['description'],
            # "project": {"id": mantis_data['project_id']},
            # "category": {"id": mantis_data['category_id']},
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status() # Lancia un errore se la richiesta fallisce
            
            # Traccia l'azione (es. loggandola)
            print(f"L'utente {request.user.username} ha creato il ticket Mantis {response.json().get('issue', {}).get('id')}")
            
            return Response(response.json(), status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Errore chiamata Mantis: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

# --- ViewSet per Lettura Dati (Read-Only) ---

class GatewayViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Gateways.objects.all()
    serializer_class = GatewaySerializer
    permission_classes = [IsAuthenticated]

class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Channels.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]
    
    # Esempio di filtro: /api/channels/?active=1
    def get_queryset(self):
        queryset = Channels.objects.all()
        active = self.request.query_params.get('active')
        if active is not None:
            queryset = queryset.filter(active=active)
        return queryset

class KfeLogEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = KfeLogEvent.objects.all()
    serializer_class = KfeLogEventSerializer
    permission_classes = [IsAuthenticated]
    
    # Esempio di filtri: /api/logs/?level=ERROR&search=xds
    def get_queryset(self):
        queryset = KfeLogEvent.objects.all().order_by('-datetime') # Sempre ordinati
        level = self.request.query_params.get('level')
        search = self.request.query_params.get('search')
        
        if level:
            queryset = queryset.filter(level=level)
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) | 
                Q(doc_channel__icontains=search)
            )
        return queryset

class MirthMetricsHistoryView(APIView):
    """
    Endpoint per i grafici:
    GET /api/metrics/mirth/history/?gateway_uid=...&channel_name=...&range=24h
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        gtw_uid = request.query_params.get('gateway_uid')
        channel_name = request.query_params.get('channel_name')
        range_hours = request.query_params.get('range', '24h') # '24h', '7d'

        if not gtw_uid or not channel_name:
            return Response({"error": "gateway_uid e channel_name sono richiesti"}, status=400)

        # Calcola intervallo temporale
        if range_hours == '7d':
            start_date = timezone.now() - timedelta(days=7)
        else:
            start_date = timezone.now() - timedelta(hours=24)
            
        # TODO: Aggiungere aggregazione per non restituire troppi punti
        # (es. media oraria)
        
        queryset = MirthMetrics.objects.filter(
            gateway__gtw_uid=gtw_uid,
            channel_name=channel_name,
            gateway_timestamp__gte=start_date
        ).order_by('gateway_timestamp')
        
        serializer = MirthMetricsSerializer(queryset, many=True)
        return Response(serializer.data)
        
# Aggiungere ViewSet simili per ExportPda, PdaStatsV6, ecc.
