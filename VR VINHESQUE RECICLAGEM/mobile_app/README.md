# Vinhesque Mobile

App mobile offline para lancar compras externas.

Agora o app pode abrir sem o Python do notebook. Ele salva tudo no proprio celular e sincroniza automaticamente quando encontrar o endereco de sincronizacao configurado.

## Modo independente

Para o link funcionar a qualquer momento no celular e sincronizar sem depender do notebook, hospede o servidor completo na nuvem usando `render.yaml` ou `Dockerfile`.

O sistema desktop do notebook da empresa continua usando o banco local `vr_reciclagem.db`. Para ligar os dois mundos, o notebook roda `desktop_cloud_sync.py` em segundo plano e importa para o banco local os lancamentos que chegaram na nuvem.

Depois de abrir uma vez no Safari/Chrome, toque em `Adicionar a Tela de Inicio`. A partir dai:

- o app abre mesmo sem notebook ligado;
- o app abre mesmo sem internet;
- compras ficam salvas no celular como pendentes;
- quando houver internet, o app tenta sincronizar sozinho com a URL da nuvem.

## Sincronizacao

Sincronizar significa enviar os lancamentos do celular para algum servidor. Existem duas opcoes:

1. Internet/definitivo: hospede `sync_server.py` na nuvem com HTTPS e disco persistente.
2. Notebook/local: execute `instalar_mobile_automatico.bat` se quiser manter o modo local como reserva.

Sem um servidor de sincronizacao ligado em algum lugar, o app continua funcionando offline, mas os dados ficam pendentes no celular.

## Hospedagem na nuvem

Arquivos prontos:

- `render.yaml`: blueprint para provedor com Web Service Python e disco persistente.
- `Dockerfile`: alternativa para qualquer provedor que aceite container.
- `HOSPEDAGEM_NUVEM.txt`: passo a passo de configuracao.

Variaveis esperadas no provedor:

```text
DB_PATH=/data/vr_reciclagem.db
RECEIPTS_DIR=/data/comprovantes
SYNC_TOKEN=um-codigo-secreto
```

No Menu do app, coloque a URL HTTPS do provedor em `Endereco de sincronizacao` e o mesmo valor de `SYNC_TOKEN` em `Codigo de sincronizacao`.

## Ligar com o banco do notebook

No notebook da empresa:

1. Copie `cloud_sync_config.example.json` para `cloud_sync_config.json`.
2. Preencha `cloud_url` com a URL HTTPS do provedor.
3. Preencha `sync_token` com o mesmo valor de `SYNC_TOKEN`.
4. Execute uma vez `instalar_sincronizacao_nuvem.bat`.

Depois disso, o notebook puxa da nuvem os lancamentos do celular e grava no `vr_reciclagem.db` local automaticamente.

## Sem abrir terminal todo dia

No notebook da cliente, execute uma unica vez:

```text
instalar_mobile_automatico.bat
```

Isso cria uma tarefa do Windows chamada `Vinhesque Mobile Sync`. Ela inicia o servidor mobile automaticamente quando a cliente entrar no Windows, em segundo plano e sem janela de terminal.

Se precisar desfazer:

```text
remover_mobile_automatico.bat
```

## Como testar no notebook

```text
http://127.0.0.1:8765
```

1. Abra a pasta `VR VINHESQUE RECICLAGEM`.
2. Execute `instalar_mobile_automatico.bat` uma vez, ou `iniciar_vinhesque_mobile.bat` para teste manual.
3. No navegador do notebook, abra o endereco acima.

## Como testar no celular na mesma rede

1. Conecte o iPhone no mesmo Wi-Fi do notebook.
2. Execute `instalar_mobile_automatico.bat` uma vez no notebook.
3. Abra no Safari o endereco mostrado como `iPhone na mesma rede`.
4. Toque em compartilhar e depois em `Adicionar a Tela de Inicio`.

## Fluxo

- O app baixa clientes e materiais do banco do notebook.
- Sem internet, o app salva compras como pendentes no proprio iPhone.
- Toda compra lancada pelo app mobile entra como `Venda externa`.
- O comprovante aparece na hora, mesmo antes de sincronizar.
- Quando houver conexao com o servidor de sincronizacao, o app tenta sincronizar sozinho. Tambem da para tocar em `Sync`.
- O servidor grava em `transacoes`, `transacao_itens` e `comprovantes`.
- Ao sincronizar pelo notebook, ele gera o PNG oficial do comprovante e tenta imprimir na impressora padrao.
- A tabela `mobile_sync` evita lancamento duplicado se sincronizar duas vezes.

## Observacao importante

Para o modo offline completo instalado na tela inicial, o celular precisa abrir o app por HTTPS. Em teste local por HTTP, a tela e a sincronizacao funcionam, mas o cache offline pode ser limitado pelo Safari.
