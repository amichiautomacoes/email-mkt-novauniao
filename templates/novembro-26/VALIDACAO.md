# Revisão dos emails de novembro de 2026

Revisão de 26/10/2026 com a skill [email-marketing-bible](../../.agents/skills/email-marketing-bible/SKILL.md) e a identidade visual do projeto.

Os quatro templates estão preparados para revisão e simulação pela pipeline. A liberação operacional depende dos itens de pré-envio abaixo.

Atualização de 27/10/2026: os quatro cabeçalhos passaram a usar o mesmo azul dos rodapés, `#0f599c`. A logo no cabeçalho aumentou de 180 para 280 px de largura, com altura proporcional e redução automática em telas estreitas. Essa medida substitui, para estas campanhas, a sugestão geral de 180 a 200 px do guia da marca. As imagens originais e os rodapés foram preservados.

Nova atualização de 27/10/2026: a pedido do usuário, a marca do cabeçalho e do rodapé dos quatro emails foi substituída pela versão transparente de `templates/design-system/references/logo2.png`. As larguras de 280 e 245 px foram mantidas e as alturas ajustadas à proporção da nova imagem. O [registro da logo e do prompt](references/logo2-sem-fundo.md) documenta o arquivo sem fundo branco e sua exportação para email.

Endereço do rodapé: o endereço agora tem link explícito para o Google Maps fornecido pelo usuário, com cor branca inline, prioridade `!important`, texto interno branco e CSS restrito a `.footer-address`. Isso evita depender da cor do link criado automaticamente pelo Gmail. O texto do endereço e os demais links foram preservados. A abordagem de link explícito com estilo próprio segue a [orientação da Litmus](https://www.litmus.com/blog/how-to-fix-blue-links-in-gmail).

## Campanhas e assuntos

| Chave para a planilha | Assunto | Foco |
| --- | --- | --- |
| `preparacao_black_friday` | Não esqueça disso na Black Friday! | Conferir preço, leitura no caixa e reposição antes das promoções. |
| `produtividade_agilidade_operacao` | Sua equipe perde tempo com isso? | Reposição por setor e preparação da equipe antes da abertura. |
| `valorizacao_marca` | O cliente percebe esse detalhe? | Informações, identidade e formato das tags personalizadas. |
| `comercial_direta` | Vai deixar sua reposição para depois? | Pedir cotação com tipo de material, quantidade e modelo da impressora. |

Os assuntos do catálogo correspondem ao `<title>` dos HTMLs. Cada email tem preheader próprio, um botão principal e, quando existente, um link textual de continuidade para o mesmo objetivo comercial. Não foram acrescentados descontos, prazos de entrega, disponibilidade ou resultados de clientes sem comprovação.

## Alterações e validação local

- Texto mais específico, menos repetição e títulos e CTAs mais curtos.
- Nome personalizado com fallback `Olá!` para nome ausente, vazio ou nulo. HTML nos nomes continua escapado pelo Jinja2.
- Identidade da Nova União, estrutura dos rodapés e todos os destinos de WhatsApp, Instagram e solicitação de descadastro preservados. A logo foi atualizada conforme a solicitação de 27/10.
- HTML com tabelas de apresentação, largura máxima de 600 px, fontes de sistema, cores explícitas e botão com alternativa VML para Outlook.
- Tratamento de modo escuro com CSS, usando a nova logo transparente sobre o azul institucional do cabeçalho e do rodapé.
- Imagens por CID no clean e anexos inline na Resend. O renderer identifica corretamente os tipos MIME de PNG e JPEG.
- No comercial, as duas fotos originais de produto substituem a composição ilustrativa. Com a nova logo transparente, o total de imagens inline é de 166.819 bytes, cerca de 92% abaixo dos 2.040.430 bytes da versão inicial. Nenhuma imagem usada ultrapassa 200 KB.
- Raw atualizado junto com clean; regenerar pelo cleaner produz os mesmos arquivos.
- 47 testes automatizados aprovados; os 9 testes focados de renderer/sender também passaram.
- Quatro campanhas renderizadas no Chrome: desktop de 1440 px, celulares de 390 e 320 px e modo escuro de 390 px. Imagens carregadas, botão com área de toque de pelo menos 44 px e ausência de transbordamento horizontal.

As capturas do navegador verificam o HTML local; não substituem a conferência em Gmail, Outlook e Apple Mail de um email efetivamente entregue. Os indicadores `links_validated` e `images_validated` do catálogo representam a validação local de destinos, conteúdo clicável e resolução das imagens, não uma certificação de entrega.

A revisão visual independente foi aplicada em até quatro rodadas. As fotos originais do comercial têm pouco contraste nos contornos dos materiais brancos; as legendas individuais identificam cada produto. Fotografias de produto com melhor iluminação são uma oportunidade para uma próxima revisão, sem alterar ou inventar a aparência do material atual.

Os backups, prévias e relatórios desta revisão ficam em `tmp/novembro-26/revisao-2026-10-26/`, fora do versionamento. O arquivo antigo `tmp/preview-novembro-26-preparacao_black_friday.html` também foi atualizado.

## Configuração para usar novembro

A configuração padrão da aplicação ainda aponta para setembro. Ao preparar a simulação de novembro, configure no ambiente que executará o comando:

```env
TEMPLATES_CATALOG_PATH=templates/novembro-26/catalog.json
TEMPLATES_RAW_DIR=templates/novembro-26/raw
TEMPLATES_CLEAN_DIR=templates/novembro-26/clean
DRY_RUN_DEFAULT=true
EMAIL_SCHEDULE_DRY_RUN=true
```

Exemplo manual, após configurar os caminhos e `PYTHONPATH=src`:

```powershell
python -m email_mkt.cli send --campaign preparacao_black_friday --lote lote1 --limit 10 --dry-run
```

Use as chaves da tabela na coluna de campanha do Google Sheets. Lote, etapa, data e horário precisam corresponder à jornada real: a numeração dos quatro emails não define automaticamente suas etapas. Os horários devem coincidir com a execução do cron, que por padrão ocorre a cada 5 minutos, em `America/Sao_Paulo`.

## Pré-envio: resultados e pendências

1. **Resend validada em 27/10/2026:** a chave atual permite apenas envio. O HTTP 401 de `GET /domains` retorna `restricted_api_key`, com a mensagem `This API key is restricted to only send emails`; listar domínios exige acesso completo, conforme a [documentação de erros da Resend](https://resend.com/docs/api-reference/errors). O diagnóstico anterior, que tratava essa resposta como falha da credencial, estava incorreto. Um único teste autorizado para `hugoproamichi@gmail.com`, com o assunto `[TESTE NOVEMBRO] Black Friday: confira sua etiquetagem`, foi aceito por `POST /emails` com HTTP 200. O webhook respondeu HTTP 200 no endpoint de saúde e registrou `email.opened` para o mesmo email. A chave foi mantida. O relatório sanitizado fica em `tmp/resend-diagnostico-2026-10-27.json`. Consultas de domínios, relatórios e outros recursos continuam fora do escopo dessa chave; isso não impede o envio.
2. **Remetente:** o ambiente local retorna `Hugo <hugoamichi@etiquetasnovauniao.com.br>` e não define reply-to. Confirmar o nome de exibição da Nova União e a caixa que receberá respostas no ambiente de envio.
3. **Descadastro:** o rodapé preserva uma solicitação por `mailto:`. Esse link não remove automaticamente o contato da base. A pipeline atual também não adiciona os headers de descadastro em um clique. Antes de disparos em massa, implementar e conferir o processamento de descadastro e a supressão correspondente. A [documentação da Resend](https://resend.com/blog/manage-subscribers-using-resend-audiences) distingue o fluxo gerenciado para audiências dos headers usados em uma implementação própria.
4. **Lote e entregabilidade:** conferir a base autorizada, total real de destinatários, opt-outs, bounces, reclamações, histórico da etapa e autenticação do domínio. Não foram consultados ou alterados contatos nesta revisão.
5. **Conferência do teste recebido:** o teste de Black Friday foi enviado uma única vez após autorização explícita e gerou um evento de abertura. Esse evento pode ser disparado pelo cliente ou por um proxy de imagens; não substitui a conferência visual de nome, imagens no corpo, CTAs, rodapé, remetente e respostas na caixa recebida. Os outros três emails ainda não tiveram teste de entrega nesta revisão. Registrar a aprovação visual antes de definir o agendamento.

Nenhuma linha da planilha ou configuração de produção foi alterada. O único envio realizado foi o teste interno de Black Friday explicitamente autorizado; não houve disparo para os lotes de leads.

## Preparação de 10/11/2026 — Black Friday com copy humana

- Chave para a coluna Campanha: `01_black_friday_nova_uniao_copy_humana`.
- Assunto cadastrado: **Black Friday à vista: como estão suas etiquetas?**
- Fonte em `raw/01_black_friday_nova_uniao_copy_humana.html`, com imagens em `raw/01_black_friday_nova_uniao_copy_humana/images/`; clean regenerado pelo cleaner do projeto.
- Texto, saudação, CTA e destinos originais preservados. Regenerar a fonte produz o mesmo clean, byte a byte.
- Três imagens únicas inline (76.907 bytes no total), todos os CIDs resolvidos e nomes opacos no payload Resend. A imagem principal deixou de depender da pasta de outra campanha.
- Nome com fallback para vazio/nulo, escape de HTML e referência WhatsApp iguais nos botões HTML e VML conferidos.
- 53 testes passaram: renderer, sender, imagens inline, atribuição WhatsApp e agendamento. As integrações mensais foram atualizadas para os quatro clean atuais, pois os antigos já estavam removidos antes desta preparação.
- Capturas locais em larguras de 320, 390 e 600 px, além de modo escuro em 390 px; imagens carregadas e texto legível. Evidências em `tmp/audit-01-black-friday/`.
- Remetente **local** ajustado para `Etiquetas Nova União <hugoamichi@etiquetasnovauniao.com.br>`; reply-to local `hugoamichi@etiquetasnovauniao.com.br`. Variáveis de simulação preservadas.

### Pendências operacionais

O arquivo está preparado e validado localmente. Ainda não houve teste real desta versão, aprovação visual em Gmail, commit/push, redeploy ou agendamento. Não foram alteradas a planilha, a base de contatos ou as variáveis do EasyPanel. Os arquivos e o catálogo precisam estar no ambiente do worker antes de usar a chave acima.

O rodapé mantém o pedido de descadastro por email. A consulta de metadados ao banco configurado não encontrou `email_suppressions`; portanto não foi comprovada supressão automática. Descadastro em um clique não foi implementado nesta preparação de template. Essa pendência geral continua necessária para liberar um disparo em massa; não tratar a validação local do HTML como aprovação da audiência ou de entregabilidade.

### Edição de conteúdo após o teste interno — 10/11/2026

A pedido do usuário, foi retirada a frase abaixo do primeiro CTA e o texto principal foi reduzido de 340 para 141 palavras (59%). Foram cortadas repetições sobre a reposição; produtos, orientação para cotação por foto, personalização, imagens, destinos dos links e rodapé foram preservados. Raw e clean sincronizados; 29 testes focados passaram. Esta edição é posterior ao teste aceito pela Resend com ID `01a1c3c3-7db2-70a9-9266-cb8c379e7dbe`; esse envio corresponde à versão anterior, mais longa. A versão resumida ainda não foi reenviada.

### Imagens hospedadas sem anexos — 10/11/2026

O usuário confirmou cartões de anexo no Gmail para a imagem principal. O payload anterior já usava CID, nomes opacos e disposição inline; isso não eliminou o cartão nesse cliente. Com autorização explícita do usuário, foi criado o bucket público `email-mkt-assets` no Supabase e publicadas apenas as três imagens do template. Acesso anônimo HTTP 200, MIME e hashes dos bytes foram conferidos.

Raw e clean agora usam URLs HTTPS permanentes com hash no caminho. As imagens locais continuam disponíveis como fonte; o manifesto público está em `references/black-friday-public-assets.json`. O renderer e o payload devem gerar zero anexos para esta campanha. Essa atualização substitui o uso de CID anteriormente registrado para este template. O texto resumido, o assunto, a personalização, o rodapé e os destinos dos CTAs foram preservados.

Validação desta atualização: **54 testes passaram**. Um novo teste interno para `hugoproamichi@gmail.com`, com assunto `[TESTE SEM ANEXOS] Black Friday à vista: como estão suas etiquetas?`, foi aceito pela Resend com ID `01a1c3d8-4988-78ac-adca-6bc09ea54b21`. O payload desse teste não contém o campo `attachments`. Ainda depende da conferência do usuário no Gmail.

### Revisão para publicação — 10/11/2026

- O usuário aprovou o último teste recebido no Gmail: `[TESTE SEM LEGENDA] Black Friday à vista: como estão suas etiquetas?`, aceito pela Resend com ID `01a1c3db-1df0-7335-bbca-c76cb105bab0`. A versão aprovada tem conteúdo resumido, imagens HTTPS e zero anexos; a legenda abaixo da imagem foi removida.
- A planilha foi consultada em modo de leitura. O usuário confirmou manter a programação de **10/11/2026**, hoje: lote1 08:30, lote2 09:00, lote3 09:30, lote4 13:00, lote5 13:30 e lote6 14:00, todos na etapa 1 e com a chave `01_black_friday_nova_uniao_copy_humana`. Os horários coincidem com o cron padrão de cinco minutos. Não há linhas futuras completas para outras campanhas na consulta atual.
- A seleção atual da pipeline retornou respectivamente 165, 163, 168, 168, 168 e 167 candidatos: **999 no total**. A consulta não enviou mensagens nem alterou contatos. Esses totais refletem elegibilidade técnica no momento da revisão, não comprovação de consentimento.
- A tabela `email_suppressions` continua ausente no banco configurado. O descadastro do rodapé permanece manual por email; não foram comprovados processamento automático de opt-outs ou exclusões de bounces/reclamações. Esta publicação de arquivos não certifica essas condições de envio.
- O catálogo foi alinhado aos quatro arquivos clean atuais, retirando as cinco entradas cujo HTML havia sido removido. Os HTMLs raw antigos continuam no repositório como fontes; campanhas ausentes do catálogo não devem ser usadas na planilha.
- O estado local e o conteúdo aprovado foram revisados. O push precisa ser seguido pelo build/deploy do worker no EasyPanel. Não foi possível conferir daqui suas variáveis efetivas, o processo cron ou o deploy; `.env` local não configura produção. Conferir caminhos de novembro, remetente/reply-to e `EMAIL_SCHEDULE_DRY_RUN=false` no worker somente após resolver as pendências operacionais.
