# Discord Coder Evidence

Checked: 2026-07-29

## Scope

The official Hack4Health Discord invite linked by Kaggle was joined with
explicit user approval. The review was read-only: no message, reaction,
organizer contact, or prize claim was made.

Server: `Hack4Health` (`1411753545660629165`)

Relevant channels:

- `#announcements` (`1424788250450591954`)
- `#competitions` (`1441670252172673205`)
- `#hackathon-discussion` (`1427673543923204259`)
- `#rules` (`1425865654174486658`)
- `#claim-prizes` (`1430963867336577186`)

## Organizer evidence

- On 2026-02-11, organizer `cytokine` announced that Coder sponsors all
  USD 1,500 of the cash prizes and that cash eligibility requires deploying
  the code through Coder. The message was edited on 2026-02-18.
- On 2026-02-26, organizer `jumpy` stated that the project must use Coder's
  product suite somewhere in the project and recommended using it to develop
  a visual website instead of relying only on a dense paper. The same response
  said entries without Coder remain eligible for non-cash prizes.
- On 2026-03-12, `cytokine` rejected Google Sites as a substitute because
  Coder is the sponsor.
- Participant questions about whether a Terraform template with a Jupyter
  workspace or simple port forwarding would be sufficient had no visible
  organizer answer in the indexed search results.
- On 2026-05-26, `cytokine` said Kaggle contains the most up-to-date rules and
  that the shared Drive is mainly for project ideas and datasets.

## Guide search result

Global searches for `Coder`, `deploy`, `workspace`, `coder.com`, and related
terms found the eligibility statements above but no challenge-specific guide,
public Coder URL, template, or step-by-step deployment instructions. The
announcement said more information would follow, but no such guide was visible
in the inspected channels or search results.

This is evidence of a missing public instruction artifact, not proof that none
exists in an unindexed message, deleted post, private channel, or external
document.

## Operational conclusion

Cash track status: **CONDITIONAL GO**.

The local Dev Container, Coder app metadata, autostart launcher, and health
check are useful implementation evidence, but they do not satisfy the observed
requirement by themselves. A real eligible Coder workspace must launch the
project, expose the app, and be captured in the submission demo. Until that
run is completed and recorded, cash-prize eligibility is unproven.

