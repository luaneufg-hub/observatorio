// Ícones dos pontos do Sebrae no mapa (arquivos sede.svg e escritório.svg do kit, nov. 2026).
// Pino com o "S" do Sebrae: agência (azul, maior), Sala do Empreendedor (rosa #FF80C8) e parceiros (verde #3D824F).
// A ponta do pino é a bolinha de baixo: anchorY aponta para o centro dela.
// width/height no <svg> dão tamanho intrínseco à imagem (sem isso alguns navegadores não a rasterizam).
const SVG_SEDE = '<svg id="Camada_2" data-name="Camada 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 54.88 69.2" width="110" height="138"><defs><style> .cls-1 { fill-rule: evenodd; } .cls-1, .cls-2 { fill: #fff; } .cls-3 { fill: #2a4fda; } </style></defs><g id="Camada_1-2" data-name="Camada 1"><circle class="cls-2" cx="27.44" cy="27.44" r="27.44"/><circle class="cls-3" cx="27.44" cy="27.44" r="25.08"/><g id="Layer_1" data-name="Layer 1"><g><polygon class="cls-1" points="41.85 21.24 15.6 21.24 14.63 26.1 40.88 26.1 41.85 21.24"/><polygon class="cls-1" points="40.25 28.78 14 28.78 13.02 33.64 39.27 33.64 40.25 28.78"/></g></g><circle class="cls-2" cx="27.44" cy="64.79" r="4.41"/><circle class="cls-3" cx="27.44" cy="64.79" r="3.26"/></g></svg>';
const SVG_ESCRITORIO = '<svg id="Camada_2" data-name="Camada 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 38.9 48.87" width="78" height="98"><defs><style> .cls-1 { fill-rule: evenodd; } .cls-1, .cls-2 { fill: #fff; } .cls-3 { fill: #ff80c8; } </style></defs><g id="Camada_1-2" data-name="Camada 1"><circle class="cls-2" cx="19.45" cy="19.45" r="19.45"/><circle class="cls-2" cx="19.45" cy="45.74" r="3.12"/><circle class="cls-3" cx="19.45" cy="19.45" r="17.78"/><circle class="cls-3" cx="19.45" cy="45.74" r="2.31"/><g id="Layer_1" data-name="Layer 1"><g><polygon class="cls-1" points="27.67 15.91 12.69 15.91 12.14 18.68 27.12 18.68 27.67 15.91"/><polygon class="cls-1" points="26.76 20.21 11.78 20.21 11.22 22.98 26.2 22.98 26.76 20.21"/></g></g></g></svg>';
// parceiros (Espaço Sebrae, parcerias de atendimento, Parceiro Sebrae): o pino do escritório em verde #3D824F
// (paleta Ativo_15; ΔE ≥ 13,7 do azul e do rosa nas simulações de daltonismo; "S" branco a 4,66:1)
const SVG_PARCEIRO = SVG_ESCRITORIO.replace(/#ff80c8/gi, '#3D824F');
const url = (svg) => `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;

export const URL_SEDE = url(SVG_SEDE);
export const URL_ESCRITORIO = url(SVG_ESCRITORIO);
export const URL_PARCEIRO = url(SVG_PARCEIRO);

// rasterização em 2× do viewBox (nitidez em telas de alta densidade)
export const ICONE_SEDE = { url: URL_SEDE, id: 'sede', width: 110, height: 138, anchorY: (64.79 / 69.2) * 138 };
export const ICONE_ESCRITORIO = { id: 'escritorio', url: URL_ESCRITORIO, width: 78, height: 98, anchorY: (45.74 / 48.87) * 98 };

// altura na tela (px): mesma proporção entre os dois arquivos (69,2 ÷ 48,87 ≈ 1,42)
export const ALTURA_SEDE = 24; // agências (383 no Brasil): menores que as antigas sedes (27), para não cobrir o mapa
export const ALTURA_ESCRITORIO = Math.round((ALTURA_SEDE * 48.87) / 69.2);

/**
 * Atlas com os dois pinos desenhados num canvas, a partir de <img> (funciona em Chrome, Safari e Firefox;
 * o carregador de imagens do deck.gl usa createImageBitmap, que falha com SVG em alguns navegadores).
 * @returns {Promise<{ atlas: HTMLCanvasElement, mapping: object }>}
 */
let atlasPromessa = null;
export function atlasPinos() {
  if (atlasPromessa) return atlasPromessa;
  const carregar = (src) =>
    new Promise((ok, erro) => {
      const img = new Image();
      img.onload = () => ok(img);
      img.onerror = erro;
      img.src = src;
    });
  atlasPromessa = Promise.all([carregar(URL_SEDE), carregar(URL_ESCRITORIO), carregar(URL_PARCEIRO)]).then(([sede, esc, parc]) => {
    const c = document.createElement('canvas');
    const W = ICONE_SEDE.width;
    const E = ICONE_ESCRITORIO.width;
    c.width = W + 2 * E;
    c.height = ICONE_SEDE.height;
    const ctx = c.getContext('2d');
    ctx.drawImage(sede, 0, 0, W, ICONE_SEDE.height);
    ctx.drawImage(esc, W, 0, E, ICONE_ESCRITORIO.height);
    ctx.drawImage(parc, W + E, 0, E, ICONE_ESCRITORIO.height);
    const pequeno = { y: 0, width: E, height: ICONE_ESCRITORIO.height, anchorY: ICONE_ESCRITORIO.anchorY };
    return {
      atlas: c,
      mapping: {
        sede: { x: 0, y: 0, width: W, height: ICONE_SEDE.height, anchorY: ICONE_SEDE.anchorY },
        escritorio: { x: W, ...pequeno },
        parceiro: { x: W + E, ...pequeno },
      },
    };
  });
  return atlasPromessa;
}
