DROP SCHEMA IF EXISTS gold CASCADE;
DROP SCHEMA IF EXISTS silver CASCADE;

CREATE SCHEMA silver;


CREATE TABLE silver.organizacoes_academicas (
    organizacao_academica_id SMALLINT PRIMARY KEY,
    nome VARCHAR(60) NOT NULL
);


CREATE TABLE silver.categorias_administrativas (
    categoria_administrativa_id SMALLINT PRIMARY KEY,
    nome VARCHAR(40) NOT NULL
);


CREATE TABLE silver.regioes (
    regiao_id SMALLINT PRIMARY KEY,
    nome VARCHAR(20) NOT NULL
);


CREATE TABLE silver.ufs (
    uf_id SMALLINT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    sigla CHAR(2) NOT NULL UNIQUE,
    regiao_id SMALLINT NOT NULL REFERENCES silver.regioes (regiao_id)
);


CREATE TABLE silver.municipios (
    municipio_id INTEGER PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    e_capital BOOLEAN NOT NULL,
    uf_id SMALLINT NOT NULL REFERENCES silver.ufs (uf_id)
);


CREATE TABLE silver.ies (
    ies_id INTEGER PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    sigla VARCHAR(20),
    e_publica BOOLEAN NOT NULL,
    -- Sem FK de propósito: o DuckDB transforma o UPDATE de coluna indexada em DELETE + INSERT,
    -- e silver.cursos referencia silver.ies, então a FK bloquearia editar estes campos via CRUD.
    -- Os valores válidos são garantidos pelos CHECKs abaixo.
    organizacao_academica_id SMALLINT NOT NULL, -- REFERENCES silver.organizacoes_academicas (organizacao_academica_id),
    categoria_administrativa_id SMALLINT NOT NULL, -- REFERENCES silver.categorias_administrativas (categoria_administrativa_id),
    municipio_id INTEGER NOT NULL REFERENCES silver.municipios (municipio_id),

    qtd_docentes_total INTEGER,
    qtd_docentes_em_exercicio INTEGER,

    -- Constraints
    CHECK (e_publica = (categoria_administrativa_id IN (1,2,3,7))),
    CHECK (organizacao_academica_id BETWEEN 1 AND 5),
    CHECK (categoria_administrativa_id BETWEEN 1 AND 9),
    CHECK (qtd_docentes_total >= 0),
    CHECK (qtd_docentes_em_exercicio >= 0),
    CHECK (qtd_docentes_em_exercicio <= qtd_docentes_total)
);


CREATE TABLE silver.graus_academicos (
    grau_academico_id SMALLINT PRIMARY KEY,
    nome VARCHAR(30) NOT NULL
);


CREATE TABLE silver.areas_gerais_cine_brasil (
    area_geral_id SMALLINT PRIMARY KEY,
    nome VARCHAR(60) NOT NULL
);


CREATE TABLE silver.cursos (
    curso_id INTEGER PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    ies_id INTEGER NOT NULL REFERENCES silver.ies (ies_id),
    grau_academico_id SMALLINT NOT NULL REFERENCES silver.graus_academicos (grau_academico_id),
    area_geral_id SMALLINT NOT NULL REFERENCES silver.areas_gerais_cine_brasil (area_geral_id),
    e_gratuito BOOLEAN NOT NULL,
    e_presencial BOOLEAN NOT NULL,
    e_graduacao BOOLEAN NOT NULL,
    
    qtd_vagas INTEGER,
    qtd_inscritos INTEGER,
    qtd_ingressantes INTEGER,
    qtd_matriculas INTEGER,
    qtd_concluintes INTEGER,

    -- Constraints
    CHECK (qtd_vagas >= 0),
    CHECK (qtd_inscritos >= 0),
    CHECK (qtd_ingressantes >= 0),
    CHECK (qtd_matriculas >= 0),
    CHECK (qtd_concluintes >= 0)
);