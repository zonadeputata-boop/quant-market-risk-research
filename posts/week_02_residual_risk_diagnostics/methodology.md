# Methodology - Week 02 Residual Risk Diagnostics

This note extends the Week 01 rolling OLS output.

Core model:

```text
r_asset,t = alpha + beta x r_SPY,t + epsilon_t
```

Core diagnostics:

- latest beta
- latest R²
- stress beta
- unexplained share = 1 - R²

The purpose is to show why beta should be read together with explanatory power. A beta estimate can be misleading if R² is low or unstable.

Not investment advice.
