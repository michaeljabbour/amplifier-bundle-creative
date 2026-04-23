# Image & Video API Provider Comparison

Privacy, Security, Retention, Ownership & Training Policies — April 21, 2026

---

## Verdicts

- **PASS**: OpenAI, Anthropic, Recraft
- **CONDITIONAL** (requires user warning): Google Gemini, xAI, ElevenLabs (audio only)
- **REMOVED** (abusive terms): Black Forest Labs, Ideogram
- **NOT A PRIVACY PROXY**: ElevenLabs Image & Video aggregator (see note below)

---

## Side-by-Side Summary

| Criterion | OpenAI | Anthropic | Google Gemini | xAI (Grok) | Recraft | ElevenLabs (Audio) |
|---|---|---|---|---|---|---|
| **Trains on API data?** | No (opt-in only) | No (never for API) | No if paid; **Yes if free tier** | No (enterprise); **de-identified data exception** | No (API never used) | **Yes by default** (free/Growth); No on Enterprise |
| **Output ownership** | User owns all | User owns all | User owns; Google may generate similar for others | User owns; **broad irrevocable license to xAI** | User owns (paid plans) | User owns; **sublicensable license if shared publicly** |
| **License to provider** | Minimal — ops only | Minimal — ops only | "To the extent required under applicable law" | **Broad irrevocable + de-identified data owned by xAI** | None for API data | Sublicensable if publicly shared; opt-out available |
| **Data retention** | 30 days; ZDR available | 7 days; auto-deleted | Paid: transient only; Free: unspecified | 30 days; auto-deleted | Not stored for API | 30 days post-deletion; active period unspecified |
| **Deletion rights** | API deletion + ZDR | Auto-deleted at 7 days | Tuned model deletion only | Delete within 30 days | Purged on account deletion | Voice model deletion available; 30-day backup |
| **Opt-out mechanism** | Default off; opt-in only | Default off; feedback only | Use paid tier (no toggle) | Default off for Enterprise | API exempt automatically | Manual toggle in settings; Enterprise defaults to off |
| **Human review** | Flagged abuse only; excludable via ZDR | Opt-in feedback only | **Free: human reviewers read data**; Paid: no | Not addressed | Not addressed | Not detailed |
| **Security certs** | SOC 2 Type II, ISO 27001/27017/27018/27701 | SOC 2 Type II, ISO 27001, ISO 42001 | SOC 2, ISO 27001+, FedRAMP, HITRUST, ISO 42001 | None public | SOC 2 Type II, PCI DSS L1 | Trust Center available; specific certs not confirmed |
| **Data residency** | 10 regions | Not detailed | Vertex AI: full regional controls | Not documented | US East/West | Not documented |
| **DPA available** | Yes | Yes | Yes (paid) | Yes (Enterprise) | Not confirmed | Yes |
| **IP indemnification** | Enterprise agreements | Enterprise agreements | Google Cloud standard | Yes — patent/copyright/trademark | Not documented | Not documented |

---

## Provider Details

### OpenAI — PASS

**Products**: gpt-image-2, gpt-image-1.5, Images 2.0, Sora 2

**Training**: API data is not used for training. Opt-in only. "Data sent to the OpenAI API is not used to train or improve OpenAI models unless you explicitly opt in."

**Retention**: 30 days for abuse monitoring logs. Zero Data Retention (ZDR) available for gpt-image-1, gpt-image-1.5, gpt-image-1-mini (not DALL-E 2/3). ZDR requires prior approval from OpenAI. CSAM scanning always active regardless.

**Ownership**: User owns all inputs and outputs. "Your organization's data always remains confidential, secure, and entirely owned by you."

**Security**: SOC 2 Type II (Jan–Jun 2025), ISO 27001:2022, ISO 27017, ISO 27018, ISO 27701:2019. Data residency in 10 regions with 10% pricing uplift for non-US.

