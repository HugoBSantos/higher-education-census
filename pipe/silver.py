import duckdb

from pathlib import Path

from pipe.bronze import BRONZE
from pipe.utils.etl_utils import INEP_COLUMNS, normalize_string_column


SILVER_DDL = Path(__file__).resolve().parents[1] / "sql" / "ddl" / "silver.sql"


def create_silver(conn: duckdb.DuckDBPyConnection):
    
    for table_name, info in INEP_COLUMNS.items():
        
        renamed_columns = ",".join([
            f"{old_col} AS {new_col}"
            for old_col, new_col in info["column_mapping"].items()
        ])
        
        conn.sql(f"""
            CREATE TEMPORARY TABLE {table_name} AS
            SELECT {renamed_columns}
            FROM read_csv(
                '{BRONZE / info["file_name"]}',
                delim=';',
                encoding='latin-1',
                all_varchar=true
            );
        """)
    
    conn.sql(f"""
        BEGIN TRANSACTION;
        
        {SILVER_DDL.read_text()}
        
        INSERT INTO silver.organizacoes_academicas
        VALUES
            (1, 'Universidade'),
            (2, 'Centro Universitário'),
            (3, 'Faculdade'),
            (4, 'Instituto Federal de Educação, Ciência e Tecnologia'),
            (5, 'Centro Federal de Educação Tecnológica');
        
        INSERT INTO silver.categorias_administrativas
        VALUES
            (1, 'Pública Federal'),
            (2, 'Pública Estadual'),
            (3, 'Pública Municipal'),
            (4, 'Privada com fins lucrativos'),
            (5, 'Privada sem fins lucrativos'),
            (6, 'Privada - Particular em sentido estrito'),
            (7, 'Especial'),
            (8, 'Privada comunitária'),
            (9, 'Privada confessional');
        
        INSERT INTO silver.regioes
        SELECT
            DISTINCT CAST(regiao_id AS SMALLINT),
            nome_regiao AS nome
        FROM ies;
        
        INSERT INTO silver.ufs
        SELECT
            DISTINCT CAST(uf_id AS SMALLINT),
            nome_uf AS nome,
            sigla_uf AS sigla,
            CAST(regiao_id AS SMALLINT)
        FROM ies;
        
        INSERT INTO silver.municipios
        SELECT
            DISTINCT CAST(municipio_id AS INTEGER),
            nome_municipio AS nome,
            CAST(e_capital AS BOOLEAN),
            CAST(uf_id AS SMALLINT)
        FROM ies;
        
        INSERT INTO silver.ies
        SELECT
            CAST(ies_id AS INTEGER),
            {normalize_string_column("nome")},
            UPPER(sigla),
            CASE rede_ensino
                WHEN '1' THEN true
                WHEN '2' THEN false
            END AS e_publica,
            CAST(organizacao_academica_id AS SMALLINT),
            CAST(categoria_administrativa_id AS SMALLINT),
            CAST(municipio_id AS INTEGER),
            CAST(qtd_docentes_total AS INTEGER),
            CAST(qtd_docentes_em_exercicio AS INTEGER)
        FROM ies;
        
        
        UPDATE cursos
        SET grau_academico_id = '5'
        WHERE
            area_geral_id = '00'
            AND grau_academico_id IS NULL;
        
        UPDATE cursos
        SET grau_academico_id = '6'
        WHERE
            nivel_academico = '2'
            AND grau_academico_id IS NULL;
        
        
        INSERT INTO silver.graus_academicos
        VALUES
            (1, 'Bacharelado'),
            (2, 'Licenciatura'),
            (3, 'Tecnológico'),
            (4, 'Bacharelado e Licenciatura'),
            (5, 'Área Básica de Ingresso'),
            (6, 'Curso Sequencial');
        
        INSERT INTO silver.areas_gerais_cine_brasil
        SELECT
            DISTINCT CAST(area_geral_id AS SMALLINT),
            nome_area_geral AS nome
        FROM cursos;
        
        INSERT INTO silver.cursos
        SELECT
            CAST(curso_id AS INTEGER),
            ANY_VALUE(nome),
            CAST(ANY_VALUE(ies_id) AS INTEGER),
            CAST(ANY_VALUE(grau_academico_id) AS SMALLINT),
            CAST(ANY_VALUE(area_geral_id) AS SMALLINT),
            CAST(ANY_VALUE(e_gratuito) AS BOOLEAN),
            ANY_VALUE(
                CASE modalidade_ensino
                    WHEN '1' THEN true
                    WHEN '2' THEN false
                END
            ) AS e_presencial,
            ANY_VALUE(
                CASE nivel_academico
                    WHEN '1' THEN true
                    WHEN '2' THEN false
                END
            ) AS e_graduacao,
            SUM(CAST(qtd_cursos AS SMALLINT)),
            SUM(CAST(qtd_vagas AS INTEGER)),
            SUM(CAST(qtd_inscritos AS INTEGER)),
            SUM(CAST(qtd_ingressantes AS INTEGER)),
            SUM(CAST(qtd_matriculas AS INTEGER)),
            SUM(CAST(qtd_concluintes AS INTEGER))
        FROM cursos
        GROUP BY curso_id;
        
        COMMIT;
    """)