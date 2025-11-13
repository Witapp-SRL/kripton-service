-- Tabella per le metriche dei canali (dal blocco "mirth")
CREATE TABLE public.mirth_metrics (
    pk bigserial NOT NULL,
    
    -- Chiave esterna che collega al gateway
    -- Usa 'gtw_uid' che è già un indice univoco sulla tabella 'gateways'
    gateway_uid varchar(64) NOT NULL, 
    
    -- Timestamp del report (dal JSON)
    gateway_timestamp timestamptz NOT NULL, 
    
    -- Dati della metrica
    channel_name varchar(255) NOT NULL,
    channel_id varchar(50) NOT NULL,
    received int4 NOT NULL DEFAULT 0,
    sent int4 NOT NULL DEFAULT 0,
    error int4 NOT NULL DEFAULT 0,
    filtered int4 NOT NULL DEFAULT 0,
    "queued" int4 NOT NULL DEFAULT 0,

    CONSTRAINT mirth_metrics_pkey PRIMARY KEY (pk),
    CONSTRAINT fk_gateway_uid 
        FOREIGN KEY (gateway_uid) 
        REFERENCES public.gateways(gtw_uid) 
        ON DELETE CASCADE
);

-- Indici per velocizzare le query (fondamentali per le dashboard)
CREATE INDEX idx_mirth_metrics_timestamp ON public.mirth_metrics(gateway_timestamp DESC);
CREATE INDEX idx_mirth_metrics_gateway_uid ON public.mirth_metrics(gateway_uid);
CREATE INDEX idx_mirth_metrics_channel_name ON public.mirth_metrics(channel_name);

-- Tabella per le metriche di "CheckStatus"
CREATE TABLE public.check_status_metrics (
    pk bigserial NOT NULL,
    
    -- Chiave esterna
    gateway_uid varchar(64) NOT NULL,
    
    -- Timestamp del report
    gateway_timestamp timestamptz NOT NULL,
    
    -- Dati della metrica
    check_name varchar(255) NOT NULL,
    level varchar(10) NOT NULL,
    description text NULL,
    actual_value int4 NOT NULL,
    limit_value int4 NOT NULL,
    operator varchar(5) NOT NULL,
    query_time_sec float4 NULL,

    CONSTRAINT check_status_metrics_pkey PRIMARY KEY (pk),
    CONSTRAINT fk_gateway_uid 
        FOREIGN KEY (gateway_uid) 
        REFERENCES public.gateways(gtw_uid) 
        ON DELETE CASCADE
);

-- Indici
CREATE INDEX idx_check_status_timestamp ON public.check_status_metrics(gateway_timestamp DESC);
CREATE INDEX idx_check_status_gateway_uid ON public.check_status_metrics(gateway_uid);
CREATE INDEX idx_check_status_check_name ON public.check_status_metrics(check_name);
