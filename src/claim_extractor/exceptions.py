class InvalidPDFError(Exception):
    """Raised when the supplied bytes are not in the pdf"""


class LLMExtractionError(Exception):
    """Raised when the extraction model's output cannot be turned into a ClaimDocument.

    Covers two distinct failures: the model did not return valid JSON, and
    the model returned JSON that does not satisfy ClaimDocument's schema
    (missing required field, wrong type, a rejected value such as a future
    date). Both are treated the same way by the caller: the extraction is
    unusable and must not be guessed at or silently defaulted. See ADR 003.
    """