**Sources**: [Data Controls](https://developers.openai.com/api/docs/guides/your-data), [Business Data](https://openai.com/business-data/), [Security & Privacy](https://openai.com/security-and-privacy/)

---

### Anthropic — PASS

**Products**: Claude Opus 4.7 vision (Critic only)

**Training**: API data is never used for training. No exceptions unless user explicitly submits feedback via thumbs up/down. "By default, Anthropic does not use inputs or outputs from commercial products (including the Anthropic API) to train its models."

**Retention**: 7 days for API logs, then auto-deleted (reduced from 30 days in Sept 2025). Feedback data, if opted in, retained up to 5 years. DPA available for 30-day audit window.

**Ownership**: User owns all inputs and outputs under Commercial Terms. Explicit contractual prohibition on training.

**Security**: SOC 2 Type II, ISO 27001:2022, ISO 42001:2023 (AI management systems), HIPAA configurable.

**Sources**: [Training Policy](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training), [Data Retention](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data), [Trust Center](https://trust.anthropic.com/)

---

### Recraft — PASS

**Products**: Recraft V4 (vectors, logos, illustrations)

**Training**: API data is never used for training. Strongest documented API carve-out of any provider. "API inputs and outputs are never used for model training. Data sent through the Recraft API is processed only to generate requested results and is not stored or used to improve models."

**Retention**: API data is not stored. All personal data permanently removed on account deletion.

**Ownership**: Paid plans grant full ownership with commercial rights. Free plans do not grant ownership. Ownership established at time of generation based on plan status.

**Security**: SOC 2 Type II (certified Jan 2026), PCI DSS Level 1 (via Stripe). Azure-hosted, encryption in transit and at rest, annual penetration testing, 24-hour DR restoration target.

**Pending gate**: Written confirmation from help@recraft.ai that the published API training policy is contractually binding and applies to paid API plans.

**Sources**: [Data Use & Training](https://www.recraft.ai/docs/trust-and-security/data-use-and-model-training), [Security Overview](https://www.recraft.ai/blog/recraft-security-privacy-compliance-overview), [SOC 2 Cert](https://www.recraft.ai/blog/recraft-is-soc-2-type-2-certified)

---

### Google Gemini — CONDITIONAL

**Products**: Nano Banana 2/Pro, Veo 3.1 Lite/Fast/Standard

**Training**: Split policy. Paid API (Cloud Billing active): not used for training. Free/unpaid API: used for training AND subject to human review. "Google doesn't use your prompts or responses to improve our products" (paid). Google uses content to "improve and develop Google products and services and machine learning technologies" (unpaid).

**Retention**: Paid tier: transient/cached for abuse detection only. Free tier: no retention limit stated. Grounding with Search: 30 days. Grounding with Maps: up to 6 months.

**Ownership**: Google won't claim ownership of generated content. Reserves right to generate similar content for others. License granted "to the extent required under applicable law."

**Human review**: Free tier: human reviewers may read, annotate, and process API input/output (disconnected from account before review). Paid tier: no review for improvement purposes.

**Security**: Most comprehensive certification portfolio — SOC 2, ISO 27001/27017/27018/27701, ISO 42001, FedRAMP High, HITRUST, PCI DSS v4.0. Full regional data residency via Vertex AI.

> **User warning required**: The Creative bundle must enforce Cloud Billing (paid API tier) at configuration time. Free-quota API keys must be rejected with a clear message explaining that free-tier usage sends all inputs into Google's training pipeline and exposes them to human review. Users must understand the privacy difference before proceeding.

**Sources**: [Gemini API Terms](https://ai.google.dev/gemini-api/terms), [Certifications](https://docs.cloud.google.com/gemini/docs/discover/certifications), [Data Residency](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/data-residency)

---

### xAI (Grok) — CONDITIONAL

**Products**: Grok Imagine Image, Grok Imagine Video

**Training**: Enterprise API terms explicitly prohibit training on User Content. However, xAI may create and use "de-identified data" from your usage to improve products, and xAI owns that de-identified data permanently. "xAI shall not use any User Content for any of its internal AI or other training purposes." But: "xAI may create and use de-identified data related to Customer's use of the Services to improve xAI's products and services...and such de-identified data will be owned by xAI."

**Retention**: User Content auto-deleted within 30 days unless legally required or flagged for safety/compliance.

**Ownership**: Users own outputs but grant xAI a broad irrevocable license for service provision, improvement, and analysis. De-identified derivatives become xAI property permanently.

**Security**: No public certifications documented (no SOC 2, no ISO). DPA available for Enterprise customers. IP indemnification covers patent, copyright, and trademark claims.

> **User warning required**: The Creative bundle must display a notice at configuration time explaining that xAI's de-identified data clause means derivative information from your prompts and outputs may be used by xAI indefinitely, even after you delete your data. Users sending original artwork or character designs should understand this risk. Additionally, xAI has no public security certifications — users in regulated industries should evaluate accordingly.

**Sources**: [Enterprise ToS](https://x.ai/legal/terms-of-service-enterprise), [Privacy Policy](https://x.ai/legal/privacy-policy), [DPA](https://x.ai/legal/data-processing-addendum)

---

### Black Forest Labs (Flux) — REMOVED

**Products**: Flux 2 Pro, Flux Kontext

**Why removed**: BFL's API terms grant them a perpetual, irrevocable, worldwide, fully sublicensable license over all inputs and outputs, and explicitly allow training on all data with no opt-out. There is no disclosed retention period and no deletion mechanism. These terms are incompatible with protecting original creative work.

Key policy language: "We may use Inputs and Outputs to train and improve our artificial intelligence models, algorithms, and related technology, products, and services." License: "Fully paid, royalty-free, perpetual, irrevocable, worldwide, non-exclusive and fully sublicensable right and license to use, modify, and distribute."

Sending children's book artwork through this API means BFL permanently owns a sublicensable license to that artwork and can use it to train future models. No opt-out exists. No deletion is possible. Revisit only if BFL materially changes their terms.

**Sources**: [Flux API Service Terms](https://bfl.ai/legal/flux-api-service-terms), [Developer ToS](https://bfl.ai/legal/developer-terms-of-service), [Privacy Policy](https://bfl.ai/legal/privacy-policy)

---

### Ideogram — REMOVED

**Products**: Ideogram V3 (typography-focused generation)

**Why removed**: Ideogram's policies contradict themselves. The API Terms say "shall not use any User Input or User Output to train the Ideogram AI Model," but also claim "the right to use in any manner all User data received via the Ideogram API." The Privacy Policy separately states data may be used "including by training the models that power the Services." There is no disclosed retention period, no deletion mechanism, and no security certifications.

When a provider's own legal documents contradict each other on whether they train on your data, you cannot rely on the protective clause. Combined with zero transparency on retention, deletion, and security, this provider cannot be trusted with original artwork. Revisit only if Ideogram resolves the contradiction and publishes clear, consistent terms.

**Sources**: [API Terms](https://ideogram.ai/legal/api-tos), [Privacy Policy](https://ideogram.ai/privacy), [Terms of Service](https://ideogram.ai/legal/tos)

---

### ElevenLabs (Audio) — CONDITIONAL

**Products**: Voice synthesis (TTS), sound effects, music generation

**Training**: Defaults to ON for Free and Growth tiers — voice data and inputs train ElevenLabs models unless you manually opt out in account settings under "Data use > Terms and Privacy." Enterprise tier defaults to OFF. "You may opt out of ElevenLabs' use of your Personal Data for training at any time."

**Retention**: 30-day backup retention after deletion. Active data retention period not clearly specified. Voice models can be deleted on request.

**Ownership**: User retains rights to inputs. However, if output is shared publicly (even accidentally), ElevenLabs gains a "worldwide, royalty-free, fully paid-up, transferable, and sublicensable license" for commercial purposes. Opt-out available in product settings, but prior sublicenses survive.

**Security**: Trust Center at compliance.elevenlabs.io. DPA available. GDPR and CCPA compliant. Specific certifications (SOC 2, ISO) not confirmed from public documentation.

**Third-party data sharing**: ElevenLabs may share input/output with third parties for content moderation and safety. Personal data shared with vendors for verification, moderation, data analysis, and payment processing.

> **User warning required**: Bundle must verify Enterprise tier or confirm training opt-out is active before allowing audio generation calls. Display warning: "ElevenLabs trains on your audio data by default on Free and Growth plans. Verify training is opted out in your account settings, or use an Enterprise plan, before generating audio for original creative work."

**Sources**: [Privacy Policy](https://elevenlabs.io/privacy-policy), [DPA](https://elevenlabs.io/dpa), [Service-Specific Terms](https://elevenlabs.io/service-specific-terms), [Image & Video Terms](https://elevenlabs.io/image-and-video-terms)

---

### ElevenLabs Image & Video Aggregator — NOT A PRIVACY PROXY

**Important**: ElevenLabs offers image and video generation through an aggregator that provides access to Flux 2 Pro, Flux Kontext, Nano Banana, GPT Image 1/1.5, Sora 2, Veo 3/3.1, Kling 2.5/3.0, and others through a single platform. This does NOT solve the privacy problems with removed providers.

**Why it's not a proxy**: ElevenLabs' Image & Video Terms explicitly state the service is "powered in part by one or more third party model providers" and that users "must comply with any and all applicable Third-Party Provider terms." Your data still flows to the underlying provider. Using Flux through ElevenLabs still subjects your data to BFL's perpetual sublicensable training license.

**Why it's actually worse for clean providers**: For models we already cleared (OpenAI, Google, Anthropic), routing through ElevenLabs adds ElevenLabs' own data handling, training defaults, and sublicensing terms on top of the provider's already-clean terms. You gain convenience (one API) but lose privacy guarantees.

**Recommendation**: Do not use ElevenLabs as an image/video aggregator for the Creative bundle. Use direct API integrations with cleared providers. Use ElevenLabs only for its core audio capabilities (voice, sound effects, music) on the Enterprise tier with training opted out.

---

## Recommendations for the Creative Bundle

1. **OpenAI, Anthropic, Recraft** — integrate freely. Recraft pending written confirmation email.

2. **Google Gemini** — integrate with a config gate. Bundle must verify Cloud Billing is active before allowing API calls. Display a warning if a free-tier key is detected: "Free-tier Gemini API keys send your data to Google for training and human review. Use a paid API key to protect your work."

3. **xAI** — integrate as a stub, gated on legal review. Display a notice at configuration: "xAI may create de-identified derivatives of your usage data and retain them permanently. xAI has no public security certifications. Proceed only if you accept these terms."

4. **ElevenLabs (audio only)** — integrate for voice synthesis, sound effects, and music composition in video trailers. Require Enterprise tier or verified training opt-out before allowing calls. Display a warning: "ElevenLabs trains on your data by default on Free and Growth plans. Verify training is opted out or use Enterprise before generating audio for original creative work." Do NOT use ElevenLabs as an image/video aggregator — use direct provider APIs instead.

5. **Black Forest Labs, Ideogram** — do not integrate. Dropped from scope entirely. Using them through ElevenLabs' aggregator does not change this — their underlying terms still apply.

---

*Compiled April 21, 2026 from publicly available terms, privacy policies, and documentation. Policies may change. Always verify current terms before production use. This is not legal advice.*
