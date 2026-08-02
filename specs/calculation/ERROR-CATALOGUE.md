# Kernel Error Catalogue

| code | HTTP-ish meaning | When |
|---|---|---|
| INVALID_DATETIME | 400 | Naive/aware misuse, bad VedAstro time token |
| INVALID_TIMEZONE | 400 | Offset minutes out of ±14h |
| INVALID_LOCATION | 400 | Latitude/longitude out of range |
| UNSUPPORTED_PLANET | 400 | Planet not in supported set |
| UNSUPPORTED_CONFIG | 400 | Bad ayanamsa/node/ephemeris mode/path |
| EPHEMERIS_UNAVAILABLE | 503 | Reserved when SE files missing in file mode |
| CALCULATION_FAILED | 500 | Unexpected Swiss Ephemeris failure |
