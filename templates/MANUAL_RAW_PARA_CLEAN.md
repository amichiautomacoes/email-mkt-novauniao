# Manual: transformacao de raw para clean

Este manual define o padrao obrigatorio para transformar HTML bruto em template clean antes de qualquer disparo pela Resend.

## Estrutura correta

Os arquivos brutos entram sempre em:

```text
templates/agosto-2026/raw/
```

Os arquivos tratados precisam sair sempre em:

```text
templates/agosto-2026/clean/
```

Cada campanha deve ter:

- `arquivo.html` em `raw`;
- `arquivo.txt` em `raw`, quando existir no pacote original;
- entrada correspondente em `templates/agosto-2026/catalog.json`;
- `arquivo.html` gerado em `clean`.

O nome do template usado na planilha e no worker e sempre o nome do arquivo sem `.html`.

Se o nome tiver acento, confirme tambem a chave sem acento no catalogo. O worker
normaliza a campanha da planilha removendo acentos; por exemplo,
`4dicasinfalíveis` vira `4dicasinfaliveis`.

## Comando de limpeza

Depois de colocar os HTMLs brutos em `raw`, rode:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe scripts\clean_templates.py
```

Esse comando aplica o cleaner em todos os `.html` da pasta `raw` e recria os arquivos correspondentes em `clean`.

## O que a limpeza precisa garantir

Todo email clean precisa cumprir estes pontos antes de teste ou envio:

- O placeholder de nome deve virar `{{ contact.nome }}` no clean.
- No email renderizado, o lead deve receber o valor do campo `nome` da tabela `email_mkt_leads`.
- Nunca pode sobrar `[PRIMEIRO NOME]`, `[Primeiro Nome]`, `*|PRIMEIRO_NOME|*` ou `*|NOME|*`.
- Imagens devem usar `cid:nome-da-imagem.png` no HTML.
- Imagens nao podem ficar como `src="images/..."`.
- Imagens nao podem ficar como `data:image...`.
- Imagens precisam ser enviadas como inline pela Resend, nao como anexo visivel no Gmail.
- Todo link do raw precisa existir no clean.
- Todo `<a href="...">` precisa ter texto clicavel ou imagem clicavel dentro dele.
- Nao pode existir link vazio com a imagem fora do `<a>`.
- Links de CTA, WhatsApp e Instagram precisam ser preservados.
- Tokens de plataforma externa, como `unsubscribe_url`, `tracking_pixel_url` e referencias de RD Station, devem ser removidos quando forem lixo do export.

## Pontos que ja deram erro e nao podem voltar

### Imagens como anexo

Erro: Gmail mostrar as imagens embaixo como anexos.

Padrao correto:

- HTML usa `src="cid:arquivo.png"`;
- payload para Resend usa `content_id`;
- payload para Resend usa `content_disposition: "inline"`;
- nao usar `contentId`, porque este projeto envia via REST.

### Nome do lead nao personalizado

Erro: email chegar com `Ola, [PRIMEIRO NOME]`.

Padrao correto:

- clean fica com `Ola, {{ contact.nome }}`;
- render final fica com `Ola, Hugo` no teste;
- em producao, `Hugo` deve ser substituido pelo `nome` real do lead.

### Link do Instagram vazio

Erro: o `<a href="https://www.instagram.com/novauniaoetiquetas/">` existir, mas sem imagem ou texto dentro.

Padrao correto:

- o icone do Instagram precisa estar dentro do `<a>`;
- ao clicar no icone no email, deve abrir o Instagram.

## Validacao obrigatoria antes de enviar teste

Rode os testes focados:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m pytest tests/test_renderer.py tests/test_sender.py
```

Resultado esperado:

```text
7 passed
```

Se algum teste falhar, nao envie email de teste e nao faca commit.

## Validacao manual recomendada

Renderize ou envie um teste para um email interno e confira no Gmail:

- remetente aparece como `Etiquetas Nova Uniao`;
- assunto esta correto;
- saudacao mostra o nome do contato;
- imagens aparecem no corpo do email;
- Gmail nao mostra imagens como anexos;
- botoes de WhatsApp abrem corretamente;
- icone do Instagram abre corretamente;
- nao existe texto estranho de template/exportacao.

## Sequencia segura de trabalho

1. Colocar novos arquivos em `templates/agosto-2026/raw/`.
2. Atualizar `templates/agosto-2026/catalog.json` com subject e HTML.
3. Rodar `scripts/clean_templates.py`.
4. Rodar `pytest` focado em renderer e sender.
5. Conferir links raw vs clean.
6. Enviar teste real para `hugoproamichi@gmail.com`.
7. Conferir visualmente no Gmail.
8. So depois fazer commit e push.

## Observacao importante

Nao criar migration SQL para esse fluxo. Template, cleaner, renderer e catalogo sao alteracoes de codigo/arquivo. Mudancas no Supabase devem ser feitas diretamente no Supabase usando as variaveis do `.env`, conforme regra atual do projeto.
