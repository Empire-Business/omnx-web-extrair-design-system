---
name: omnx-web-extrair-design-system
description: "Transforma a pasta de um site já baixado num design system em HTML que abre sozinho: a página recriada com texto genérico e, ao lado, tipografia, cores, superfícies, animações e componentes reais do site, só com o que existe nele. Use quando pedirem 'extrai o design system desse site', 'transforma essa pasta em design system', 'quero o DS dessa referência', 'pega as cores, fontes e componentes deste site baixado', 'cataloga o visual dessa página'. Precisa da pasta do site no computador. Não use para criar, recriar ou modernizar um site, baixar um site, converter imagem em HTML nem misturar identidades (morfo), nem para copiar um site e publicar como se fosse seu."
---

# Extrair design system de um site baixado

Pega a pasta de um site e entrega um arquivo `design-system.html` com duas partes: a página recriada com texto genérico (Visão geral) e o catálogo vivo do que ela usa (Componentes). Serve de referência para criar páginas novas. O trabalho é de transcrição: ler o código e organizar, sem inventar.

## Como falar com a pessoa

Ela pode nunca ter usado IA. No começo da conversa, diga em duas linhas o que você faz. Faça uma pergunta por vez. Explique termo técnico em meia frase (design system é o catálogo de cores, fontes e peças visuais de um site). Nunca peça para ela digitar comando: quem roda o script é você. Termine cada resposta com o próximo passo.

## Quando não usar

| Pedido | Quem resolve |
|---|---|
| Criar, redesenhar ou publicar site, baixar referências, imagem para HTML, misturar identidades | agente Morfo |
| Copiar um site para publicar como próprio | recuse: referência serve para estudar |

## Regras

1. **Só o observado.** Sem componente, cor, fonte, animação ou variação que não exista no site. Categoria sem item: escreva "não observado". O que aparece na tela por padrão do navegador entra rotulado como "padrão do navegador". Fonte em `fontes_sem_arquivo` entra como "citada, não carregada".
2. **Nunca edite a pasta original.** Trabalhe sempre na cópia.
3. **Texto genérico em tudo que aparece:** títulos, botões, menus, depoimentos, preços, `alt`, `title`, placeholders. Mantenha o tamanho aproximado, para não mexer no layout. Logo, foto de pessoa ou imagem com marca: troque por imagem neutra do mesmo tamanho. Imagem sem marca pode ficar, registrada no README de saída.
4. **Mantenha o movimento.** Limpar código nunca remove animação, interação ou fundo animado.
5. **Reaproveite as classes** do site. Os componentes usam o CSS original, sem estilo reescrito do zero.
6. **Diga o que ficou diferente.** Nunca declare "idêntico" sem comparar.

## Passos

