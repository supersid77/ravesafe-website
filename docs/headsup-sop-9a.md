# Heads Up SOP, section 9a: Automatic headlines from testing services

Amendment to the Heads Up Master Monitoring and Editorial SOP v1.0.
Approved by Sid on 28 October 2026 at 19:31.
Approvers: Sid and Jimmy.
Point 4 changed from "written agreement before a source is added" to the wording below, approved by Sid on 29 October 2026 at 11:05, then extended to cover all services and uses including a data log at 11:06. RaveSafe is working with the services and wants to raise awareness of them and support their funding.
Point 7 changed from 48 hours to 4 days, approved by Sid on 28 October 2026 at 19:56, to match a rebuild every 3 days.

1. **What it is.** The Heads Up page may show a separate list called "Latest from testing services". It pulls headlines automatically from named drug checking services. These are not RaveSafe Heads Up entries.
2. **What it can show.** Only the source's own headline, its publication date, the source's name and a link to the original. Nothing is reworded, summarised, classified or added.
3. **Labelling.** The list must always say "Not yet reviewed by RaveSafe". It must stay visually separate from reviewed entries and never use the Alert, Heads Up or One to Watch labels.
4. **Sources.** Any drug checking service can be used, for headlines or for a data log, with approval from Sid or Jimmy. Each service is told what we're using, and is switched off straight away if it asks.
5. **Approval.** Adding, removing or switching on a source needs explicit approval from Sid or Jimmy. Adding the list itself doesn't count as approving any headline in it.
6. **Not a review.** A headline appearing in this list does not mean RaveSafe has checked it. Anything that may meet our threshold still goes through the normal review and approval process before it becomes a Heads Up entry.
7. **Failures.** If a source can't be reached, the list says so and links to the source directly. If the list hasn't updated for 4 days, it hides itself and points people to the source directly. It must never show old headlines as if they were current.
8. **Everything else unchanged.** Apart from this list, the rules in this SOP still apply in full, including "no response means no approval".

## Settings

- Only headlines from the last 30 days are shown (decided by Sid, 28 Oct 2026). Older or undated headlines are left out.
- Up to 12 headlines at a time, and no more than 4 from any one service so the list stays a mix.
- Headlines in other languages are shown in the original language, labelled with the language, as point 2 says nothing is reworded. Added 29 Oct 2026 because European services often spot dangerous batches before they reach the UK.
- The site rebuilds every 3 days to fetch new headlines (GitHub Actions and a Netlify build hook). Chosen to stay within Netlify's free plan. Live alerts are covered on RaveSafe's socials.

- The test site (netlify.app) is hidden from search engines. A source can be set to show there only ("preview") if needed.

## Status

| Source | Permission | Approved to switch on | Enabled |
|---|---|---|---|
| The Loop (UK) | Okay received by Sid, 28 Oct 2026 (written copy to be filed) | Yes, Sid, 28 Oct 2026 19:38 | Yes |
| Energy Control (Spain, Spanish headlines) | Not needed for headlines (point 4 amended). RaveSafe working with them | Yes, Sid, 29 Oct 2026 11:05 | Yes |
| checkit! (Vienna, German headlines) | Not needed for headlines (point 4 amended). RaveSafe working with them | Yes, Sid, 29 Oct 2026 11:05 | Yes |
| drugchecking.berlin (Germany, German headlines) | Not needed (point 4) | Yes, Sid, 29 Oct 2026 13:39 | Yes |
| DrogArt (Slovenia, Slovenian headlines, warnings only) | Not needed (point 4) | Yes, Sid, 29 Oct 2026 13:39 | Yes |
| Modus Vivendi (Belgium, French headlines, early warnings only) | Not needed (point 4) | Yes, Sid, 29 Oct 2026 13:39 | Yes |
