# Ask for the current user's Git destination

A shared skill does not grant access to its author's repositories and does not authorize publication there. Never use an example repository, the skill author's account, a previous user's destination, or the checkout's `git origin` as the default publication target.

## Required destination question

If the current user has not already explicitly supplied their own authorized destination for this task, ask before any remote write:

> Which repository in your own GitHub account or organization should receive this project and video? Please provide its URL and, if relevant, the branch and folder.

If they do not have one yet, ask them to create an empty repository in their own account or organization and provide its URL. Continue local analysis, mapping, reconstruction, rendering, and validation while waiting. Do not publish to the skill author's repository as a fallback. Creating a remote repository on the user's behalf requires their explicit request and available authorized credentials; do not assume that request from a missing destination.

If the current user already supplied the authorized URL, reuse it without asking again. Derive branch/folder preferences from their instructions or existing repository conventions; clarify a genuinely consequential unresolved choice. A repository mentioned only as a style reference, example, source of the skill, or previous production is not a publication destination.

## Before the first remote write

- Confirm the chosen owner/repository matches the current user's instruction and their stated account or authorized organization.
- Inspect the actual remote URL and branch; do not silently push to an existing remote that points somewhere else.
- If the user-provided repository does not exist or access fails, diagnose using existing authentication. Request only the missing creation/access action. Keep completed local output; never substitute another person's repository.
- Follow the requested project/video folder layout and visibility. Do not change public/private settings without authorization.
- Publish only the files authorized for that destination. Source-video inclusion in this example does not imply permission to expose another user's private input.

After pushing, verify the remote commit and actual file paths. Return links for that user's repository, not links copied from the example. A missing destination blocks publication only; it does not block local production or justify dropping the finished project/video.

## Case-study distinction

The included project demonstrates a past production and has local case-specific output paths. It contains no reusable authorization to publish anywhere. Repository hosting of this skill itself is not consent to upload new users' work into that hosting repository.
