"""Bússola – Roteiro de UC: Activity Provider para a Inven!RA (semana 1, dados de exemplo).

Serviços implementados (os cinco URL fixos do ficheiro de registo):
  GET  /configuracao      -> config_url          (página HTML de configuração)
  GET  /json-params       -> json_params_url     (parâmetros recolhíveis da página)
  GET  /deploy            -> user_url            (deploy de uma instância; ?activityID=...)
  GET  /analytics-list    -> analytics_list_url  (analíticas disponíveis)
  POST /analytics         -> analytics_url       (analíticas de uma instância)

O serviço "Provide activity" ainda não está implementado, como pede o enunciado.
Neste ficheiro fica o papel do AdaptadorInvenRA da arquitetura do Tópico 3:
traduz os pedidos HTTP da Inven!RA em chamadas aos serviços de domínio.
"""
import os
from flask import Flask, Response, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

import dominio

app = Flask(__name__)
# No Render o pedido chega por um proxy HTTPS: assim os URL devolvidos usam https://
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.json.ensure_ascii = False  # manter acentos legíveis no JSON
app.json.sort_keys = False


@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


def base_url():
    return request.url_root.rstrip("/")


# ---------------------------------------------------------------- registo
@app.get("/")
def indice():
    """Ficheiro de registo da atividade, com os URL absolutos deste servidor."""
    b = base_url()
    return jsonify({
        "name": "Bússola – Roteiro de UC",
        "config_url": f"{b}/configuracao",
        "json_params_url": f"{b}/json-params",
        "user_url": f"{b}/deploy",
        "analytics_url": f"{b}/analytics",
        "analytics_list_url": f"{b}/analytics-list",
    })


# ---------------------------------------------------------- config_url
@app.get("/configuracao")
def configuracao():
    opcoes_uc = "".join(
        f'<option value="{uc["codigo"]}">{uc["codigo"]} – {uc["nome"]}</option>'
        for uc in dominio.listar_ucs()
    )
    html = f"""<!DOCTYPE html>
<html lang="pt-PT"><head><meta charset="utf-8"><title>Bússola – configuração</title>
<style>
 body{{font-family:Arial,sans-serif;max-width:560px;margin:16px;color:#1d2433}}
 label{{display:block;margin-top:10px;font-weight:bold}}
 input,select{{width:100%;padding:6px;margin-top:4px;box-sizing:border-box}}
 small{{color:#555}}
</style></head><body>
<h2>Bússola – Roteiro de UC</h2>
<p><small>Configure a unidade curricular a acompanhar. Os valores são recolhidos pela Inven!RA.</small></p>

<label for="uc_codigo">Unidade curricular</label>
<select id="uc_codigo" name="uc_codigo">{opcoes_uc}</select>

<label for="uc_nome">Nome da UC (como aparece ao estudante)</label>
<input id="uc_nome" name="uc_nome" type="text" value="Arquitetura e Padrões de Software">

<label for="roteiro_url">URL do roteiro / contrato de aprendizagem</label>
<input id="roteiro_url" name="roteiro_url" type="url" placeholder="https://elearning.uab.pt/...">

<label for="tipologia_avaliacao">Tipologia de avaliação (Modelo Pedagógico da UAb)</label>
<select id="tipologia_avaliacao" name="tipologia_avaliacao">
  <option value="1">1</option><option value="2" selected>2</option>
  <option value="3">3</option><option value="4">4</option>
</select>

<label for="data_inicio">Data de início</label>
<input id="data_inicio" name="data_inicio" type="date" value="2026-10-12">

<label for="horas_semanais">Horas semanais previstas</label>
<input id="horas_semanais" name="horas_semanais" type="number" min="1" max="40" value="10">

<label for="lembretes_ativos">Lembretes de atividades em atraso</label>
<select id="lembretes_ativos" name="lembretes_ativos">
  <option value="true" selected>Sim</option><option value="false">Não</option>
</select>
</body></html>"""
    return Response(html, mimetype="text/html")


# ------------------------------------------------------- json_params_url
@app.get("/json-params")
def json_params():
    return jsonify(dominio.PARAMETROS)


# -------------------------------------------------------------- user_url
@app.get("/deploy")
def deploy():
    activity_id = request.args.get("activityID") or request.args.get("activityId") or request.args.get("id")
    if not activity_id:
        return jsonify({"erro": "Falta o parâmetro activityID"}), 400
    dominio.criar_instancia(activity_id)
    url = f"{base_url()}/atividade?activityID={activity_id}"
    return Response(url, mimetype="text/plain")


@app.get("/deploy/<activity_id>")
def deploy_path(activity_id):
    dominio.criar_instancia(activity_id)
    return Response(f"{base_url()}/atividade?activityID={activity_id}", mimetype="text/plain")


# ----------------------------------------------------- analytics_list_url
@app.get("/analytics-list")
def analytics_list():
    return jsonify(dominio.CONTRATO_ANALYTICS)


# ---------------------------------------------------------- analytics_url
@app.route("/analytics", methods=["POST", "OPTIONS"])
def analytics():
    if request.method == "OPTIONS":
        return "", 204
    dados = request.get_json(silent=True) or {}
    activity_id = dados.get("activityID")
    if not activity_id:
        return jsonify({"erro": "O corpo JSON deve conter activityID"}), 400
    return jsonify(dominio.obter_analytics(activity_id, base_url()))


# ------------------------------------------- páginas das analíticas qualitativas
@app.get("/qual/<tipo>")
def pagina_qualitativa(tipo):
    activity_id = request.args.get("activityID", "")
    std_id = request.args.get("stdID", "")
    html = dominio.pagina_qualitativa(tipo, activity_id, std_id)
    if html is None:
        return jsonify({"erro": "Analítica desconhecida"}), 404
    return Response(html, mimetype="text/html")


# ------------------------------------------------ provide activity (fase seguinte)
@app.route("/atividade", methods=["GET", "POST"])
def atividade():
    return Response(
        "<!DOCTYPE html><html lang='pt-PT'><meta charset='utf-8'><body style='font-family:Arial'>"
        "<h2>Bússola – Roteiro de UC</h2><p>Instância criada. A interface do estudante "
        "(serviço Provide activity) será implementada numa fase seguinte do projeto.</p></body></html>",
        mimetype="text/html",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
