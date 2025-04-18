--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: optimizer_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO optimizer_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: buildings; Type: TABLE; Schema: public; Owner: optimizer_user
--

CREATE TABLE public.buildings (
    id integer NOT NULL,
    name character varying NOT NULL,
    curr_level integer NOT NULL,
    num_employees integer NOT NULL,
    curr_coefficient double precision NOT NULL,
    next_coefficient double precision NOT NULL,
    curr_total_income double precision NOT NULL,
    gold_to_upgrade double precision NOT NULL,
    idol_income double precision DEFAULT 0.0
);


ALTER TABLE public.buildings OWNER TO optimizer_user;

--
-- Name: buildings_id_seq; Type: SEQUENCE; Schema: public; Owner: optimizer_user
--

CREATE SEQUENCE public.buildings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.buildings_id_seq OWNER TO optimizer_user;

--
-- Name: buildings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: optimizer_user
--

ALTER SEQUENCE public.buildings_id_seq OWNED BY public.buildings.id;


--
-- Name: buildings id; Type: DEFAULT; Schema: public; Owner: optimizer_user
--

ALTER TABLE ONLY public.buildings ALTER COLUMN id SET DEFAULT nextval('public.buildings_id_seq'::regclass);


--
-- Data for Name: buildings; Type: TABLE DATA; Schema: public; Owner: optimizer_user
--

COPY public.buildings (id, name, curr_level, num_employees, curr_coefficient, next_coefficient, curr_total_income, gold_to_upgrade, idol_income) FROM stdin;
13	Car dealership	8	770	1500	2500	12680000	1000000	8533400
15	Hair Salon	8	770	1500	2500	14880000	1000000	10733400
12	Promo Center	6	770	400	800	4410000	400000	2940030
11	Crowne Plaza	6	770	400	800	4310000	400000	2840030
9	Private Bank	6	770	400	800	4070000	400000	2600030
10	Energy Company	6	770	400	800	3980000	400000	2510030
17	Movie Theater	6	770	400	800	3890000	400000	2420030
16	Insurance Company	6	770	400	800	3870000	400000	2400030
18	Luxury Yacht	6	770	400	800	3820000	400000	2350030
14	Coffee Shop	12	770	7200	9200	102660000	2000000	84643590
\.


--
-- Name: buildings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: optimizer_user
--

SELECT pg_catalog.setval('public.buildings_id_seq', 18, true);


--
-- Name: buildings buildings_pkey; Type: CONSTRAINT; Schema: public; Owner: optimizer_user
--

ALTER TABLE ONLY public.buildings
    ADD CONSTRAINT buildings_pkey PRIMARY KEY (id);


--
-- Name: ix_buildings_id; Type: INDEX; Schema: public; Owner: optimizer_user
--

CREATE INDEX ix_buildings_id ON public.buildings USING btree (id);


--
-- PostgreSQL database dump complete
--

