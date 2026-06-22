// FIFA TLA → { name, iso2 }
// iso2 is used to generate flag emoji via flagEmoji()
export const TEAM_META = {
  ARG: { name: 'Argentina',              iso2: 'AR' },
  FRA: { name: 'France',                 iso2: 'FR' },
  ENG: { name: 'England',                iso2: 'GB' },
  BEL: { name: 'Belgium',               iso2: 'BE' },
  BRA: { name: 'Brazil',                 iso2: 'BR' },
  POR: { name: 'Portugal',              iso2: 'PT' },
  NED: { name: 'Netherlands',           iso2: 'NL' },
  ESP: { name: 'Spain',                  iso2: 'ES' },
  URU: { name: 'Uruguay',               iso2: 'UY' },
  COL: { name: 'Colombia',              iso2: 'CO' },
  USA: { name: 'United States',         iso2: 'US' },
  MEX: { name: 'Mexico',                iso2: 'MX' },
  MAR: { name: 'Morocco',               iso2: 'MA' },
  CRO: { name: 'Croatia',               iso2: 'HR' },
  GER: { name: 'Germany',               iso2: 'DE' },
  SEN: { name: 'Senegal',               iso2: 'SN' },
  JPN: { name: 'Japan',                 iso2: 'JP' },
  KOR: { name: 'South Korea',           iso2: 'KR' },
  IRN: { name: 'Iran',                  iso2: 'IR' },
  SUI: { name: 'Switzerland',           iso2: 'CH' },
  AUS: { name: 'Australia',             iso2: 'AU' },
  TUR: { name: 'Turkey',                iso2: 'TR' },
  ECU: { name: 'Ecuador',               iso2: 'EC' },
  NOR: { name: 'Norway',                iso2: 'NO' },
  SCO: { name: 'Scotland',              iso2: 'GB' },
  AUT: { name: 'Austria',               iso2: 'AT' },
  CZE: { name: 'Czech Republic',        iso2: 'CZ' },
  SWE: { name: 'Sweden',                iso2: 'SE' },
  TUN: { name: 'Tunisia',               iso2: 'TN' },
  EGY: { name: 'Egypt',                 iso2: 'EG' },
  ALG: { name: 'Algeria',               iso2: 'DZ' },
  PAR: { name: 'Paraguay',              iso2: 'PY' },
  KSA: { name: 'Saudi Arabia',          iso2: 'SA' },
  PAN: { name: 'Panama',                iso2: 'PA' },
  CAN: { name: 'Canada',                iso2: 'CA' },
  QAT: { name: 'Qatar',                 iso2: 'QA' },
  GHA: { name: 'Ghana',                 iso2: 'GH' },
  RSA: { name: 'South Africa',          iso2: 'ZA' },
  CIV: { name: "Côte d'Ivoire",         iso2: 'CI' },
  IRQ: { name: 'Iraq',                  iso2: 'IQ' },
  UZB: { name: 'Uzbekistan',            iso2: 'UZ' },
  BIH: { name: 'Bosnia & Herzegovina',  iso2: 'BA' },
  NZL: { name: 'New Zealand',           iso2: 'NZ' },
  JOR: { name: 'Jordan',                iso2: 'JO' },
  CPV: { name: 'Cape Verde',            iso2: 'CV' },
  COD: { name: 'DR Congo',              iso2: 'CD' },
  HAI: { name: 'Haiti',                 iso2: 'HT' },
  CUW: { name: 'Curaçao',              iso2: 'CW' },
}

/** Generate flag emoji from ISO 3166-1 alpha-2 code */
export function flagEmoji(iso2) {
  if (!iso2) return '🏳'
  return [...iso2.toUpperCase()].map(c =>
    String.fromCodePoint(0x1F1E6 + c.charCodeAt(0) - 65)
  ).join('')
}

/** Get display name for a team code */
export function teamName(code) {
  return TEAM_META[code]?.name ?? code
}

/** Get flag emoji for a team code */
export function teamFlag(code) {
  return flagEmoji(TEAM_META[code]?.iso2)
}
