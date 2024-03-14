--
-- PostgreSQL database dump
--

-- Dumped from database version 12.1
-- Dumped by pg_dump version 12.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: hundbidrag; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE hundbidrag WITH TEMPLATE = template0 ENCODING = 'UTF8';
\set pwd `bash -c "echo $PATCHES_POSTGRESQL_TEMPORARY_USER_PASSWORD"`
create user hundbidrag
    createdb
    encrypted password :'pwd';

ALTER DATABASE hundbidrag OWNER TO postgres;

\connect hundbidrag

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: arende; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.arende (
    arendeid numeric(12,0) NOT NULL,
    kundid numeric(13,0) NOT NULL,
    berforlossningdat date,
    anmalandat date,
    forsakradforarbete smallint,
    ansokanunderskriven smallint,
    egenforetagare smallint,
    avstangd smallint,
    arbplatsbesok smallint,
    faststalldsgi character varying(20),
    avslutsanled character varying(20),
    avslutsdat date,
    tstamp date NOT NULL
);


ALTER TABLE public.arende OWNER TO hundbidrag;

--
-- Name: beslut; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.beslut (
    arendeid numeric(12,0) NOT NULL,
    beslutsdat date NOT NULL,
    fromdat date NOT NULL,
    tomdat date NOT NULL,
    omfattning smallint NOT NULL,
    beslutstyp smallint,
    avstangdfromdat date,
    tstamp date NOT NULL
);


ALTER TABLE public.beslut OWNER TO hundbidrag;

--
-- Name: periodforsakran; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.periodforsakran (
    arendeid numeric(12,0) NOT NULL,
    ankomstdat date NOT NULL,
    fromdat date NOT NULL,
    tomdat date NOT NULL,
    omfattning smallint NOT NULL,
    tstamp date NOT NULL
);


ALTER TABLE public.periodforsakran OWNER TO hundbidrag;

--
-- Name: utbetperiod; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.utbetperiod (
    arendeid numeric(12,0) NOT NULL,
    utbetalningsdat date NOT NULL,
    utbettyp smallint NOT NULL,
    omfattning smallint NOT NULL,
    utbetfromdat date NOT NULL,
    utbettomdat date,
    antaldagarperiod smallint,
    antaldagborttag smallint,
    utbetantaldagsum smallint,
    utbetbel numeric(8,2),
    manuellhantering smallint,
    tpdat date,
    tstamp date NOT NULL
);


ALTER TABLE public.utbetperiod OWNER TO hundbidrag;

--
-- Name: arende pk_arende; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.arende
    ADD CONSTRAINT pk_arende PRIMARY KEY (arendeid);


--
-- Name: beslut pk_beslut; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beslut
    ADD CONSTRAINT pk_beslut PRIMARY KEY (arendeid, beslutsdat, fromdat, tomdat, omfattning);


--
-- Name: periodforsakran pk_periodforsakran; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.periodforsakran
    ADD CONSTRAINT pk_periodforsakran PRIMARY KEY (arendeid, ankomstdat, fromdat, tomdat, omfattning);


--
-- Name: utbetperiod pk_utbetperiod; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utbetperiod
    ADD CONSTRAINT pk_utbetperiod PRIMARY KEY (arendeid, utbetalningsdat, utbettyp, omfattning, utbetfromdat);


--
-- Name: beslut xy_beslut_beslut_ar_arende; Type: XY CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beslut
    ADD CONSTRAINT xy_beslut_beslut_ar_arende FOREIGN KEY (arendeid) REFERENCES public.arende(arendeid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: periodforsakran xy_pforsak_arende; Type: XY CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.periodforsakran
    ADD CONSTRAINT xy_pforsak_arende FOREIGN KEY (arendeid) REFERENCES public.arende(arendeid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: utbetperiod xy_utbetperiod_arende; Type: XY CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utbetperiod
    ADD CONSTRAINT xy_utbetperiod_arende FOREIGN KEY (arendeid) REFERENCES public.arende(arendeid) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

