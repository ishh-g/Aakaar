// Human-readable site names for search + display.
//
// The /map/tiles API only returns numeric parcel_id / building_id, so this
// module maps those IDs to the real-world site names seeded in
// db/seed.sql, db/seed_new_sites.sql and db/seed_bharat_mandapam.sql.
// Parcels 1-10 (BVCOE cluster) fall back to DEFAULT_SITE.

export const SITES_BY_PARCEL = {
  11: {
    name: 'Sri Balaji Action Medical Institute',
    aliases: ['Balaji Hospital', 'Balaji Action', 'Balaji'],
  },
  12: {
    name: 'Pacific Mall',
    aliases: ['Pacific', 'Tagore Garden'],
  },
  13: {
    name: 'Jwala Heri Market',
    aliases: ['Jwala Heri', 'Jwala'],
  },
  14: {
    name: 'Indraprastha World School',
    aliases: ['Indraprastha', 'World School', 'School'],
  },
  15: {
    name: 'Bharat Mandapam',
    aliases: ['Bharat', 'Mandapam', 'Pragati Maidan', 'IECC', 'Convention Centre'],
  },
};

export const DEFAULT_SITE = {
  name: 'BVCOE College',
  // Note: 'Bharati Vidyapeeth' intentionally omitted — it substring-matches
  // 'bharat', which must resolve to Bharat Mandapam only.
  aliases: ['BVCOE', 'Paschim Vihar'],
};

export function getSiteForParcel(parcelId) {
  return SITES_BY_PARCEL[parcelId] || DEFAULT_SITE;
}
