import requests
import truststore

import ssl

from pathlib import Path

truststore.inject_into_ssl()


INEP_EXTRA_CA_CERT = Path(__file__).parent.parent / "certs" / "rnp_icpedu_gr46_ov_tls_ca_2025.pem"


class INEPTLSAdapter(requests.adapters.HTTPAdapter):
    """
    O servidor do INEP reseta a conexão durante o handshake quando o
    cliente oferece TLS 1.3. Travar em TLS 1.2 evita o reset. A CA
    intermediária da RNP é carregada explicitamente porque não está nas
    cadeias públicas padrão; o truststore complementa com as raízes do
    sistema (ex.: GlobalSign Root R46), fechando a cadeia de confiança.
    """

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.maximum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_verify_locations(cafile=str(INEP_EXTRA_CA_CERT))
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)