# The web application

One Django project, `pib`, is the whole web tier. On `fpgas.online` and the
per-site names such as `ps1.fpgas.online` and `welland.fpgas.online` it serves
the classic board pages: a grid of boards, one page each, a camera feed and a
terminal. On `tinytapeout.fpgas.online` the same process serves the Tiny Tapeout
catalogue instead, chosen by the `Host` header alone. Nothing on either host
asks anyone to log in and nothing reserves a board. These pages cover what a
visitor sees, which Django apps the project is made of, the URL map, and how the
`site` role puts it on the gateway.

Which do you need?

(what-a-user-sees)=
- **[What a user sees](webapp/visitors.md):** for you if you want to know what a visitor to fpgas.online or tinytapeout.fpgas.online sees and can do.
(applications)=
(url-map)=
- **[Its Django apps and URL map](webapp/apps-urls.md):** for you if you are working on the code and want the Django apps the project is made of and which URL goes where.
(deployment)=
- **[Deployment](webapp/deployment.md):** for you if you run a gateway and want to know how the site role puts the web application on it.
(camera-streams)=
(gateway-api)=
- **[Camera streams and the gateway API](webapp/streams-api.md):** for you if you want to know how the board pages' camera streams and the gateway API are served.
(known-gaps)=
- **[Known gaps](webapp/known-gaps.md):** for you if you want to know what the web application does not do yet, or does wrong.
(sources)=
- **[Sources](webapp/sources.md):** for you if you want the sources behind these pages.

```{toctree}
:hidden:

What a user sees <webapp/visitors>
Apps and URL map <webapp/apps-urls>
Deployment <webapp/deployment>
Camera streams, gateway API <webapp/streams-api>
Known gaps <webapp/known-gaps>
Sources <webapp/sources>
```
