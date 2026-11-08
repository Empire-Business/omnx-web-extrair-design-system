# omnx-web-extrair-design-system

Guia visual: abra o `COMO-FUNCIONA.html` desta pasta (dois cliques; funciona sem internet).

Transforma a pasta de um site já baixado em um arquivo `design-system.html` que abre sozinho: a página recriada com texto genérico e, junto, o catálogo vivo de tipografia, cores, superfícies, animações e componentes, só com o que existe no site.

## O que ela não faz

- Não baixa o site, não cria nem redesenha páginas: isso é do agente **Morfo**.
- Não mantém texto, foto ou logo do site original.
- Serve para estudo e referência. Copiar um site e publicar como seu está fora de questão.

## Como instalar

**Direto do GitHub:** no Claude Code, diga: "Instale a skill a partir de https://github.com/Empire-Business/omnx-web-extrair-design-system". Para atualizar, diga: "Atualize a skill a partir de https://github.com/Empire-Business/omnx-web-extrair-design-system". A IA baixa e copia os arquivos.

Se você já baixou esta pasta:

1. Abra o Claude Code (no aplicativo do Claude, aba **Code**, ambiente **Local**).
2. Escreva: **"Instale a skill que está nesta pasta: `<caminho desta pasta>`"**.
3. Você vai ver a IA copiando os arquivos. Não precisa digitar comando nenhum.
4. Abra uma conversa nova e faça um pedido, como nos exemplos abaixo.

### Instalar à mão

- **Mac ou Linux:** rode `bash install.sh` a partir desta pasta. A skill é copiada para `~/.claude/skills/omnx-web-extrair-design-system`.
- **Windows:** copie esta pasta para `%USERPROFILE%\.claude\skills\omnx-web-extrair-design-system`, ou peça para a IA fazer isso. O `install.sh` não é usado no Windows.
- Funciona em Mac, Windows e Linux, no Claude Code e no Codex. Na instalação, a própria IA faz as adaptações necessárias para o seu computador.

Funciona em Mac, Windows e Linux, no Claude Code e no Codex. Na instalação, a própria IA faz as adaptações necessárias para o seu computador.

## Como pedir

- "Extrai o design system desse site que eu baixei: (caminho da pasta)"
- "Transforma essa pasta em design system."
- "Pega as cores, fontes e componentes dessa referência."

## O que tem na pasta

| Arquivo | Para que serve |
|---|---|
| `SKILL.md` | o passo a passo que a IA segue |
| `scripts/ds_site.py` | faz o inventário do site e confere o resultado; só lê |
| `COMO-FUNCIONA.html` | guia visual |
| `install.sh` | instalação no Mac ou Linux |

## Versões

- 1.0 (08/11/2026): primeira versão.
