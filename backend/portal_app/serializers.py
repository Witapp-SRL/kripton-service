from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Gateways, KfeLogEvent, Channels, ExportPda, PdaStatsV6, ErroriDaImportare,
    MirthMetrics, CheckStatusMetrics, GatewayPendingActions
)

# Serializer per l'utente (per tracciamento)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

# --- Serializers per Dati Esistenti (Read-Only) ---

class GatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateways
        fields = [
            'pk', 'gtw_name', 'gtw_uid', 'last_ip_from', 'last_date_call',
            'sw_version', 'current_version', 'gateway_description', 'activate_service'
        ]

class KfeLogEventSerializer(serializers.ModelSerializer):
    # Il nostro campo virtuale per estrarre il nome del batch
    batch_name = serializers.SerializerMethodField()

    class Meta:
        model = KfeLogEvent
        fields = [
            'id', 'datetime', 'level', 'action', 'batch_name', 
            'description', 'node_type', 'ip_address', 'doc_channel'
        ]

    def get_batch_name(self, obj):
        """
        Estrae la parte della descrizione prima del " - ".
        Esempio: "xds_cron - ((93vl)) Errore..." -> "xds_cron"
        """
        if obj.description:
            try:
                # Splitta la stringa al primo " - " e prende la parte [0]
                return obj.description.split(' - ', 1)[0].strip()
            except Exception:
                return None
        return None

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channels
        fields = ['pk', 'name', 'channel_doc', 'active', 'to_update', 'to_delete', 'lastupdate_time']

class ExportPdaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportPda
        fields = '__all__'

class PdaStatsV6Serializer(serializers.ModelSerializer):
    class Meta:
        model = PdaStatsV6
        fields = '__all__'

class ErroriDaImportareSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErroriDaImportare
        fields = '__all__'


# --- Serializers per Dati Nuovi (Metriche e Azioni) ---

class MirthMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirthMetrics
        fields = '__all__'

class CheckStatusMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckStatusMetrics
        fields = '__all__'

class GatewayPendingActionSerializer(serializers.ModelSerializer):
    # Mostra i dettagli dell'utente, non solo l'ID
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = GatewayPendingActions
        fields = [
            'id', 'gateway', 'action_command', 'payload', 'status', 
            'created_at', 'created_by', 'updated_at'
        ]
        read_only_fields = ['created_by', 'status']

# Serializer per la creazione dell'azione
class CreateActionSerializer(serializers.Serializer):
    gtw_uid = serializers.CharField(max_length=64)
    action_command = serializers.CharField(max_length=100)
    payload = serializers.JSONField(required=False)

# Serializer per la creazione del ticket Mantis
class MantisTicketSerializer(serializers.Serializer):
    summary = serializers.CharField(max_length=200)
    description = serializers.CharField()
    # Aggiungi altri campi richiesti da Mantis (es. project, category)
    # project_id = serializers.IntegerField()
    # category_id = serializers.IntegerField()
