/**
 * Lexicón local de respaldo.
 *
 * Este diccionario se usa cuando la API BETO local esta deshabilitada,
 * no tiene modelo cargado o no responde. Cubre terminos representativos
 * en espanol neutro y variantes LATAM. El usuario puede agregar/quitar
 * terminos desde la pagina de opciones.
 *
 * Categorías:
 *   - insultos: insultos generales y vulgares
 *   - discriminatorios: términos despectivos por origen, género u orientación
 *   - violencia: amenazas y lenguaje agresivo
 *   - latam: modismos LATAM con potencial ofensivo en contexto
 *
 * NOTA: Algunos términos son neutros en ciertos contextos. La detección por
 * lexicón es una aproximacion simple; BETO es el motor contextual principal.
 */

const LEXICON_DEFAULT = {
  insultos: [
    "idiota",
    "imbécil",
    "imbecil",
    "estúpido",
    "estupido",
    "pendejo",
    "tarado",
    "subnormal",
    "retrasado",
    "mongolo",
    "mongólico",
    "mongolico",
    "cretino",
    "gilipollas",
    "capullo",
    "cabrón",
    "cabron",
    "hijo de puta",
    "hdp",
    "hijueputa",
    "puta",
    "puto",
    "perra",
    "zorra",
    "mierda",
    "basura",
    "escoria",
    "asqueroso",
    "asquerosa",
    "inútil",
    "inutil"
  ],
  discriminatorios: [
    "maricón",
    "maricon",
    "marica",
    "puto",
    "tortillera",
    "bollera",
    "travelo",
    "negrata",
    "sudaca",
    "indio de mierda",
    "moro de mierda",
    "gitano de mierda",
    "naco",
    "naca",
    "fachas",
    "facho",
    "feminazi",
    "machirulo",
    "macho de mierda",
    "zurdo de mierda",
    "comunacho",
    "rojo de mierda",
    "menas"
  ],
  violencia: [
    "te mato",
    "muérete",
    "muerete",
    "ojalá te mueras",
    "que te mueras",
    "te voy a matar",
    "te reviento",
    "te parto la cara",
    "te rompo la cara",
    "te pego",
    "ojalá te violen",
    "ahorca",
    "muerete ya",
    "deberías morir",
    "deberias morir",
    "suicidate",
    "suicídate",
    "matate"
  ],
  latam: [
    "weón culiao",
    "culiao",
    "conchatumadre",
    "conchadetumadre",
    "concha de tu madre",
    "ctmre",
    "rctmre",
    "qlio",
    "qliao",
    "saco de wea",
    "flaite culiao",
    "mapuchento",
    "boludo de mierda",
    "pelotudo",
    "forro",
    "sorete",
    "chinga tu madre",
    "vete a la verga",
    "no mames",
    "pinche pendejo",
    "pinche puto",
    "pinche puta",
    "pinche naco",
    "marica hijueputa",
    "pirobo",
    "gonorrea"
  ]
};

/**
 * Devuelve un Set con todos los términos del lexicón por defecto en minúscula.
 */
function lexiconBuildDefaultSet() {
  const all = [];
  for (const cat in LEXICON_DEFAULT) {
    for (const t of LEXICON_DEFAULT[cat]) all.push(t.toLowerCase().trim());
  }
  return Array.from(new Set(all));
}

/**
 * Construye una expresión regular para detectar coincidencias del lexicón.
 * Soporta términos multipalabra ("hijo de puta") y variantes con tildes.
 *
 * @param {string[]} terminos
 * @returns {RegExp|null}
 */
function lexiconBuildRegex(terminos) {
  if (!terminos || terminos.length === 0) return null;
  const escapados = terminos
    .filter((t) => typeof t === "string" && t.trim().length > 0)
    .map((t) => t.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  if (escapados.length === 0) return null;
  // Ordenar por longitud descendente para que multipalabra gane antes que palabra simple
  escapados.sort((a, b) => b.length - a.length);
  return new RegExp("(?<![\\p{L}\\p{N}])(" + escapados.join("|") + ")(?![\\p{L}\\p{N}])", "giu");
}

// Exponer al global del content script
self.LEXICON_DEFAULT = LEXICON_DEFAULT;
self.lexiconBuildDefaultSet = lexiconBuildDefaultSet;
self.lexiconBuildRegex = lexiconBuildRegex;
