# Imagem atual — campanha comercial direta

> Registro histórico: a revisão de 26/10/2026 com email-marketing-bible substituiu esta ilustração por duas fotografias reais de produto. O PNG foi preservado, mas não é mais referenciado no raw ou clean. Consulte [VALIDACAO.md](../../VALIDACAO.md) para a versão em uso.

- Ferramenta: skill `imagegen`, ferramenta integrada `image_gen` (built-in).
- Uso: campanha “Sua loja preparada para vender mais!”.
- Arquivo utilizado: [produtos-varejo-fim-ano.png](../../raw/images/produtos-varejo-fim-ano.png).
- Formato: horizontal 2:1, aplicado no HTML a 600 × 300 px com largura fluida.
- Arquivo gerado: 1774 × 887 px, PNG de 2.030.324 bytes; proporção preservada sem cortes ou distorção.
- Fundo claro, fotografia hiper-realista de etiquetas, tags, ribbons e impressora térmica sem marca.
- Imagem gerada como composição ilustrativa a partir das referências locais; não representa uma fotografia documental do estoque.
- PNG copiado sem edição do resultado gerado. A imagem anterior foi preservada em `../../raw/images/produtos-nova-uniao.png`.
- Arquivo original: `C:/Users/Hugo Amichi/.codex/generated_images/01a179c8-f9bb-77f1-819b-5b4087b51ce0/exec-e72a886c-ddd4-4ee3-9b55-2c922ce7546d.png`.
- As marcas presentes nas referências foram excluídas da imagem da campanha.
- Integração: raw e clean atualizados; a imagem usa CID e payload inline na versão clean.
- Validação local: links preservados, nome personalizado, imagens carregadas em desktop e celulares de 390 e 320 px, dois botões sem transbordamento e 8 testes de renderer/sender aprovados.

## Referências de produto

1. `Etiqueta2colunas-50x30x2-BRANCA/01Etiqueta2colunas-50x30x2-BRANCA.jpg`.
2. `Etiqueta3colunas-30x50x3/01Etiqueta3colunas-30x50x3.jpg`.
3. `Tag2colunas-50x75x2/01Tag2colunas-50x75x2.jpg`.
4. `Tags3colunasjuntas-35x60x3/01Tags3colunasjuntas-35x60x3.jpg`.
5. `zebraZD220.webp`.

Todas estão em `templates/design-system/references/produtos/`. Foram utilizadas para orientar formas, cortes, colunas, proporções e geometria, sem alterar os arquivos de referência.

## Prompt final utilizado

```text
Use case: ads-marketing.
Asset type: a single hyper-realistic product photograph for a Brazilian retail-supplies HTML marketing email. This is the image asset only, not an email mockup.
Primary request: premium commercial product showcase conveying "Sua loja preparada para vender mais!" through products alone. Do NOT render this concept sentence or any other text.
Input images, all are product-shape references rather than edit targets:
Image 1: real white adhesive-label roll with two parallel columns of rectangular rounded-corner labels on release liner.
Image 2: real white adhesive-label roll with three columns; follow the realistic paper thickness, roll core, die cuts, spacing and scale.
Image 3: real white garment-tag stock in a two-column perforated roll.
Image 4: real garment-tag stock with three joined perforated columns; use its tag proportions and holes as product guidance.
Image 5: reference for realistic compact charcoal desktop thermal printer geometry only. Remove all branding, model labels, logos, lettering, printed marks and labeled controls from the depicted printer.
Scene/backdrop: clean light off-white seamless studio background and matte light display surface, subtle soft contact shadows, refined catalog photography.
Subject: an organized assortment of white adhesive label rolls, plain retail price-label stock, a few barcode label samples with black barcode bars ONLY and absolutely no letters or numbers, blank premium clothing hang tags with small punched holes and thin cords, and two glossy black thermal-transfer ribbon rolls on realistic hollow cores. Include one compact dark desktop thermal printer, based on Image 5, as a secondary supporting product behind the consumables. Foreground label rolls and tags are the visual focus. No other props.
Style/medium: professional hyper-realistic studio product photography, physically plausible paper layers, die cuts, smooth coated label stock, matte thick cardstock, subtle plastic texture and fine ribbon reflections. Real objects with coherent perspective and scale, not a 3D cartoon.
Composition/framing: exact horizontal 2:1 canvas, ideally 1200 by 600 pixels for display at 600 by 300 pixels in email. Preserve this aspect ratio. Balanced, compact landscape arrangement with all essential objects and their edges inside frame, comfortable margins, visually readable when scaled to 320 pixels wide. Three-quarter product-camera view, products in sharp focus, uncluttered commercial composition.
Lighting/mood: large softbox studio illumination, neutral white balance, controlled highlights, gentle natural shadows, modern premium retail presentation. Light bright background, not the previous dark scene.
Constraints: no headline, no body copy, no lettering, no numerals, no prices, no currency symbols, no logos, no brand names, no printer model labels, no watermarks, no buttons, no interface graphics, no people, no promotional text anywhere. Barcode bars may appear on only a few label samples, without human-readable digits or words. Hang tags remain completely unprinted. Do not copy any text or logos from the reference printer. No floating objects, warped rolls, fused objects, impossible label sheets or unrealistic proportions. Output one finished raster image, not a collage, contact sheet, bordered layout or mock email.
```
