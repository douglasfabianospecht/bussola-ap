"""Domínio do Bússola com dados de exemplo (semana 1).

Agrupa, de forma simplificada, o GestorInstancias, o GestorRoteiros e o
ServicoAnalytics da arquitetura do Tópico 3. Nesta fase os dados ficam em
memória; a persistência (PostgreSQL) entra nas fases seguintes.
"""
from datetime import datetime, timezone
from urllib.parse import quote

# Os 7 parâmetros entregues no Tópico 2 (json_params_url)
PARAMETROS = [
    {"name": "uc_codigo", "type": "text/plain"},
    {"name": "uc_nome", "type": "text/plain"},
    {"name": "roteiro_url", "type": "URL"},
    {"name": "tipologia_avaliacao", "type": "integer"},
    {"name": "data_inicio", "type": "text/plain"},
    {"name": "horas_semanais", "type": "integer"},
    {"name": "lembretes_ativos", "type": "boolean"},
]

# As 12 analíticas entregues no Tópico 2 (analytics_list_url)
CONTRATO_ANALYTICS = {
    "qualAnalytics": [
        {"name": "pagina_progresso", "type": "URL"},
        {"name": "grafico_horas", "type": "URL"},
        {"name": "ultima_reflexao", "type": "text/plain"},
    ],
    "quantAnalytics": [
        {"name": "acedeu_atividade", "type": "boolean"},
        {"name": "percentagem_roteiro", "type": "integer"},
        {"name": "topicos_concluidos", "type": "integer"},
        {"name": "atividades_concluidas", "type": "integer"},
        {"name": "atividades_em_atraso", "type": "integer"},
        {"name": "em_dia_topico_atual", "type": "boolean"},
        {"name": "horas_registadas", "type": "integer"},
        {"name": "dias_sem_atividade", "type": "integer"},
        {"name": "reflexoes_submetidas", "type": "integer"},
    ],
}

# Catálogo de UC (GestorRoteiros, simplificado)
UCS = [
    {"codigo": "22304", "nome": "Arquitetura e Padrões de Software"},
    {"codigo": "22290", "nome": "Investigação Operacional"},
    {"codigo": "IS", "nome": "Integração de Sistemas"},
]

# Instâncias criadas por deploy (GestorInstancias, em memória)
INSTANCIAS = {}

# Estudantes de exemplo (Inven!RAstdID -> valores)
EXEMPLOS = {
    "1001": {"acedeu_atividade": True, "percentagem_roteiro": 45, "topicos_concluidos": 3,
             "atividades_concluidas": 14, "atividades_em_atraso": 1, "em_dia_topico_atual": True,
             "horas_registadas": 52, "dias_sem_atividade": 1, "reflexoes_submetidas": 5,
             "ultima_reflexao": "Esta semana organizei melhor as leituras; falta-me tempo para o fórum."},
    "1002": {"acedeu_atividade": True, "percentagem_roteiro": 20, "topicos_concluidos": 1,
             "atividades_concluidas": 6, "atividades_em_atraso": 4, "em_dia_topico_atual": False,
             "horas_registadas": 21, "dias_sem_atividade": 6, "reflexoes_submetidas": 2,
             "ultima_reflexao": "Entrei tarde no semestre e ainda estou a recuperar o Tópico 2."},
}


def listar_ucs():
    return UCS


def criar_instancia(activity_id):
    INSTANCIAS.setdefault(activity_id, {"criada_em": datetime.now(timezone.utc).isoformat(), "estudantes": {}})
    return INSTANCIAS[activity_id]


def obter_analytics(activity_id, base_url):
    """Analíticas de todos os estudantes da instância (dados de exemplo)."""
    resultado = []
    for std_id, v in EXEMPLOS.items():
        q = f"activityID={quote(str(activity_id))}&stdID={std_id}"
        resultado.append({
            "inveniraStdID": std_id,
            "quantAnalytics": [
                {"name": a["name"], "value": v[a["name"]]} for a in CONTRATO_ANALYTICS["quantAnalytics"]
            ],
            "qualAnalytics": [
                {"pagina_progresso": f"{base_url}/qual/pagina_progresso?{q}"},
                {"grafico_horas": f"{base_url}/qual/grafico_horas?{q}"},
                {"ultima_reflexao": v["ultima_reflexao"]},
            ],
        })
    return resultado


def pagina_qualitativa(tipo, activity_id, std_id):
    v = EXEMPLOS.get(std_id)
    if tipo not in ("pagina_progresso", "grafico_horas") or v is None:
        return None
    if tipo == "pagina_progresso":
        corpo = (f"<p>Roteiro concluído: <b>{v['percentagem_roteiro']}%</b> · tópicos concluídos: "
                 f"{v['topicos_concluidos']} · atividades concluídas: {v['atividades_concluidas']} · "
                 f"em atraso: {v['atividades_em_atraso']}</p>")
    else:
        horas = [8, 10, 7, 12, 9, 6][: max(1, v["horas_registadas"] // 9)]
        barras = "".join(
            f"<div style='display:flex;align-items:center;margin:3px 0'><span style='width:80px'>Semana {i+1}</span>"
            f"<div style='background:#1f3a68;height:14px;width:{h*20}px'></div><span>&nbsp;{h} h</span></div>"
            for i, h in enumerate(horas))
        corpo = f"<p>Horas registadas por semana (exemplo):</p>{barras}"
    return (f"<!DOCTYPE html><html lang='pt-PT'><meta charset='utf-8'><body style='font-family:Arial;margin:16px'>"
            f"<h3>Bússola · {tipo.replace('_', ' ')}</h3><p><small>Instância {activity_id} · estudante {std_id}"
            f" (dados de exemplo)</small></p>{corpo}</body></html>")