1. **Confirme a pasta.** Só veio link? Explique que a skill precisa do site salvo no computador: no navegador, salvar como "Página da Web, completa". Várias páginas: pergunte qual usar (padrão `index.html`).
2. **Pergunte onde salvar.** Sugira uma pasta nova ao lado da original, com o nome `<site>-design-system`. Se ela já existir, pergunte: substituir, criar `-v2` ou cancelar.
3. **Inventário.** Rode `python3 "<pasta desta skill>/scripts/ds_site.py" inventario <pasta-do-site> --pagina <pagina>`. `<pasta desta skill>` é a pasta onde está este `SKILL.md`. A saída é JSON com cores, fontes, tamanhos, medidas de tela, animações, modo de abertura, rastreadores e links externos. Use isso como base do catálogo; não confie na memória.
4. **Modo de abertura.** Se `modo` for `precisa_servidor`, pergunte: (A) converter para abrir com dois cliques, demora mais; ou (B) manter o servidor local, mais rápido agora, mas sempre precisa dele para abrir. Em A, reescreva caminhos absolutos, embuta dados e troque módulos, testando a cada passo. Em B, registre o comando no README de saída.
5. **Copie** o necessário para a pasta de saída, em `assets/{css,js,img,fonts,video}`, salve a página como `design-system.html`, corrija os caminhos e confira que a cópia abre igual.
6. **Limpe:** troque o texto (regra 3) e tire comentários, código morto, rastreadores e scripts de terceiros sem função visual. Na dúvida se um código faz efeito, mantenha e registre no README.
7. **Monte a Visão geral:** cabeçalho com navegação, depois a página recriada numa `<section id="overview">`. Estilo e script só da moldura (navegação, rótulos, botão de repetir animação) vão em `<style data-ds-moldura>` e `<script data-ds-moldura>`. Menu ou elemento fixo do site não pode cobrir o cabeçalho: ajuste só a posição e registre. Compare com o original em tela de computador e de celular, se tiver captura de tela, depois de as animações de entrada terminarem: tipografia, cores, gradientes, menu. Corrija o que der.
8. **Aprovação 1.** Mostre como abrir, o que ficou diferente e pergunte se a Visão geral está fiel. Só siga com "pode seguir".
9. **Monte o catálogo** no mesmo arquivo, uma seção por vez, com cada item funcionando de verdade e rótulo "nome · classe · onde aparece":
   - `#tipografia`: cada nível, com tamanho em computador, tablet e celular (sem corte para tablet, repita o valor de computador), peso, entrelinha, cor;
   - `#cores`: agrupadas por função, com HEX, RGB, HSL; gradientes com direção;
   - `#superficies`: cartões, painéis, vidro, borda, raio, sombra;
   - `#icones`;
   - `#motion`: cada animação rodando (se for de uma vez só, ponha botão de repetir), com gatilho, duração e curva quando legíveis;
   - `#componentes`: ação, formulário, cartões, dados, navegação, feedback, mídia, outros observados, com os estados que existem;
   - `#layout`: colunas, largura máxima, espaçamento, medidas de tela.

   Na amostra, altura e posição podem mudar para caber na página; cor, fonte, raio e sombra, nunca.
10. **Confira.** Rode `python3 "<pasta desta skill>/scripts/ds_site.py" conferir <pasta-do-site> <pasta-de-saida>`. Resolva tudo até `ok` ser verdadeiro. Link externo só fica se a pessoa aceitar, registrado no README. Confira também `possiveis_nomes_de_marca`, `so_na_moldura` (só a moldura pode ter cor própria) e se a Visão geral continua intacta.
11. **Aprovação 2.** Mostre o resumo (níveis de texto, cores, componentes, animações, categorias não observadas, diferenças) e pergunte se falta algo ou se sobra algo.
12. **Feche.** Escreva `README.md` na pasta de saída: origem, data, como abrir, diferenças conhecidas, categorias não observadas. Entregue o caminho e esta frase para reutilizar: "Crie [página] usando este design system como referência: [caminho do design-system.html]."

## Direitos

O resultado é material de estudo. Texto, fotos e logos do site original pertencem ao dono dele: não entram no catálogo. Antes de publicar algo inspirado, adapte a identidade à sua marca.

## Se der erro

Pasta sem HTML: explique e peça o site salvo de novo. Baixado pela metade (arquivos faltando na `arquivos_quebrados` do inventário): avise o que falta e peça novo download. Sem Python: faça o inventário lendo o CSS e avise que a conferência automática não rodou.

## Outro sistema operacional

O script usa só a biblioteca padrão do Python 3. Adapte e conte o que funcionou de verdade:

- **Python:** `python3` (macOS, Linux), `py -3` ou `python` (Windows). Sem Python, não instale nada só para isso.
- **Abrir arquivo:** `open` (macOS), `start ""` (Windows), `xdg-open` (Linux).
- **Servidor local:** `python3 -m http.server`; no Windows, `py -3 -m http.server`.
- **Pasta pessoal:** `~` é `%USERPROFILE%` no Windows. Caminho com espaço vai entre aspas.
- **Instalar no Windows:** copie esta pasta para `%USERPROFILE%\.claude\skills\omnx-web-extrair-design-system`.

## Outra ferramenta (Codex e outras)

Compatível com Claude Code, Codex e outras ferramentas de agentes, em Mac, Windows e Linux. Se a pessoa pedir para instalar
fora do Claude Code, a IA dela adapta na hora, testa no computador dela e conta o que realmente funcionou:
