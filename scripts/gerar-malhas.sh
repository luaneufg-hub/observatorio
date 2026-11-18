#!/usr/bin/env bash
# Malhas do site a partir da malha municipal do IBGE, baixada da API de Malhas
# (servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=intermediaria&intrarregiao=municipio,
# nov. 2026: 5.570 municípios; a propriedade codarea vira "id"). Antes: cópia antiga em github.com/tbrugz/geodata-br (5.564).
# Simplificação topológica com o mapshaper: as divisas compartilhadas são simplificadas uma vez só
# (sem vãos nem sobreposições entre vizinhos) e keep-shapes impede que municípios pequenos ou ilhas sumam.
# Os estados (ufs.json) saem da dissolução dos próprios municípios, então batem com a malha municipal;
# -clean preenche as frestas (até 20 km²) que a malha original tem entre municípios vizinhos.
#
# Antes: node scripts/corrigir-aneis.mjs geojs-100-mun.json mun-corrigido.json (ilhas gravadas como anéis)
# Uso: scripts/gerar-malhas.sh <geojs-100-mun.json> <municipios-index.csv> <saida>
#   municipios-index.csv: cod,nome,uf,cap (gerado de public/geo/municipios-index.json)
set -euo pipefail
ORIG=$1; IDX=$2; OUT=$3
MS=${MAPSHAPER:-mapshaper}
# Simplificação por distância mínima entre vértices (metros), e não por porcentagem: preserva a área dos
# municípios pequenos (Taboão da Serra, Cabedelo, Paço do Lumiar…) com o mesmo tamanho de arquivo.
I_UF=${I_UF:-1600}   # arquivos por estado (municipios/UF.json): mais detalhe
I_BR=${I_BR:-3500}   # todos os municípios (municipios-br.json)
I_EST=${I_EST:-2500} # estados (ufs.json): simplifica os municípios e depois dissolve
mkdir -p "$OUT/municipios"
BASE="-i $ORIG -each cod=+id -filter-fields cod -join $IDX keys=cod,cod field-types=cod:number,cap:number"

$MS $BASE -simplify interval=$I_UF keep-shapes -clean gap-fill-area=20km2 -split uf -o "$OUT/municipios/" format=geojson precision=0.0001
$MS $BASE -simplify interval=$I_BR keep-shapes -clean gap-fill-area=20km2 -o "$OUT/municipios-br.json" format=geojson precision=0.0001
$MS $BASE -simplify interval=$I_EST keep-shapes -dissolve uf -clean gap-fill-area=20km2 \
  -each 'cod={RO:11,AC:12,AM:13,RR:14,PA:15,AP:16,TO:17,MA:21,PI:22,CE:23,RN:24,PB:25,PE:26,AL:27,SE:28,BA:29,MG:31,ES:32,RJ:33,SP:35,PR:41,SC:42,RS:43,MS:50,MT:51,GO:52,DF:53}[uf]' \
  -o "$OUT/ufs.json" format=geojson precision=0.0001
