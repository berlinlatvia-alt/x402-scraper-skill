# VPS Hardening Checklist — Phylosophy AGI x402 Relay

**VPS IP:** 54.168.247.83 (Tokyo)  
**Service:** x402 Machine Paid API Relay on port 8402  
**Last Assessment:** 2026-07-30

---

## 1. Current Security State (Findings)

| Check | Result | Details |
|-------|--------|---------|
| **Port 22 (SSH)** | OPEN | Accessible from the Internet. Needs key-only auth + fail2ban. |
| **Port 80 (HTTP)** | CLOSED | No web server listening. To expose TLS-terminated relay, use a reverse proxy. |
| **Port 443 (HTTPS)** | CLOSED | No TLS termination configured. Must be opened behind Caddy/Nginx. |
| **Port 8402 (x402 relay)** | OPEN (HTTP only) | **Exposed directly to the Internet without TLS.** All traffic is plaintext. |
| **TLS/SSL** | NOT CONFIGURED | HTTPS connections to port 8402 fail (SEC_E_INVALID_TOKEN). No certificate installed. |
| **Health endpoint** | Working | `http://...:8402/api/v1/health` returns 200 `{"status":"online"}` |

**Risk:** The relay is fully exposed on the public IP with **no encryption, no authentication, and no proxy**. API keys, USDC payment metadata, and request payloads are sent in cleartext.

---

## 2. Port Exposure Policy

| Port | Service | Status | Recommended Action |
|------|---------|--------|--------------------|
| 22 | SSH | OPEN | Allow only from trusted IPs or use a VPN/tailscale. |
| 80 | HTTP | CLOSED | Open behind reverse proxy for ACME HTTP-01 challenge. |
| 443 | HTTPS | CLOSED | Open behind reverse proxy — this is the **only public entrance**. |
| 8402 | x402 relay | OPEN (HTTP) | **CLOSE EXTERNAL ACCESS.** Relay listens on `127.0.0.1:8402` only, proxied through 443. |

### Final Firewall Rules (target state)

```
Allow Inbound:
  - 22/tcp   → (trusted IPs only, e.g. office VPN)
  - 80/tcp   → (any — for ACME cert renewal)
  - 443/tcp  → (any — public HTTPS traffic)

Drop/Deny Inbound:
  - 8402/tcp → (block from WAN; relay is local-only)
  - All other ports
```

---

## 3. Recommended Reverse Proxy Config (Caddy)

Caddy is the simplest option — it auto-provisions Lets Encrypt TLS certificates.

```caddyfile
# /etc/caddy/Caddyfile

relay.phylosophy.example.com {
    reverse_proxy 127.0.0.1:8402

    # Optional: strip /api prefix if needed
    # handle_path /api/* {
    #     reverse_proxy 127.0.0.1:8402
    # }

    # Security headers
    header {
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
```

### Alternative: Nginx

```nginx
# /etc/nginx/sites-available/relay

server {
    listen 443 ssl http2;
    server_name relay.phylosophy.example.com;

    ssl_certificate     /etc/letsencrypt/live/relay.phylosophy.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/relay.phylosophy.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8402;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name relay.phylosophy.example.com;
    return 301 https://$host$request_uri;
}
```

---

## 4. UFW / iptables Rules

### UFW (Ubuntu)

```bash
# Default deny
ufw default deny incoming
ufw default allow outgoing

# SSH from trusted range only
ufw allow from 10.0.0.0/8 to any port 22 proto tcp
# OR for single IP
# ufw allow from YOUR_OFFICE_IP to any port 22 proto tcp

# HTTP + HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Deny port 8402 explicitly (belt-and-suspenders)
ufw deny 8402/tcp

ufw enable
```

### iptables (any distro)

```bash
# Flush existing
iptables -F
iptables -X

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Loopback
iptables -A INPUT -i lo -j ACCEPT

# Established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# SSH from trusted
iptables -A INPUT -p tcp --dport 22 -s 10.0.0.0/8 -j ACCEPT

# HTTP / HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Log and drop everything else
iptables -A INPUT -j LOG --log-prefix "IPT-DROP: " --log-level 4
iptables -A INPUT -j DROP

# Save
iptables-save > /etc/iptables/rules.v4
```

---

## 5. Stop Exposing Port 8402 Directly

On the VPS, reconfigure the x402 relay service to **bind only to localhost**:

```bash
# In the relay config, change bind address:
# Before:   bind = "0.0.0.0:8402"
# After:    bind = "127.0.0.1:8402"

# Alternatively, if it uses env vars:
export HOST=127.0.0.1
export PORT=8402

# Then restart the service
systemctl restart x402-relay
```

Verify:
```bash
ss -tlnp | grep 8402
# Should show: 127.0.0.1:8402  (NOT 0.0.0.0:8402)
```

---

## 6. Additional Hardening

- [ ] **SSH hardening**: disable password auth, use ed25519 keys, change port optional.
- [ ] **fail2ban**: install and configure for SSH + Nginx/Caddy.
- [ ] **Automatic updates**: enable unattended-upgrades (security only).
- [ ] **Monitoring**: run the `vps-monitor.ps1` script (or port to a Linux equivalent like a systemd timer + curl).
- [ ] **Rate limiting**: configure `rate_limit` in Caddy/Nginx on the `/api` path.
- [ ] **Telegram alerts**: wire the monitor script to a Telegram bot for downtime alerts.
- [ ] **Audit logging**: forward logs to a remote SIEM or log aggregator.

---

## 7. Quick Wins (Priority Order)

1. **Bind relay to 127.0.0.1** — closes the biggest hole immediately.
2. **Install Caddy** — TLS + proxy in one step.
3. **Drop port 8402 from firewall** — defense in depth.
4. **Enable UFW** — simple stateful firewall.
5. **Setup monitoring** — know when the service is down.

---

*Document generated by Phylosophy AGI DevOps — 2026-07-30*
