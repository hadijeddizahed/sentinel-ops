# Runbook: Authentication Gateway Federation Timeout

## Error Code: ERR-AUTH-504 / IDP_TIMEOUT

### Symptoms
- Upstream OAuth 2.0 / SAML identity federation provider fails to return tokens within 5000ms.
- End-users receive HTTP 504 Gateway Timeout on login endpoints.

### Immediate Mitigation Steps
1. Check identity provider (Okta/Azure AD) public status page.
2. If IdP is healthy, check connection timeout thresholds in `auth-service` config.
3. Perform a zero-downtime rolling restart of the auth gateway:
   ```bash
   kubectl rollout restart deployment/auth-gateway -n production
   ```
4. Failover to the secondary backup identity federation endpoint if latency persists > 5 minutes.

