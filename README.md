# hello-factory

Den mindste mulige løsning under Integrator Software Factory. Den beviser hele vejen:

1. Push til `main` → pipelinen tester, bygger og lægger imaget i `ghcr.io/integrator-dk/hello-factory` og melder versionen til Factory.
2. Factory viser **Ny version klar**. Vælg **Udrul nu** eller **i næste servicevindue**.
3. factory-agenten på `azure-weu-1` starter den nye container, tjekker den, skifter Traefik og lukker den gamle efter opbevaringstiden.
4. https://hello-factory.apps.integrator.dk kræver Entra-login. `/healthz` er åben.

Ny version: hæv `metadata.version` i `factory.yaml`, og push.

**Drift:** se løsningen på https://factory.integrator.dk/solutions/hello-factory. Tilbagerulning: "Rul tilbage" på løsningens side.
