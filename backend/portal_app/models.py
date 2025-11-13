from django.db import models
from django.contrib.auth.models import User # User standard di Django

# === Modelli GESTITI da Django (managed = True) ===
# Django creerà e gestirà queste tabelle.

class MirthMetrics(models.Model):
    # Relazione alla tabella 'gateways' (tramite il suo gtw_uid)
    gateway = models.ForeignKey(
        'Gateways',
        to_field='gtw_uid',
        on_delete=models.CASCADE,
        db_column='gateway_uid'
    )
    gateway_timestamp = models.DateTimeField(db_index=True)
    channel_name = models.CharField(max_length=255, db_index=True)
    channel_id = models.CharField(max_length=50)
    received = models.IntegerField(default=0)
    sent = models.IntegerField(default=0)
    error = models.IntegerField(default=0)
    filtered = models.IntegerField(default=0)
    queued = models.IntegerField(default=0)

    class Meta:
        managed = True # Default, ma lo esplicito
        db_table = 'mirth_metrics'
        ordering = ['-gateway_timestamp']

class CheckStatusMetrics(models.Model):
    gateway = models.ForeignKey(
        'Gateways',
        to_field='gtw_uid',
        on_delete=models.CASCADE,
        db_column='gateway_uid'
    )
    gateway_timestamp = models.DateTimeField(db_index=True)
    check_name = models.CharField(max_length=255, db_index=True)
    level = models.CharField(max_length=10)
    description = models.TextField(blank=True, null=True)
    actual_value = models.IntegerField()
    limit_value = models.IntegerField()
    operator = models.CharField(max_length=5)
    query_time_sec = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'check_status_metrics'
        ordering = ['-gateway_timestamp']

