# Design system — Nova União Etiquetas

Referência visual para criar os próximos emails da Nova União Etiquetas.

- **Fonte principal:** [Instagram @novauniaoetiquetas](https://www.instagram.com/novauniaoetiquetas/).
- **Data da análise:** 26 de outubro de 2026.
- **Amostra:** perfil, avatar e capas das 11 publicações visíveis na grade pública. Os slides internos dos carrosséis não fazem parte desta análise.
- **Aplicação:** identidade visual da marca adaptada para emails HTML do projeto.

## 1. Como usar esta referência

Antes de criar um email, consultar este arquivo, os [tokens](tokens/) e o [manual de raw para clean](../MANUAL_RAW_PARA_CLEAN.md).

O guia distingue **características observadas nas artes** de **decisões propostas para email**. Tamanhos de texto, espaçamentos, cores neutras de leitura e medidas de botões são escolhas operacionais deste guia. Não representam medidas extraídas de um manual oficial da marca.

A extração com SkillUI foi executada na URL do perfil. Seu resultado automático identificou principalmente o CSS do próprio Instagram. Cores de botões, fontes e animações dessa interface foram descartadas como referência da Nova União. A análise da marca abaixo usa as imagens das publicações, o avatar e um logotipo já existente neste repositório.

## 2. Identidade visual observada

**Direção:** comunicação comercial de produtos para o varejo, com aparência técnica, contraste forte e demonstrações de uso.

| Elemento | O que aparece no perfil | Aplicação nos emails |
| --- | --- | --- |
| Fundos | Azul-marinho muito escuro, preto e ambientes de loja com luz azul | Cabeçalho ou bloco principal escuro; áreas claras para leitura de textos maiores |
| Cores de destaque | Azul intenso, azul mais claro e, pontualmente, ciano | Uma cor de ação por email; azul claro para destaque sobre fundo escuro |
| Títulos | Grandes, sem serifa, em peso forte; branco com palavras em azul | Título curto em HTML, com hierarquia clara e destaque seletivo |
| Marca | Monograma branco em escudo azul; nome Nova União em letras serifadas | Usar o arquivo original do logotipo, preservando proporções |
| Imagens | Etiquetas, impressoras, ribbons, roupas, calçados, embalagens e estoque | Mostrar o produto e sua aplicação no segmento da campanha |
| Composição | Texto na parte superior e produto em destaque abaixo; também há comparações lado a lado | Uma mensagem principal e uma imagem dominante por email |
| Grafismos | Linhas e arcos azuis, pontos, sublinhados, luzes e marcações | Usar com moderação nas artes; manter o HTML simples e estático |

O contraste entre o azul técnico e os materiais do comércio — papel, tecido, jeans, madeira e embalagens — faz parte da linguagem visual. Vermelho de produtos, tons de pele e cores das fotografias não devem virar novas cores de interface.

## 3. Paleta e funções

Os valores das imagens são **aproximações por amostragem**, sujeitas a iluminação, compressão e variações entre artes. O azul institucional foi tomado também do arquivo de logotipo disponível no projeto. As amostras estão em [references/color-sampling.json](references/color-sampling.json).

| Token | Cor | Função | Origem |
| --- | --- | --- | --- |
| `brand.primary` | `#2967A2` | Identidade institucional e links em fundo claro | Cor sólida do logotipo local; próxima ao azul do avatar |
| `brand.accent` | `#1C64CB` | Botão principal e destaques sobre branco | Aproximação do azul do título na arte de impressoras |
| `brand.highlight` | `#4598EF` | Palavras e pequenos destaques sobre azul-marinho | Aproximação da arte sobre problemas de estoque |
| `brand.cyan` | `#1DDEF8` | Acento opcional dentro de artes de produto | Aproximação da publicação sobre apresentação do produto |
| `background.dark` | `#010A1B` | Cabeçalho, bloco principal e áreas de assinatura | Aproximação dos fundos escuros das publicações |
| `background.paper` | `#FFFFFF` | Área principal de leitura | Branco recorrente nas artes, aplicado ao suporte de email |
| `background.soft` | `#F3F7FB` | Fundo externo e blocos secundários | Proposta para email |
| `text.primary` | `#172B3A` | Texto corrido em fundo claro | Proposta para email |
| `text.secondary` | `#526479` | Observações, legendas e rodapé em fundo claro | Proposta para email |
| `text.inverse` | `#FFFFFF` | Texto sobre fundo escuro ou botão azul | Branco recorrente nas artes |
| `border.subtle` | `#DCE5EF` | Separação funcional, quando necessária | Proposta para email |

### Combinações de referência

As razões abaixo foram calculadas para cores sólidas. Fotografias e textos dentro de imagens precisam de conferência própria.

| Texto | Fundo | Contraste calculado |
| --- | --- | --- |
| Branco `#FFFFFF` | Marinho `#010A1B` | 19,80:1 |
| Azul claro `#4598EF` | Marinho `#010A1B` | 6,59:1 |
| Branco `#FFFFFF` | Azul de ação `#1C64CB` | 5,62:1 |
| Azul institucional `#2967A2` | Branco `#FFFFFF` | 5,91:1 |
| Texto `#172B3A` | Branco `#FFFFFF` | 14,55:1 |
| Texto secundário `#526479` | Branco `#FFFFFF` | 6,07:1 |

Usar `brand.highlight` para palavras sobre o marinho. Reservar `brand.accent` para botões e elementos sobre fundos claros. O ciano é um detalhe das artes: branco sobre `#1DDEF8` tem contraste de apenas 1,63:1, portanto essa combinação não serve para os textos dos botões.

## 4. Logotipo

Arquivo centralizado: [assets/logo-nova-uniao-branco.png](assets/logo-nova-uniao-branco.png).

- PNG original de **490 × 236 px**, com transparência, monograma azul e nome branco.
- Copiado sem alteração de `templates/setembro-2026/raw/3dicasdiminuirdesperdicio/images/59e0914a0499ca4a8567debab82856c7.png`.
- Aplicar sobre azul-marinho; largura sugerida de **180 a 200 px** no cabeçalho do email, com altura proporcional.
- Reservar pelo menos **16 px** de espaço ao redor.
- Preservar o nome, o monograma, as cores e a proporção. Não reconstruir o logotipo com uma fonte aproximada.
- O [avatar do Instagram](references/profile.jpg), capturado em 150 × 150 px, serve para comparação visual. Usar o PNG original para o cabeçalho dos emails.

## 5. Tipografia

Nas artes, os títulos têm aparência geométrica, sem serifa e peso forte; algumas chamadas usam letras mais condensadas. O nome da marca tem desenho serifado de alto contraste. **Não foi possível confirmar o nome das fontes a partir das imagens.**

Para o HTML dos emails, padronizar a família `Arial, Helvetica, sans-serif`. A fidelidade vem do peso, da escala, das cores e da composição; o logotipo preserva o desenho original da marca.

| Uso | Desktop | Celular | Peso | Entrelinha |
| --- | --- | --- | --- | --- |
| Título principal | 32 px | 28 px | 700 | 1,15 |
| Título de seção | 22 px | 20 px | 700 | 1,25 |
| Introdução em destaque | 18 px | 18 px | 400 ou 700 | 1,45 |
| Texto corrido | 16 px | 16 px | 400 | 1,50 |
| Botão | 16 px | 16 px | 700 | 1,25 |
| Legenda e rodapé | 13 px | 13 px | 400 | 1,50 |

- Buscar títulos curtos, preferencialmente com até duas linhas no celular.
- Destacar uma expressão relevante em azul; evitar colorir várias partes do mesmo parágrafo.
- Manter parágrafos curtos e alinhados à esquerda. O cabeçalho pode ser centralizado.
- Reservar caixa alta para chamadas muito curtas; texto corrido em caixa normal.
- Informações essenciais, como benefício, condições e CTA, devem existir em texto HTML.

## 6. Estrutura e espaçamento para email

Estas medidas são uma **adaptação proposta para email**, e não uma reprodução da grade do Instagram.

| Parâmetro | Padrão |
| --- | --- |
| Largura do conteúdo | 600 px no desktop; fluida até 100% no celular |
| Organização | Uma coluna como padrão; blocos comparativos podem empilhar no celular |
| Margem interna | 24 px no desktop; 20 px no celular |
| Escala de espaçamento | 4, 8, 12, 16, 24, 32 e 40 px |
| Distância entre parágrafos | 16 px |
| Distância entre blocos | 24 a 32 px |
| Área de toque dos botões | Pelo menos 44 px; altura de referência de 48 px |
| Arredondamento dos botões | 6 px |

### Sequência de referência

1. **Preheader:** complemento curto do assunto, sem repetir o título inteiro.
2. **Cabeçalho:** fundo marinho com logotipo e espaço livre ao redor.
3. **Mensagem principal:** uma dor ou oportunidade, título curto e contexto.
4. **Imagem dominante:** produto ou situação que sustenta a mensagem.
5. **Explicação:** poucos parágrafos ou até três pontos úteis.
6. **CTA:** um objetivo comercial, com texto explícito.
7. **Rodapé:** assinatura, contatos e descadastro conforme o mecanismo vigente do projeto.

Essa sequência pode mudar conforme o conteúdo. Um email curto pode ter apenas cabeçalho, texto, botão e rodapé. As capas verticais 4:5 do Instagram são referências de estilo; não determinam a proporção nem a extensão dos emails.

## 7. Componentes

### Cabeçalho e bloco principal

- Fundo `#010A1B`, logotipo original e textos brancos.
- Usar `#4598EF` para uma palavra ou expressão de destaque.
- Fotografias de loja e produtos podem ocupar uma faixa própria, sem prejudicar a leitura.
- Efeitos de luz e textura, quando desejados, pertencem à imagem; o HTML deve funcionar com fundos sólidos.

### Corpo de leitura

- Fundo branco, texto `#172B3A` e subtítulos no mesmo tom ou em `#2967A2`.
- Separar assuntos por espaço. Usar bordas apenas quando ajudarem a distinguir informação funcional.
- Listas devem conter orientações concretas, sem repetir a introdução.

### Botão principal

- Fundo `#1C64CB`, texto branco, 16 px e peso 700.
- Espaçamento interno de referência: 14 px na vertical e 24 px na horizontal.
- Rótulo orientado ao objetivo: “Solicitar orçamento”, “Encontrar minha etiqueta” ou outra ação específica da campanha.
- Usar um destino real e validado. Se o botão aparecer novamente no fim, manter o mesmo objetivo.
- Links secundários podem ser textuais, em `#2967A2`, com identificação visual de link.

### Imagem e legenda

- Imagem com largura fluida e altura proporcional; sem distorcer produtos ou o logotipo.
- Texto alternativo descritivo, sem repetir todo o corpo do email.
- Explicar em HTML qualquer informação que seja necessária para entender a oferta.
- Comparações precisam manter condições e critérios claros; dados e depoimentos devem vir de materiais confirmados.

### Rodapé

- Visual discreto, em fundo claro ou marinho, com contraste coerente com o restante do email.
- Fonte de 13 px, espaçamento confortável e links com área clicável identificável.
- Usar endereço e contatos vigentes confirmados para a campanha.
- O ícone ou o texto “Instagram” deve estar dentro do link para o perfil.

## 8. Direção de imagens

**Assuntos recorrentes na amostra:** impressoras térmicas, rolos de etiquetas, tags de roupas, ribbons, códigos de barras, prateleiras, vestuário, calçados, embalagens de delivery e produtos alimentícios.

**Tratamento observado:** cenas com profundidade, fundos escuros ou desfocados, luz azul, produtos grandes em primeiro plano e superfícies de trabalho. Algumas peças usam comparação antes/depois e demonstração de um problema de operação.

Para os próximos emails:

- Escolher imagens relacionadas ao segmento e ao assunto daquela campanha.
- Dar destaque ao produto e à aplicação; evitar uma montagem com muitos elementos disputando atenção.
- Preferir fotos e materiais existentes da empresa. Mockups e ilustrações devem ter função demonstrativa, sem serem apresentados como resultados de clientes.
- Usar os grafismos azuis como apoio, preservando a leitura e o foco no produto.
- Manter os códigos, dados de produto e informações da mensagem legíveis em HTML quando forem relevantes para a decisão do leitor.
- As cópias em `references/` são evidências visuais. Para uma nova campanha, selecionar e preparar os arquivos de produção no respectivo `raw`.

## 9. Tom de voz e conteúdo

A comunicação do perfil aproxima produto e rotina comercial: uma pergunta, um problema reconhecível ou um benefício, seguido da aplicação da etiqueta. A bio apresenta etiquetas, tags e ribbons, produtos personalizados e para impressão, com convite para orçamento.

**Tom para email:** direto, útil e comercial. Falar com “você” e “sua loja”; explicar termos como ribbon quando o público precisar; mostrar o benefício antes de detalhar o produto.

Cada email deve ter uma mensagem central e uma ação. Promessas de prazo, disponibilidade, desempenho, economia e depoimentos precisam estar confirmados para aquela campanha; a bio ou uma arte isolada não bastam para criar uma nova promessa.

### Controle de repetição

Agosto e setembro já abordaram estes ângulos:

- Experiência de compra, preço visível, apresentação da marca e agilidade no caixa.
- Organização do estoque por categorias e padronização das referências.
- Etiquetas que descolam, rasgam ou apagam, causando retrabalho e divergências.
- Economia de etiquetas, material e tamanho corretos, redução de desperdício e reimpressões.
- Leitura de códigos de barras, qualidade de impressão e combinação com ribbon.
- Escolha de impressoras de 4 ou 6 polegadas conforme a largura da etiqueta.

Antes de escolher um novo tema, revisar os HTMLs em [agosto/clean](../agosto-2026/clean/) e [setembro/clean](../setembro-2026/clean/). Trocar o título de uma mensagem já usada não cria um novo conteúdo. Os posts abaixo são referências visuais, e não uma lista automática de próximas pautas.

## 10. Aplicação à pipeline

- Seguir o [manual do projeto](../MANUAL_RAW_PARA_CLEAN.md), aplicando seus caminhos ao mês da campanha.
- Nos templates tratados, usar `{{ contact.nome }}` para a personalização.
- Implementar o layout com tabelas de apresentação, estilos essenciais inline e cores de fundo explícitas.
- Usar fontes de sistema e preservar a leitura sem depender de JavaScript, animações, fontes remotas ou imagens de fundo.
- Para usar o logotipo centralizado, copiar o arquivo para `raw/<nome-do-template>/images/` da campanha. O renderer procura os anexos nas pastas `images` do `raw`, não em `design-system/assets`.
- No `clean`, referenciar as imagens por `cid:nome-do-arquivo.png`, conforme o renderer. Não usar caminhos locais nem `data:image` no email final.
- Preservar CTAs e links de Instagram/WhatsApp como links normais, com conteúdo clicável dentro do `<a>` e sem `ses:no-track`.
- Assunto e arquivo HTML devem corresponder à entrada do catálogo do mês.
- Conferir a renderização em desktop e celular e os requisitos do manual antes de qualquer envio.

## 11. Referências observadas

[Captura da grade pública do perfil](references/instagram-profile.png). As capas foram salvas sem edição; `sources.json` registra arquivo, origem e data de captura. A inspeção dos temas abaixo considera o que é visível nas capas.

| Publicação | Característica visual de referência | Cópia local |
| --- | --- | --- |
| [O que nós produzimos](https://www.instagram.com/novauniaoetiquetas/p/De4XITOoAF6/) | Marca central, contexto de loja, impressoras e etiquetas em primeiro plano | [Imagem](references/post-De4XITOoAF6.jpg) |
| [Qual impressora utilizo](https://www.instagram.com/novauniaoetiquetas/p/Dcb8PlYoFZl/) | Fundo quase preto, título branco/azul, comparação de equipamentos | [Imagem](references/post-Dcb8PlYoFZl.jpg) |
| [Por que nossas etiquetas são ideais para sua loja](https://www.instagram.com/novauniaoetiquetas/p/De-EHyvIP89/) | Título condensado, faixa azul e demonstração de uso no varejo | [Imagem](references/post-De-EHyvIP89.jpg) |
| [Seu delivery termina na entrega. Sua marca, não.](https://www.instagram.com/novauniaoetiquetas/p/DejoxqyoDSX/) | Fundo marinho, palavras em azul, embalagem como imagem dominante | [Imagem](references/post-DejoxqyoDSX.jpg) |
| [Seu produto merece uma apresentação melhor](https://www.instagram.com/novauniaoetiquetas/p/Dejn7W9IB64/) | Azul luminoso, detalhe ciano e produto alimentício em destaque | [Imagem](references/post-Dejn7W9IB64.jpg) |
| [O que é um ribbon?](https://www.instagram.com/novauniaoetiquetas/p/Dcb-V8_oIgt/) | Explicação de produto, título forte e composição com rolos | [Imagem](references/post-Dcb-V8_oIgt.jpg) |
| [Se você tem uma loja, provavelmente já passou por isso](https://www.instagram.com/novauniaoetiquetas/p/Dbq1A8roEjQ/) | Contexto de vestuário e calçados, título grande e marcação azul | [Imagem](references/post-Dbq1A8roEjQ.jpg) |
| [O mistério do estoque que não sumia](https://www.instagram.com/novauniaoetiquetas/p/Dbq0qDuICRB/) | Cena narrativa, título em azul claro e explicação em faixa inferior | [Imagem](references/post-Dbq0qDuICRB.jpg) |
| [Como nossas etiquetas ajudam a organizar o estoque](https://www.instagram.com/novauniaoetiquetas/p/DbGgi53oLaY/) | Comparação lado a lado e iluminação azul | [Imagem](references/post-DbGgi53oLaY.jpg) |
| [Por que nossas etiquetas duram mais?](https://www.instagram.com/novauniaoetiquetas/p/DbECswWoPkq/) | Produtos grandes, marca na base e faixa azul no título | [Imagem](references/post-DbECswWoPkq.jpg) |
| [3 maneiras de melhorar a experiência do cliente](https://www.instagram.com/novauniaoetiquetas/p/DbBlDvjoF9e/) | Comparação antes/depois, branco sobre marinho e sinalização azul | [Imagem](references/post-DbBlDvjoF9e.jpg) |

## 12. Conferência de uma nova peça

- [ ] Tema diferente dos ângulos já usados ou aprofundamento claramente novo.
- [ ] Logotipo original, com proporção e contraste corretos.
- [ ] Paleta deste guia; elementos da interface do Instagram não foram incorporados à marca.
- [ ] Título curto, mensagem única e CTA compreensível.
- [ ] Texto essencial em HTML, legível no celular e sem depender das imagens.
- [ ] Imagem coerente com o assunto e informações comerciais confirmadas.
- [ ] Arquivos, personalização, catálogo e links conferidos conforme o manual do projeto.
- [ ] Validações de renderização e envio executadas quando a tarefa envolver uma campanha.
