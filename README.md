# Observatório Setorial Territorial · Página Brasil

Protótipo da nova página **Brasil** do [Observatório Sebrae](https://observatorio.sebrae.com.br): mapa interativo por estado e município, painéis de micro e pequenas empresas, estudos, calendário e uma versão mobile. Desenvolvido pelo Sebrae (Núcleo de Comunicação da DITEC), com tecnologia da Datawheel.

**Prévias publicadas**
- Desktop: https://claude.ai/artifact/UxabRDhRWqkgpUX1wnwGAe
- Mobile: https://claude.ai/artifact/BsJY9G7fuRhPPmWd91YqvU

Quase todos os números são **reais**: vêm da API do Observatório, com retratos salvos para quando a API não responde. O que ainda é ilustrativo aparece marcado na tela com o selo "fictício" ou a nota "valores ilustrativos" (veja [O que ainda é ilustrativo](#o-que-ainda-é-ilustrativo)).

## Como rodar

```bash
npm install
cp .env.local.example .env.local   # e preencha a chave da API
npm run dev                         # http://localhost:3000
npm run build:estatico              # versão estática em dist-estatico/
```

Node 18.17+. A versão estática (Vite, configuração em `vite.estatico.config.mjs`) é a que vai para as prévias. Ela funciona em qualquer servidor de arquivos, inclusive numa subpasta. Para a prévia mobile, publique o mesmo build com `<html lang="pt-BR" data-versao="mobile">`.

**Chave da API.** `.env.local` guarda `NEXT_PUBLIC_OBS_API` e `NEXT_PUBLIC_OBS_TOKEN`. Ele não vai para o repositório; só o modelo `.env.local.example`, sem chave. A chave do protótipo é provisória: para o site no ar, peça uma chave de uso à equipe do Observatório.

## Páginas e rotas

| Rota | O que é | Componente |
|---|---|---|
| `#/` | Página Brasil: mapa, barra lateral, painéis de MPE e setores | `components/Observatorio.jsx` |
| `#/estudos` | Estudos (Impulsionar Negócios, Potencial Exportador) | `components/estudos/` |
| `#/calendario` | Calendário de eventos DITEC 2026, com botões para Google, Outlook e .ics | `components/calendario/` |
| `#/m` | Versão mobile (Início, Territórios, Relatórios, Comparar, Calendário) | `components/mobile/AppMobile.jsx` |

`components/Raiz.jsx` escolhe a versão. Telas com menos de 768 px abrem o mobile, e `data-versao="mobile"` na tag `<html>` força o mobile. O rodapé tem o botão de voltar à versão mobile.

## Stack

| Camada | Escolha |
|---|---|
| Framework | Next.js 14 (App Router, JS) e Vite para a versão estática |
| Mapa | MapLibre GL JS 4 e Deck.gl 9 (`MapboxOverlay`): pinos do Sebrae, siglas das UFs, seletor da visualização Destaques |
| Gráficos | Recharts (setores) e d3-geo (minimapa do mobile) |
| Estilo | Tailwind 3 com variáveis CSS por tema (`claro`, `navy`, `escuro`) |
| Escalas | d3-scale, d3-array, d3-interpolate |

## Estrutura

```
app/                    layout, página e CSS global (temas)
components/
  Observatorio.jsx      estado da página: indicador, UF, município, camadas, tema, visualização
  Mapa.jsx              MapLibre + Deck.gl: cor por feature-state, hachuras, pinos, foco de IG
  Prancha.jsx           visualização "Destaques setoriais" (quadro, N/S/L/O, círculo de foco, legenda)
  Controles.jsx         busca, dropdowns de indicador e UF, camadas do mapa
  SebraeTerritorio.jsx  programas do Sebrae no território
  TiposPontos.jsx       pontos de atendimento por tipo
  IndicacoesGeograficas.jsx, CadeiasProdutivas.jsx, InovacaoTerritorio.jsx
  diagnostico/          Micro e Pequenas empresas e Setores
  estudos/, calendario/, comparar/, mobile/
  Rodape.jsx, SeletorTema.jsx, LogosParceiros.jsx
lib/
  api/observatorio.js   cliente da API (Tesseract) e consultas do site
  escalas.js            rampas de cor, classes, hachuras, contraste
  dados/                indicadores, municípios, destaques, unidades, calendário…
  dados/retratos/       retratos pequenos que entram no código (totais Brasil e UF)
public/
  geo/                  malhas (estados, municípios do Brasil e por UF), índice e biomas
  dados/                retratos por município, carregados sob demanda
scripts/                geração de malhas e retratos (ver "Atualizar os dados")
```

## Dados e fontes

| Tema | Fonte | Onde |
|---|---|---|
| Pequenos negócios ativos, por porte e por setor; aberturas e baixas | Receita Federal · CNPJ (API do Observatório, cube `RF`) | `public/dados/rf/` |
| Empregos (saldo) | Novo CAGED (API do Observatório) | `public/dados/caged/` |
| Empregados e remuneração em MPE | RAIS 2025 (API do Observatório) | `public/dados/rais/` |
| Atendimentos e cobertura do Sebrae | Sebrae · atendimentos (cube `Sebrae_Atendimento`) | `public/dados/sebrae/atendimentos-municipio.json` |
| Programas (Jornada, Sala do Empreendedor, Cidade Empreendedora…) | API do Observatório, dimensão Jornada do cube `RF`; Delas, ALI e Educação Empreendedora pelo cube de atendimentos | `public/dados/programas/` |
| Pontos de atendimento e pinos | Sebrae · Mapa de Unidades SAS (Qlik interno, nov. 2026), com complemento oficial do RS, do AM e do Sebrae Nacional | `public/dados/sebrae/unidades.json` |
| Indicações geográficas | INPI · listas de IP e DO | `public/dados/inpi/` |
| Inovação, bioeconomia | Sebrae (API do Observatório) | `public/dados/sebrae/` |
| Tempo de abertura | REDESIM | `public/dados/redesim/` |
| Produção agropecuária e extrativa | IBGE · PAM, PPM, PEVS 2024 | `public/dados/ibge/` |
| População (densidade empresarial) | IBGE · Censo Demográfico 2022, SIDRA tabela 4709 (população residente) | `public/dados/ibge/populacao-municipio.json`, `lib/dados/retratos/populacao-uf.json` |
| Calendário | Calendário de Comunicação DITEC 2026 (planilha) | `lib/dados/calendario.js` |
| Municípios (lista) | IBGE · API de Localidades (5.571 municípios) | `public/geo/municipios-index.json` |
| Malhas | IBGE · API de Malhas, qualidade intermediária (5.570 municípios) | `public/geo/` |
| Biomas | IBGE, Biomas 2019, via geobr (IPEA) | `public/geo/biomas.json`, `municipios-biomas.json` |
| Bandeiras | pierrelapalu/icones-bandeiras-br-uf (CC0) | gerado por `scripts/gerar-bandeiras.mjs` |

A documentação oficial das fontes do Observatório fica em https://observatorio.sebrae.com.br/about/fontes-de-dados.

**Estratégia "sempre atualizado":** o site consulta a API ao abrir e, se ela falhar (rede, CORS ou chave), usa o último retrato salvo.

### O que ainda é ilustrativo

- **Interiorização:** só existe por estado (é a parcela fora da capital); com a camada municipal ligada, o mapa mostra o estado e avisa "disponível só por estado".
- **Densidade empresarial:** real por estado e por município (pequenos negócios ativos ÷ população do Censo 2022). Boa Esperança do Norte (MT), criado depois do Censo, fica sem valor.
- **Destaques setoriais por município:** são ilustrativos onde falta o dado de setor da API.
- **Programas do Sebrae:** ficam ilustrativos só se a API e o retrato falharem.
- **Painel de MPE:** alguns cartões de estado e de município, com o selo "fictício".

## Mapa

- **Do Brasil ao município:** clicar na UF enquadra o estado e liga "Indicadores municipais"; clicar no município aproxima e abre a caixa de destaque.
- **Cor por `feature-state`:** os polígonos são carregados uma vez (`promoteId: 'cod'`). Trocar de indicador só atualiza o valor de cada município ou estado, sem reprocessar a geometria.
- **Carga sob demanda:** a malha do Brasil por município (cerca de 2 MB) só é baixada ao ligar a camada sem UF. Cada estado tem um arquivo próprio, mais detalhado, baixado ao entrar nele.
- **Pontos de atendimento:** os pinos são azuis para as agências (sede e escritórios regionais), rosa para as Salas do Empreendedor e verdes (`#3D824F`) para os parceiros. No Brasil aparecem só as agências; ao escolher um estado, todas as unidades dele. O indicador "Pontos de atendimento" liga os pinos sozinho.
- **Destaques setoriais:**
  - cores da paleta Ativo_10: agro `#A7BFD9`, comércio `#44442A`, indústria `#E04510`, serviços `#A69F4E`;
  - concentração forte (QL ≥ 1,5) em hachura cruzada tom sobre tom;
  - seletor amarelo `#FFD400` com contorno escuro ao selecionar um lugar.
- **Indicação geográfica:** ao clicar numa IG, o mapa aproxima a área e mostra o marcador com o nome do produto.

## Design system

- **Cores:** UI kit do Observatório. Navy `#070568`/`#0A2474`, azul `#2A4FDA`, lima `#C9DF60`, verdes `#60B466`/`#36BF76` e off-whites.
- **Rampas do mapa** (`lib/escalas.js`), todas verificadas para daltonismo (ΔE em CAM02-UCS, simulações de deuteranomalia, protanomalia e tritanomalia):
  - verde (`RAMPA_EMPRESAS`): pequenos negócios ativos, setores econômicos e bioeconomia;
  - azul (Ativo_15/14/12): demais indicadores;
  - quente (Ativo_11): interiorização, densidade, aberturas, baixas, MEI, ME e EPP, em teste;
  - biomas: cores do kit.
- **Fontes:** Proxima Nova (títulos e números), Aktiv Grotesk (texto) e Lato (detalhes), pelo kit Adobe Fonts `hpk7hne` (uso não comercial do Observatório). Inter e Lato ficam embutidas como reserva. Veja [Fontes](#fontes).
- **Caixas:** todo card tem ícone, rótulo, ícone de informação com fonte e data, número principal e selo de posição.
- **Ícones:** Iconly Regular (sistema) e ícones de conteúdo do kit.
- **Temas:** `data-theme="claro|navy|escuro"`, com o seletor de três posições no topo.
- **Acessibilidade:** contraste WCAG nos textos; as siglas das UFs ficam escuras ou brancas conforme o fundo; o movimento respeita "reduzir movimento".

## Fontes

O código de incorporação da Adobe Fonts está em `app/layout.jsx` (Next.js) e em `estatico/index.html` (versão estática e prévias):

```html
<link rel="stylesheet" href="https://use.typekit.net/hpk7hne.css">
```

Nomes no CSS (`tailwind.config.js`):

| Uso | Família | Classe Tailwind | Pesos usados |
|---|---|---|---|
| Títulos e números | `proxima-nova` | `font-display` | 400, 500, 600, 700, 800 |
| Texto | `aktiv-grotesk` | `font-body` | 400, 500, 600, 700 |
| Detalhes e notas | `Lato` (embutida, `@fontsource/lato`) | `font-detail` | 400, 400 itálico, 700, 900 |

O kit carrega nas prévias publicadas (conferido em 20 nov. 2026). Ambientes sem acesso à Adobe, como servidores de teste, mostram a Inter no lugar.

## Atualizar os dados

Cada script em `scripts/` converte uma resposta da API (ou um arquivo oficial) num retrato. O cabeçalho de cada script traz a consulta e o uso. Os principais:

| Script | Gera |
|---|---|
| `retrato-ativas-municipio.mjs`, `retrato-setor-municipio.mjs`, `retrato-aberturas-municipio.mjs`, `retrato-abertura-baixas.mjs` | Receita Federal por município e UF |
| `retrato-caged-municipio.mjs`, `retrato-rais-municipio.mjs`, `retrato-rais-mercantis.mjs` | emprego e remuneração |
| `retrato-atendimentos-municipio.mjs`, `retrato-programa.mjs`, `retrato-regionais-sebrae.mjs` | atendimentos, programas e regionais do Sebrae |
| `retrato-populacao.py <2022.xml>` | população do Censo 2022 por município e por estado (XML ou JSON do SIDRA, tabela 4709) |
| `retrato-unidades-sebrae.py <planilha.xlsx>` | pontos de atendimento (planilha do Mapa de Unidades SAS + `scripts/fontes/unidades-complemento.csv`) |
| `retrato-ig-inpi.py`, `retrato-inovacao.mjs`, `retrato-producao.mjs`, `retrato-exportacoes-ue.py` | IG, inovação, produção, exportações |
| `retrato-calendario-ditec.py` | calendário DITEC (planilha em `scripts/fontes/`) |
| `corrigir-aneis.mjs` + `gerar-malhas.sh` | malhas a partir do GeoJSON da API de Malhas do IBGE (simplificação por distância: 1.600 m por estado, 3.500 m Brasil, 2.500 m estados) |

## Branches

| Branch | Conteúdo |
|---|---|
| `main` | versão atual (desktop e mobile) |
| `mobile-v2` | retrato de 20 nov. 2026: paletas novas, unidades do Sebrae, municípios e malhas do IBGE |
| `mobile-v1` | primeira versão mobile (10 nov. 2026) |
| `desktop-final`, `desktop-v1-backup` | backups do desktop |

## Pendências

- **Chave da API:** chave de uso definitiva para o site no ar.
- **Pontos de atendimento:** extração mensal ou API do Mapa de Unidades SAS. Pedir ao Sebrae RS e ao Sebrae AM que cadastrem as agências no SAS, para o complemento manual deixar de ser necessário.
- **Sede e escritórios regionais:** separar os dois no card de tipos (a sede fica na capital; em Brasília, Sebrae DF e Sebrae Nacional).
- **Boa Esperança do Norte (MT):** incluir o contorno quando a API de Malhas do IBGE trouxer o município.
- **Indicações geográficas:** fotos das IGs (`lib/dados/igFotos.js`).
