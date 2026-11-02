# Public information and disclosure policy

## Purpose

SSSWET publishes enough information for visitors to understand the project's general purpose, public progress and contribution process. Public materials are not intended to disclose every research direction, unpublished concept, technical design, internal method, commercial plan or operational procedure.

## Publication boundary

The public repository and website may contain general descriptions, interface code, public-facing policies and selected software components. They should not contain:
- unpublished inventions, patent-sensitive details or confidential technical designs;
- private research notes, internal roadmaps, detailed implementation plans or trade secrets;
- credentials, private keys, access tokens, database files or administrative secrets;
- personal, donor, customer, payment or fulfilment information;
- third-party material unless its publication and license are authorized.

When a public feature can be described without exposing an internal mechanism, prefer the general description.

## Public submissions

Public issues, pull requests and discussions may be visible, indexed, copied and retained by third parties. Do not submit confidential concepts, unpublished inventions, sensitive datasets, personal information or material that the sender is not authorized to disclose.

A public submission is not a confidential disclosure channel and does not create an NDA. Submitters should review the repository license and applicable platform terms before contributing material.

## Intellectual property

The repository license applies to the files and rights it expressly covers. It does not automatically grant rights to trademarks, patents, confidential know-how, third-party assets or material outside its scope.

A public repository cannot prevent others from reading, copying or preserving material that has already been published. Removing a file from the current branch does not erase earlier commits, forks, mirrors, caches or downloaded copies.

Before publishing a potentially patentable invention or commercially sensitive design, obtain appropriate intellectual-property advice and determine whether a filing or other protection should occur first. Copyright generally protects a particular expression of an idea, not the underlying idea or concept itself. This policy is informational and is not legal advice.

## Public code and private components

Do not rely on minification, obfuscation or hidden frontend fields to protect confidential logic. Code delivered to a visitor's browser can be inspected. Confidential algorithms, keys, datasets and privileged operations must remain on controlled systems and must not be exposed through public endpoints.

The public source tree should contain only material intentionally approved for publication. Local databases and private working directories should be excluded by repository ignore rules, but ignore rules do not remove files already committed.

## License review

The repository currently includes an MIT License. That license permits broad reuse of covered code, including commercial reuse, subject to its terms. Changing the license later does not revoke permissions already granted for copies distributed under an earlier license. Any change to the project's licensing model requires a deliberate review of ownership, contributor rights, dependencies and prior releases.
