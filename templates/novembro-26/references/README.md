# Referências dos modelos de novembro

As quatro campanhas receberam os roteiros fornecidos pelo usuário e têm versões tratadas na pasta `../clean/`. Em 26/10/2026, os textos, assuntos, CTAs, personalização e compatibilidade foram refinados com a skill email-marketing-bible. A personalização, a preservação dos links e as imagens inline foram verificados localmente, com previews de desktop, celular e modo escuro. Os indicadores de links e imagens no catálogo refletem essas conferências locais. Consulte o [registro de validação e pré-envio](../VALIDACAO.md) para os resultados e pendências operacionais.

O modelo `comercial_direta` usa agora duas fotografias reais copiadas sem edição das referências locais: `Etiqueta2colunas-50x30x2-BRANCA/02Etiqueta2colunas-50x30x2-BRANCA.jpg` e `Tag2colunas-50x75x2/02Tag2colunas-50x75x2.jpg`, em `templates/design-system/references/produtos/`. As cópias utilizadas no envio ficam em `../raw/images/etiquetas-adesivas-referencia.jpg` e `../raw/images/tags-impressao-referencia.jpg`. Os registros de imagegen desta pasta documentam a composição ilustrativa anterior, preservada como histórico.

Os quatro rodapés seguem a estrutura centralizada de agosto e setembro, usando o HTML do rodapé de `setembro-2026/clean/3dicasdiminuirdesperdicio.html`: fundo azul `#0f599c`, ícone do Instagram de 53 px, logotipo de 245 px, divisor, endereço e texto de descadastro. O ícone foi copiado sem alteração para `../raw/images/instagram-rodape.png`; o descadastro preserva o destino de solicitação por email já usado em novembro. Os arquivos raw foram sincronizados para manter esse padrão nas próximas limpezas. Em 27/10/2026, a logo dos cabeçalhos e rodapés foi substituída pela versão de `logo2.png` com transparência real, conforme solicitação do usuário; o restante da estrutura do rodapé foi preservado. O [registro da nova logo](logo2-sem-fundo.md) descreve os arquivos e o prompt utilizados.

| Modelo | Referência | Estrutura aproveitada |
| --- | --- | --- |
| preparacao_black_friday | https://reallygoodemails.com/emails/beefree-trial-ended-upgrade | Chamada central, introdução, três blocos de próximos passos e CTA. |
| produtividade_agilidade_operacao | https://reallygoodemails.com/emails/q1-email-support-group | Faixa temática, abertura editorial com CTA, bloco de orientações e fechamento. |
| valorizacao_marca | https://reallygoodemails.com/emails/rge-studio-ai-confessions-webinar-replay | Carta personalizada, quadro de aplicações, CTA e assinatura. |
| comercial_direta | https://reallygoodemails.com/emails/pocket-meeting-notes-ai-summary | Proposta direta, CTA, produto em destaque, aplicações e novo CTA. |

Cada subpasta guarda a captura original e o HTML original disponibilizado pela referência. Os novos emails usam textos próprios, o logotipo e a paleta da Nova União.

Taste: direção original `page-is-the-object`, seed `282184163`, mantendo paleta e tipografia da marca. A composição específica de cada referência e as restrições do email estático têm prioridade sobre sugestões de páginas com animação. O refinamento posterior com email-marketing-bible usou capturas reais do Chrome, revisão visual independente e verificações de largura, imagens e botões; os relatórios ficam em `tmp/novembro-26/revisao-2026-10-26/`.

Os CTAs usam o contato já presente nos templates anteriores (`553141049383`). O descadastro é um link de solicitação por email; não representa uma integração automática de opt-out. Confirmar os destinos na revisão antes do envio.
