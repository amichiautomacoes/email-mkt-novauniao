# Logo2 transparente nos emails de novembro

Atualização de 27/10/2026 solicitada pelo usuário.

- Origem: [logo2.png](../../design-system/references/logo2.png). O arquivo fornecido foi preservado.
- Remoção de fundo: skill `imagegen`, ferramenta integrada `image_gen`, com saída transparente.
- Resultado original: [logo2-sem-fundo-imagegen.png](../../design-system/assets/logo2-sem-fundo-imagegen.png), PNG RGBA de 2188 × 718 px.
- Arquivo para email: [logo2-sem-fundo.png](../../design-system/assets/logo2-sem-fundo.png), exportado proporcionalmente em 640 × 210 px, 75.307 bytes, preservando o canal alpha.
- Cópia da pipeline: [raw/images/logo2-sem-fundo.png](../raw/images/logo2-sem-fundo.png).
- Uso: duas ocorrências em cada um dos quatro emails, por `cid:logo2-sem-fundo.png` no clean. Cabeçalho de 280 px e rodapé de 245 px de largura; alturas proporcionais e redução automática no celular.
- Os quatro cantos do PNG têm alpha 0. O branco das letras e do monograma pertence à arte; não há retângulo branco de fundo.
- Validações: imagens inline carregadas, nenhum CID sem arquivo, links preservados, Chrome em desktop, celulares de 390 e 320 px e modo escuro, além dos 9 testes de renderer/sender aprovados.

## Prompt utilizado na ferramenta integrada

```text
Use case: background-extraction. Asset type: transparent PNG logo for existing HTML marketing emails. Input image 1 is the edit target and the authoritative existing brand logo, not inspiration. Primary request: remove ONLY the solid white rectangular background from the supplied Nova União Etiquetas logo and output true RGBA transparency. Preserve the exact provided logo geometry, original typography, kerning, proportions, thin black outlines, blue shield, white monogram, and exact words 'Nova União' and 'ETIQUETAS', including the tilde over ã. Keep the white interior of the wordmark letterforms as part of the logo, and keep the shield's white monogram: these are foreground artwork, not background. Remove the thin black vertical capture/crop strip at the extreme left edge because it is not part of the logo. Do not redesign, retype, invent, recolor, add shadows, add bevels, or add any new background. Clean sharp original edges, no white rectangular matte or white halo around the outside. Compact horizontal composition, cropped closely around the whole logo with a small transparent margin, approximately 640 px wide by 180 px high if possible. The final logo will sit on an existing blue #0F599C header/footer; that blue must not be painted into the output. Return one transparent PNG asset.
```

## Atualização de 03/11/2026: símbolo com cores invertidas

- A nova versão aprovada pelo usuário está em `templates/logo.png`; a versão original foi preservada ao lado, em `templates/logo-original.png`.
- O fundo da nova imagem é transparente. Apenas o símbolo NU teve azul e branco trocados: escudo branco e monograma azul. Os textos Nova União e ETIQUETAS continuam brancos.
- A cópia usada pela pipeline está em `raw/images/logo-invertida-sem-fundo.png`, idêntica ao PNG aprovado, de 1622 × 970 px, com o canal alpha preservado.
- Os quatro emails de novembro usam a nova logo no cabeçalho e no rodapé, tanto em raw (`images/`) quanto em clean (`cid:`). As larguras permanecem em 280 e 245 px; as alturas proporcionais do arquivo são 167 e 147 px.
- Textos e links preservados; raw e clean conferidos com o cleaner; todas as imagens inline carregadas. Os 9 testes de renderer/sender passaram. As 16 prévias no Chrome (desktop, celulares de 390 e 320 px e modo escuro) passaram sem imagens quebradas, distorção ou rolagem horizontal.
- Prévia e relatório locais: `tmp/novembro-26/logo-invertida-2026-11-03/`. Nenhum email foi enviado.

## Ajuste de cabeçalho e imagens inline em 03/11/2026

- Logo do cabeçalho ampliada de 280 para 420 px (50%), com altura proporcional de 251 px, largura limitada ao espaço disponível e padding do cabeçalho de 0 × 16 px. Rodapés preservados.
- O serializador da Resend omite `filename` somente em imagens com `content_id` e `content_type` de imagem. Os nomes locais e CIDs permanecem disponíveis internamente; anexos comuns preservam seus nomes.
- `filename: false` foi rejeitado pela API com HTTP 422, sem envios aceitos. A omissão de `filename` foi aceita em três novos testes para hugoproamichi@gmail.com, com o prefixo `[Teste logo ampliada]` nos assuntos. Os assuntos do catálogo permanecem inalterados.
- Os 10 testes de renderer/sender, lint e 16 prévias de navegador passaram. A ausência de cartões de anexos no Gmail ainda depende de conferência visual dos testes; a aceitação pela API não confirma esse comportamento.
- Evidências locais em `tmp/novembro-26/logo-cabecalho-anexos-2026-11-03/`, `tmp/resend-teste-cabecalho-inline-novembro-comercial.json` e `tmp/resend-testes-novembro-2026-11-03-cabecalho-inline-omitido-restantes.json`.

## Revisão após conferência do Gmail em 03/11/2026

- O usuário confirmou que omitir `filename` não eliminou os cartões de anexos. Essa tentativa e o teste que a impunha foram revertidos; `resend_client.py`, `tests/test_sender.py` e o manual voltaram à versão do commit `97b011e`. A logo ampliada permanece nos templates.
- Os emails de `setembro-2026` também usam CID e o mesmo caminho de envio da Resend. Os nomes/CIDs são hashes; em novembro são descritivos. A logo de setembro tem 5.040 bytes (490 × 236), enquanto a nova tem 315.051 bytes (1622 × 970). Essas diferenças são hipóteses a verificar, não uma causa comprovada.
- Testes controlados enviados apenas para hugoproamichi@gmail.com: A = template original `4Pontosevitarfalhanaleitura` de setembro; B = comercial de novembro com nomes e CIDs opacos no padrão de setembro. A variante B preserva todos os bytes das imagens e altera os identificadores somente no teste, sem mudar os templates de produção.
- Ambos foram aceitos pela Resend. A comparação visual no Gmail está pendente. IDs e detalhes em `tmp/diagnostico-setembro-novembro-2026-11-03.json`; comparação dos arquivos em `tmp/comparacao-setembro-novembro-inline.json`.

## Correção validada pelo usuário em 03/11/2026

- O usuário confirmou que os testes A (setembro original) e B (novembro com nomes/CIDs no padrão de setembro) não exibiram imagens como anexos no Gmail.
- Aplicado no serializador o padrão do teste B: imagens incorporadas recebem nome e CID de 32 caracteres hexadecimais com extensão; as referências `cid:` no HTML são atualizadas na mesma operação. Os bytes, os tipos MIME e a disposição inline são preservados.
- Os nomes locais continuam legíveis. Anexos comuns mantêm seus nomes, e imagens repetidas podem compartilhar um único CID. Os nomes e CIDs já opacos de setembro são preservados.
- Os quatro emails de novembro mantêm a logo do cabeçalho em 420 px e o rodapé em 245 px. Assuntos, pré-headers, textos e links foram preservados.
- Os 11 testes passaram. O payload real do comercial reproduz exatamente os nomes, CIDs e tamanhos de imagem do teste B aprovado; as quatro prévias são idênticas às já verificadas no navegador. Os templates de setembro foram conferidos sem alterações no HTML ou nos anexos.
- Evidência local em `tmp/novembro-26/correcao-inline-validada-2026-11-03/validacao.json`. Nenhum novo email foi necessário para esta verificação local.
