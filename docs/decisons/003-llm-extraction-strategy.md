# 003. LLM extraction strategy

## Decision

Extraction uses claude-3-5-haiku-latest, overridable via the
CLAIM_EXTRACTOR_MODEL environment variable. The model is prompted for a
single JSON object and given no tools or structured-output schema
binding.

If the reply is not valid JSON, or is valid JSON that fails
ClaimDocument's validation (missing claimant name, a future date of loss,
a negative amount claimed), the request fails closed: LLMExtractionError
is raised in the extraction layer and the API returns 502 with the
validation detail. Nothing is defaulted, retried, or partially returned.

Extraction accuracy (recall/precision on real claim text) is explicitly
out of scope for this decision and for this project's Month 1 floor. No
eval set exists yet.

## Why

Haiku is the cheap model in the Claude family and this is a five-field
extraction task, not a reasoning task, so the accuracy the largest model
would add does not obviously justify the cost difference. That tradeoff
is asserted here, not measured. If this project moves past a demo, it
needs a scored eval set before the model choice can be defended with
data instead of an assumption.

Failing closed rather than returning a partial record matters because a
claim record with a silently wrong or missing amount is worse than an
error the caller can retry or route to a human. An adjuster acting on a
guessed figure will not know it was guessed. HTTP 502 rather than 500 or
422 because the request itself was fine, the failure is a bad response
from an upstream dependency, which is what 502 means.

## Rejected

A larger model (e.g. Sonnet) by default. No accuracy data exists yet to
justify the added cost; revisit once an eval set exists.

Structured output / forced JSON schema on the API call. Would remove the
JSON-decode failure mode, but this project's Month 1 scope is the API
boundary and failure handling, not squeezing the extraction call itself;
worth reconsidering when this becomes the Month 2 retrieval project's
extraction step.

Returning a partial ClaimDocument with nulls for fields the model failed
to produce validly. Silently hides the failure inside a 200 response;
the caller has no signal that something needs a human look.

Retrying the model call automatically on a bad reply. Adds latency and
cost to every failure without addressing why fixed-schema prompting
without structured output occasionally fails; a caller-driven retry is
cheaper to reason about for a teaching project.
