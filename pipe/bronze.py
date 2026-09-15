import duckdb
import requests_cache

import io
import tempfile

from pathlib import Path
from zipfile import ZipFile

from pipe.utils.tls_adapter import INEPTLSAdapter
from pipe.utils.etl_utils import INEP_COLUMNS


ROOT = Path(__file__).resolve().parent.parent
BRONZE = ROOT / "data" / "bronze"
CACHE = ROOT / "data" / "cache"

BRONZE.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)


def create_bronze():

    source_files = [
        "MICRODADOS_CADASTRO_CURSOS_2024.CSV",
        "MICRODADOS_ED_SUP_IES_2024.CSV"
    ]
    output_paths = {
        f: BRONZE / f.lower().replace(".csv", ".parquet") for f in source_files
    }
    files_exist = all(p.exists() for p in output_paths.values())

    if not files_exist:

        print("Um ou mais arquivos não existem. Baixando zip...")

        session = requests_cache.CachedSession(
            cache_name=CACHE / "inep_cache.sqlite",
            backend="sqlite",
            expire_after=None,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        session.mount("https://", INEPTLSAdapter())

        zip_name = "microdados_censo_da_educacao_superior_2024"
        url = f"https://download.inep.gov.br/microdados/{zip_name}.zip"

        response = session.get(url)
        response.raise_for_status()

        conn = duckdb.connect()

        with ZipFile(io.BytesIO(response.content)) as zf:
            for f, output_path in output_paths.items():

                file_data = zf.read(f"{zip_name}/dados/{f}")

                with tempfile.NamedTemporaryFile(suffix=".csv") as tmp:
                    tmp.write(file_data)
                    tmp.flush()

                    conn.execute(f"""
                        COPY (
                            SELECT {", ".join(INEP_COLUMNS[f])}
                            FROM read_csv('{tmp.name}', delim=';', encoding='latin-1')
                        )
                        TO '{output_path}'
                    """)

        print("Arquivos extraídos com sucesso!")

    else:
        print("Ambos os arquivos já existem.")