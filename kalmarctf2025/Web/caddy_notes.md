# Caddy

We are given a caddy file to understand the configuration of the proxy being used.

```
{
        debug
        servers  {
                strict_sni_host insecure_off
        }
}

*.caddy.chal-kalmarc.tf {
        tls internal
        redir public.caddy.chal-kalmarc.tf
}

public.caddy.chal-kalmarc.tf {
        tls internal
        respond "PUBLIC LANDING PAGE. NO FUN HERE."
}

private.caddy.chal-kalmarc.tf {
        # Only admin with local mTLS cert can access
        tls internal {
                client_auth {
                        mode require_and_verify
                        trust_pool pki_root {
                                authority local
                        }
                }
        }

        # ... and you need to be on the server to get the flag
        route /flag {
                @denied1 not remote_ip 127.0.0.1
                respond @denied1 "No ..."

                # To be really really sure nobody gets the flag
                @denied2 `1 == 1`
                respond @denied2 "Would be too easy, right?"

                # Okay, you can have the flag:
                respond {$FLAG}
        }
        templates
        respond /cat     `{{ cat "HELLO" "WORLD" }}`
        respond /fetch/* `{{ httpInclude "/{http.request.orig_uri.path.1}" }}`
        respond /headers `{{    .Header | mustToPrettyJson }}`
        respond /ip      `{{ .ClientIP }}`
        respond /whoami  `{http.auth.user.id}`
        respond "UNKNOWN ACTION"
}
```

From this

```
*.caddy.chal-kalmarc.tf {
        tls internal
        redir public.caddy.chal-kalmarc.tf
}
```
I understood that whatever was used as subdomain would be redirected to public. However, this can easily be bypassed by using the `Host` header. Even if I made a request to `public.caddy.chal-kalmarc.tf`, If I change the host header like so `Host: private.caddy.chal-kalmarc.tf`, I would be redirected to to the private host. However, there was another problem, the final check ```@denied2 `1 == 1` ```, this make sure that any request to the flag was denied. 

Looking at the endpoint at the end of the file, the `/headers` one got my attention. Indeed, it was possible to exploit an SSTI using the headers. To retrieve the flag :

```
User-Agent: {{ .env `FLAG` }}
```

`kalmar{4n0th3r_K4lmarCTF_An0Th3R_C4ddy_Ch4ll}`