class GatewayPendingActions(models.Model):
    gateway = models.ForeignKey(
        'Gateways',
        to_field='gtw_uid',
        on_delete=models.CASCADE,
        db_column='gateway_uid'
    )
    action_command = models.CharField(max_length=100)
    payload = models.JSONField(blank=True, null=True)
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('DELIVERED', 'Delivered'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    # Tracciamento dell'utente che ha creato l'azione
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        db_table = 'gateway_pending_actions'
        ordering = ['-created_at']


# === Modelli NON GESTITI (managed = False) ===
# Django leggerà da queste tabelle, ma non proverà
# MAI a modificarle, crearle o eliminarle.

class Channels(models.Model):
    pk = models.AutoField(primary_key=True)
    filesystem_fk = models.SmallIntegerField(blank=True, null=True)
    channel_doc = models.CharField(unique=True, max_length=14)
    kr_ad_id = models.CharField(max_length=5)
    cod_scarto = models.CharField(max_length=10)
    cod_firma = models.CharField(max_length=3, blank=True, null=True)
    doc_base_path = models.CharField(max_length=256)
    type_close = models.CharField(max_length=1)
    time_close_interval = models.IntegerField(blank=True, null=True)
    close_file_size = models.FloatField(blank=True, null=True)
    hour_close = models.CharField(max_length=2, blank=True, null=True)
    name = models.CharField(max_length=160, blank=True, null=True)
    in_root = models.CharField(max_length=255, blank=True, null=True)
    copy1path = models.CharField(max_length=255, blank=True, null=True)
    copy1type = models.CharField(max_length=255, blank=True, null=True)
    copy2path = models.CharField(max_length=255, blank=True, null=True)
    copy2type = models.CharField(max_length=255, blank=True, null=True)
    channel_type = models.CharField(max_length=255, blank=True, null=True)
    db_type = models.CharField(max_length=255, blank=True, null=True)
    active = models.SmallIntegerField(blank=True, null=True)
    dicom_site = models.CharField(max_length=128, blank=True, null=True)
    xsd = models.CharField(max_length=36, blank=True, null=True)
    doc_extension = models.CharField(max_length=30, blank=True, null=True)
    verify_sign = models.SmallIntegerField(blank=True, null=True)
    node_fk = models.IntegerField()
    gateway_fk = models.IntegerField(blank=True, null=True)
    tmp_sync_path = models.CharField(max_length=64, blank=True, null=True)
    activation_date = models.DateTimeField(blank=True, null=True)
    to_update = models.SmallIntegerField()
    max_rows_pipe = models.IntegerField(blank=True, null=True)
    to_delete = models.SmallIntegerField(blank=True, null=True)
    max_size_gb = models.SmallIntegerField(default=5)
    n_fields = models.IntegerField(blank=True, null=True)
    default_fields = models.TextField(blank=True, null=True)
    xsd_schema = models.TextField(blank=True, null=True)
    dictionary = models.TextField(blank=True, null=True)
    lastupdate_time = models.DateTimeField(blank=True, null=True)
    to_crypt = models.SmallIntegerField()
    adm_update = models.IntegerField()
    xml_modify = models.TextField(blank=True, null=True)
    report_include = models.BooleanField(blank=True, null=True)
    report_note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'channels'

class KfeLogEvent(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, blank=True, null=True)
    node_fk = models.SmallIntegerField(blank=True, null=True)
    action = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=10, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    node_type = models.CharField(max_length=6, blank=True, null=True)
    ip_address = models.CharField(max_length=16, blank=True, null=True)
    doc_channel = models.CharField(max_length=14, blank=True, null=True)
    attach = models.TextField(blank=True, null=True)
    external_id = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kfe_log_event'
        ordering = ['-datetime'] # Ordine di default

class Gateways(models.Model):
    pk = models.AutoField(primary_key=True)
    gtw_name = models.CharField(max_length=30, blank=True, null=True)
    gtw_uid = models.CharField(unique=True, max_length=64, blank=True, null=True)
    gtw_password = models.CharField(max_length=16, blank=True, null=True)
    node_fk = models.IntegerField(blank=True, null=True)
    last_ip_from = models.CharField(max_length=32, blank=True, null=True)
    last_date_call = models.DateTimeField(blank=True, null=True)
    remote_port = models.IntegerField(blank=True, null=True)
    forward_port = models.IntegerField(blank=True, null=True)
    activate_service = models.IntegerField(blank=True, null=True)
    sw_version = models.CharField(max_length=5, blank=True, null=True)
    gateway_description = models.CharField(max_length=256, blank=True, null=True)
    current_version = models.CharField(max_length=5, blank=True, null=True)
    gateway_endpoint = models.TextField(blank=True, null=True)
    customer_email = models.JSONField(blank=True, null=True)
    report_configuration = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gateways'

class ExportPda(models.Model):
    pk = models.AutoField(primary_key=True)
    pda_id = models.TextField(blank=True, null=True)
    pdv_generated = models.TextField(blank=True, null=True)
    pdv_zip_path = models.CharField(max_length=128, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    channel_id = models.CharField(max_length=32, blank=True, null=True)
    pdv_id = models.TextField(blank=True, null=True)
    annotation = models.TextField(blank=True, null=True)
    json_pdv = models.TextField(blank=True, null=True)
    nr_doc = models.IntegerField(blank=True, null=True)
    remote_gtw_pk = models.IntegerField(blank=True, null=True)
    remote_ack = models.TextField(blank=True, null=True)
    pda_size = models.BigIntegerField(blank=True, null=True)
    sess_id = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'export_pda'

class PdaStatsV6(models.Model):
    lot_code = models.CharField(primary_key=True, max_length=255)
    lot_date = models.DateField(blank=True, null=True)
    lot_pipe = models.CharField(max_length=255, blank=True, null=True)
    lot_nr_doc = models.IntegerField(blank=True, null=True)
    lot_nr_pdv = models.IntegerField(blank=True, null=True)
    lot_nr_doc_billed = models.IntegerField(blank=True, null=True)
    lot_first_doc_date = models.DateField(blank=True, null=True)
    lot_last_doc_date = models.DateField(blank=True, null=True)
    lot_size_doc = models.BigIntegerField(blank=True, null=True)
    doc_channel = models.CharField(max_length=64, blank=True, null=True)
    date_billing = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    kr_ad_id = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pda_stats_v6'

class ErroriDaImportare(models.Model):
    categoria = models.CharField(max_length=16)
    nome = models.CharField(max_length=64)
    descrizione = models.CharField(max_length=256)
    condizione = models.CharField(max_length=256)
    column5 = models.CharField(db_column='Column5', max_length=8)  # 'Column5'
    column6 = models.CharField(db_column='Column6', max_length=1)  # 'Column6'
    cat = models.CharField(max_length=32)
    raw = models.CharField(max_length=512)

    class Meta:
        managed = False
        db_table = 'errori_da_importare'
        # Questa tabella non ha una Primary Key definita in SQL.
        # Per Django, potremmo doverne definire una fittizia o
        # aggiungere un 'id = models.AutoField(primary_key=True)' se
        # sappiamo che le righe sono univoche. Per ora, lo lasciamo così.
        # Se Django si lamenta, la soluzione migliore è aggiungere
        # 'id = models.BigAutoField(primary_key=True)' QUI
        # (non nel DB) e Django la userà per la lettura.
