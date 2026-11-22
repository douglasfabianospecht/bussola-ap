# Bússola – Roteiro de UC (Activity Provider para a Inven!RA)

Projeto da UC Arquitetura e Padrões de Software (UAb, 2026/27). Semana 1 do Tópico 4: servidor RESTful que responde, com dados de exemplo, aos cinco pedidos da Inven!RA. O serviço "Provide activity" fica para uma fase seguinte.

Tecnologia: Python 3, Flask e Gunicorn, alojado no Render.

## Serviços

| Serviço Inven!RA | Método e caminho | Resposta |
|---|---|---|
| Registo da atividade | `GET /` | JSON com os cinco URL |
| config_url | `GET /configuracao` | Página HTML com os campos de configuração (sem botão de guardar) |
| json_params_url | `GET /json-params` | Lista JSON dos 7 parâmetros |
| user_url (deploy) | `GET /deploy?activityID=<id>` | URL de acesso à instância (texto) |
| analytics_list_url | `GET /analytics-list` | JSON com `qualAnalytics` e `quantAnalytics` |
| analytics_url | `POST /analytics` com `{"activityID": "<id>"}` | Analíticas de exemplo por estudante |

As analíticas qualitativas do tipo URL apontam para `GET /qual/pagina_progresso` e `GET /qual/grafico_horas`.

## Executar localmente

```
pip install -r requirements.txt
python app.py
```

O servidor fica em http://localhost:5000.

## Publicar no Render

1. Criar um repositório no GitHub (por exemplo `bussola-ap`) e enviar estes ficheiros.
2. Em https://dashboard.render.com: New → Web Service → ligar o repositório.
3. Configuração: Branch `main`, Runtime `Python 3`, Build Command `pip install -r requirements.txt`, Start Command `gunicorn app:app`, plano Free.
4. Esperar pelo deploy e abrir o URL gerado (por exemplo `https://bussola-ap.onrender.com/`).

No plano gratuito o serviço hiberna sem uso; o primeiro pedido pode demorar cerca de um minuto.

## Testar

```
curl https://<url>/json-params
curl https://<url>/analytics-list
curl "https://<url>/deploy?activityID=teste1"
curl -X POST https://<url>/analytics -H "Content-Type: application/json" -d "{\"activityID\": \"teste1\"}"
```

A página de configuração abre-se diretamente no browser: `https://<url>/configuracao`.

## Estrutura

- `app.py`: rotas HTTP; corresponde ao AdaptadorInvenRA da arquitetura do Tópico 3.
- `dominio.py`: parâmetros, contrato de analíticas, catálogo de UC, instâncias e analíticas de exemplo (versão simplificada de GestorInstancias, GestorRoteiros e ServicoAnalytics). Nesta fase os dados ficam em memória.
