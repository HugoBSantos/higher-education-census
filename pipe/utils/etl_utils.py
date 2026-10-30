INEP_COLUMNS = {
    "ies": {
        "file_name": "microdados_ed_sup_ies_2024.csv",
        "column_mapping": {
            "CO_IES": "ies_id",
            "NO_IES": "nome",
            "SG_IES": "sigla",
            "TP_ORGANIZACAO_ACADEMICA": "organizacao_academica_id",
            "TP_REDE": "rede_ensino",
            "TP_CATEGORIA_ADMINISTRATIVA": "categoria_administrativa_id",
            "NO_REGIAO_IES": "nome_regiao",
            "CO_REGIAO_IES": "regiao_id",
            "NO_UF_IES": "nome_uf",
            "SG_UF_IES": "sigla_uf",
            "CO_UF_IES": "uf_id",
            "NO_MUNICIPIO_IES": "nome_municipio",
            "CO_MUNICIPIO_IES": "municipio_id",
            "IN_CAPITAL_IES": "e_capital",
            "QT_DOC_TOTAL": "qtd_docentes_total",
            "QT_DOC_EXE": "qtd_docentes_em_exercicio",
        },
    },
    "cursos": {
        "file_name": "microdados_cadastro_cursos_2024.csv",
        "column_mapping": {
            "CO_IES": "ies_id",
            "NO_CURSO": "nome",
            "CO_CURSO": "curso_id",
            "TP_GRAU_ACADEMICO": "grau_academico_id",
            "IN_GRATUITO": "e_gratuito",
            "TP_MODALIDADE_ENSINO": "modalidade_ensino",
            "TP_NIVEL_ACADEMICO": "nivel_academico",
            "CO_CINE_AREA_GERAL": "area_geral_id",
            "NO_CINE_AREA_GERAL": "nome_area_geral",
            "QT_CURSO": "qtd_cursos",
            "QT_VG_TOTAL": "qtd_vagas",
            "QT_INSCRITO_TOTAL": "qtd_inscritos",
            "QT_ING": "qtd_ingressantes",
            "QT_MAT": "qtd_matriculas",
            "QT_CONC": "qtd_concluintes",
        },
    },
}


def normalize_string_column(column: str):
    """Retorna a expressão SQL que padroniza o texto de `column` em title case.

    A primeira letra de cada palavra fica maiúscula e o resto minúscula,
    exceto conectivos como "de", "da" e "do", que ficam em minúsculas.
    """

    return rf"""
        array_to_string(
            list_transform(
                string_split_regex(lower(trim({column})), '\s+'),
                lambda palavra: CASE
                    WHEN palavra IN ('de', 'da', 'do', 'das', 'dos', 'e', 'em')
                        THEN palavra
                    ELSE upper(palavra[1]) || palavra[2:]
                END
            ),
            ' '
        )
    """