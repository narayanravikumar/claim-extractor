# 001. Claim schema

## Decision

Claimant name and date of loss are required. Policy number, claim type
and amount claimed are optional. Money is stored as Decimal.

## Why

Without a claimant name and a date of loss you cannot match a claim to a
policyholder or check it against a cover period, so the record is not
usable.

The other three can be recovered by an adjuster, so one illegible box
should not reject the whole record.

Decimal rather than float because binary floating point cannot represent
decimal fractions exactly, so summed claim amounts stop reconciling
against source records.

## Rejected

All fields required. Loses an entire claim over one unreadable box.

All fields optional. The model then guarantees nothing and every caller
has to check every field before using it.

float for money. Convenient, wrong for anything that has to balance.