# Design Read

Use this before code, audit, redesign, or reference translation. Most AI slop starts when the model jumps to a default aesthetic before understanding the product scene.

## Required One-Liner

```text
Reading this as: <surface> for <audience>, in <scene>, using <product|brand|operational> register, with <visual stance>, avoiding <main slop risk>.
```

Examples:

- `Reading this as: B2B developer-tool landing for technical evaluators, in a quick credibility check scene, using brand register, with evidence-led minimalism, avoiding purple AI SaaS reflex.`
- `Reading this as: Korean date-recommendation product UI for couples choosing weekend plans, in a mobile browsing scene, using product register, with warm practical density, avoiding stock-couple imagery and pink heart clichés.`
- `Reading this as: enterprise admin dashboard for operations users, in a repeated daily workflow, using operational register, with high systemness and low motion, avoiding brand-page bento decoration.`

## Signals to Read

1. **Surface** - landing, marketing page, app shell, dashboard, data table, admin, portfolio, docs, redesign, component.
2. **Audience** - buyer, end user, operator, developer, recruiter, public user, internal team.
3. **Scene** - first impression, repeated workflow, comparison shopping, urgent task, mobile browsing, stakeholder review.
4. **Register** - product, brand, operational, editorial, public-sector, campaign.
5. **Existing assets** - logo, colors, typography, screenshots, data, imagery, product constraints.
6. **Reference signals** - named URLs, screenshots, competitors, design systems, anti-references.
7. **Quiet constraints** - accessibility, Korean typography, compliance, trust, performance, low-spec devices, older users.

## Slop Risk Naming

Name one primary risk and optionally one secondary risk.

| Risk | Typical smell | First countermeasure |
|---|---|---|
| Category reflex | AI = purple glow, finance = navy/gold | Pick scene and brand truth |
| Layout reflex | centered hero + pill + 3 equal cards | Choose layout family before code |
| Default component state | shadcn/Material defaults untouched | Token and component customization |
| Evidence slop | fake dashboards, abstract blobs | Use real proof assets or remove preview |
| Copy slop | seamless, unleash, next-gen | Concrete nouns and verbs |
| Redesign damage | changed IA/routes/forms silently | Use redesign protocol |
| Product/brand mismatch | dashboard looks like campaign | Register split |

## Clarification Rule

Ask one short question only if two plausible design reads would materially change the output. Otherwise state assumptions and proceed.

Good question:

```text
Should this preserve the current brand and IA, or are we allowed to overhaul the visual language?
```

Bad question dump:

```text
What colors, fonts, layout, mood, audience, animations, references, and content do you want?
```
