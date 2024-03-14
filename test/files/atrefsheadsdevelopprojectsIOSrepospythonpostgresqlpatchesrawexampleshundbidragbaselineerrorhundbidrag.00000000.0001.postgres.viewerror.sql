-- The purpose of this script is to test error handling during baseline execution
CREATE OR REPLACE VIEW public.arende_beslut
 AS
 SELECT a.kortnr,
    b.beslutsdat,
    b.omfattning
   FROM arende a
     JOIN beslut b ON a.arendeid = b.arendeid;

ALTER TABLE public.arende_beslut
    OWNER TO hundbidrag;