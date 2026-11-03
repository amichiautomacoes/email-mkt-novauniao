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
