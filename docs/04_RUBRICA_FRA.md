# Rubric: track-caused derailment narratives -> FRA cause family (Appendix C, "Track, Roadbed and Structures")

You receive short narratives written by US railroads in FRA Form 54 accident reports. Every accident in the file is a derailment whose official primary cause is in the track group. Assign each narrative to exactly ONE label, using only what the narrative says.

Labels:

- ROADBED (FRA codes T001-T099): roadbed settled or soft; washout, rain, slide, flood, snow or ice damage to track; other roadbed defects (soft subgrade, mud, sinkhole, undermined track).
- TRACK_GEOMETRY (T101-T199): cross level irregular; deviation from uniform top-of-rail profile; disturbed or insufficient ballast section; superelevation improper or runoff improper; track alignment irregular, including buckled track or sun kink; WIDE GAGE from any origin (defective or missing crossties, defective or missing spikes or fasteners, gage rods, worn rails); rail rollover or rail turning over under the train because ties or fasteners did not hold gage; other track geometry defects.
- RAIL_JOINT (T201-T299): broken rail of any type (bolt hole crack, base, weld, detail fracture, engine burn, head and web separation, split head, piped rail, transverse or compound fissure); worn rail; mismatched rail-head contour; joint bar broken; joint bolts broken or missing; rail defect with joint bar repair; dry or freshly ground rail; defective crossties or spikes/fasteners ONLY when the narrative does not say the result was wide gage; other rail and joint bar defects.
- SWITCH_FROG (T301-T399): switch point worn, broken or gapped; switch damaged or out of adjustment; switch stand, rod, lug or crank defects; spring or power switch mechanism malfunction; stock rail worn or broken; turnout frog or crossing frog worn or broken; guard rail loose, broken or mislocated; derail defective; retarder or yard skate defective; expansion joint; other frog, switch and track appliance defects.
- OTHER_WAY_STRUCTURE (T401-T499): bridge misalignment or failure; flangeway clogged (ice, snow, mud, debris packed in a crossing or flangeway); engineering design or construction of the track; other way and structure defects.
- UNDETERMINED: the narrative gives no information about which track condition caused the derailment (for example, it only says cars derailed, or only describes the train and the location).

Rules:
1. Use only the text. Do not guess a cause from the location (a derailment "at a switch" or "in the yard" is not by itself SWITCH_FROG; it needs a stated switch, frog or appliance defect).
2. If the text names a track condition, choose the family of that condition even if wording is brief ("due to wide gage" -> TRACK_GEOMETRY; "broken rail" -> RAIL_JOINT).
3. If two conditions are named, choose the one the narrative presents as the cause; if tied, the first mentioned.
4. If nothing in the text identifies the track condition, answer UNDETERMINED. Do not force a family.
