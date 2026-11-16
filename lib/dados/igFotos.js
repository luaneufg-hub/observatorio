// Fotos das Indicações Geográficas exibidas no marcador do mapa.
// Coloque cada imagem em public/ig/<numero INPI>.webp (quadrada, 320 × 320 px ou mais) e
// acrescente o número aqui. Sem foto, o marcador mostra o selo de IG.
// A lista das IGs, com o nome de arquivo esperado, está em scripts/fontes/ig-fotos.csv.
export const FOTOS_IG = new Set([]);
export const fotoIG = (numero) => (FOTOS_IG.has(numero) ? `ig/${numero}.webp` : null);
