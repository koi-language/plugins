# Requirements

**End users need NO API keys.** Authentication is one-click OAuth via the BRAXIL
backend "Auth Broker": the user signs in to BRAXIL and runs
`python scripts/connect.py --platform <p>` per platform.

This page is for the **BRAXIL operator** who registers the developer apps and
configures the backend. Client Secrets live ONLY in the backend env — never on
the client.

## Operator setup checklist
1. **Register one app per platform** in its developer portal (details below).
2. **Whitelist the callback** in each app:
   `https://api.braxil.ai/auth/social/<platform>/callback`
   (`x` | `linkedin` | `meta` | `tiktok`).
3. **Set the backend env vars** (table below) with each app's id/secret + that
   callback URL. Platforms left unset return HTTP 503 from their routes — the
   server still boots, so you can roll out one platform at a time.
4. **Apply the DB migration** (creates `social_connections` + `social_auth_states`):
   ```bash
   cd backend && npm run db:push      # or: npm run db:migrate
   ```
5. **Connect & verify** from BRAXIL: `python scripts/connect.py --platform x`.

Recommended go-live order: **X → TikTok → LinkedIn → Meta** (register Meta &
TikTok first though — their publish scopes need app review, the longest lead time).

## Backend env vars (set in the backend, never on the client)
| Platform | Env vars |
|----------|----------|
| X        | `X_CLIENT_ID`, `X_CLIENT_SECRET`, `X_CALLBACK_URL` |
| LinkedIn | `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_CALLBACK_URL` |
| Meta     | `META_CLIENT_ID`, `META_CLIENT_SECRET`, `META_CALLBACK_URL` |
| TikTok   | `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_CALLBACK_URL` |

`*_CALLBACK_URL` = `https://api.braxil.ai/auth/social/<platform>/callback`.
Token encryption reuses the existing `API_KEYS_ENCRYPTION_KEY`. Scopes are fixed
in code (`backend/src/modules/social/providers.ts`), not env.

## Developer portals + scopes (operator registration)
- **X** — [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard).
  OAuth 2.0 + PKCE. **Basic tier or higher** (the free tier blocks writes).
  App type: Web/Desktop, confidential client (uses the secret on token exchange).
  Scopes: `tweet.read tweet.write users.read offline.access`
  (`offline.access` is **required** to get a refresh token; without it the
  session dies every ~2h). Callback: `…/auth/social/x/callback`.
- **LinkedIn** — [developer.linkedin.com](https://developer.linkedin.com/).
  The app must be associated with a LinkedIn **Company Page** at creation.
  Products: **"Sign In with LinkedIn using OpenID Connect"** + **"Share on
  LinkedIn"** (personal posting). To post AS a Company Page the user
  administers, also request the **"Community Management API"** product.
  Scopes: `openid profile w_member_social w_organization_social r_organization_admin`.
  Refresh tokens are only issued to approved apps — otherwise the user reconnects
  when the ~60-day token expires. Callback: `…/auth/social/linkedin/callback`.
- **Meta (Facebook + Instagram)** — [developers.facebook.com](https://developers.facebook.com/).
  Business app. Add **Graph API** + **Instagram Graph API**. Scopes:
  `pages_show_list pages_manage_posts pages_read_engagement instagram_basic
  instagram_content_publish business_management`. Requires **Business
  Verification + App Review** for the publish scopes. The user must have a
  Facebook Page linked to an Instagram **Professional/Business** account.
  Callback: `…/auth/social/meta/callback`.
- **TikTok** — [developers.tiktok.com](https://developers.tiktok.com/).
  Content Posting API + PKCE. Scopes: `user.info.basic video.upload
  video.publish`. Requires a UI/UX **app audit** before production. Videos must
  be public `.mp4`/`.mov` URLs. Callback: `…/auth/social/tiktok/callback`.

## How tokens are handled
- The backend stores access + refresh tokens **AES-256-GCM encrypted**, one row
  per (user, platform), and **refreshes automatically** when within ~15 min of
  expiry. X & TikTok rotate their refresh token on each refresh (persisted);
  Meta re-derives a long-lived user token (no refresh token); LinkedIn refreshes
  only if the app is approved.
- Meta page access tokens are themselves secrets → stored encrypted inside the
  connection's `metadata`, and only the requested page's token is vended.
- The desktop client only ever receives a **short-lived access token** at
  publish time (`GET /social/<platform>/token`) and never sees the Client Secret
  or the durable refresh token.

## Plugin runtime
- Python **standard library only** (`urllib`) — no `requests`/Playwright/Flask.
- The user must be **logged in to BRAXIL**; the engine provides the bearer via
  `KOI_AUTH_TOKEN` (and the API base via `KOI_API_URL`), which the scripts read.
