# Methodology

## Question

How does modeled net alpha change as AUM increases while the strategy's
percentage turnover and the market's available liquidity remain fixed?

## Calculation

1. Weekly trade dollars equal AUM multiplied by the trade fraction.
2. Participation equals weekly trade dollars divided by effective daily dollar volume.
3. Impact cost per traded dollar equals the impact coefficient multiplied by daily volatility and the square root of participation.
4. Annual fixed and impact costs equal the relevant per-dollar cost multiplied by annual one-way turnover.
5. Net alpha equals gross alpha minus modeled annual trading costs.
6. Economic break-even capacity solves for AUM where net alpha equals zero.
7. Operational capacity applies a separate 10% participation policy.

## Interpretation

The model holds signal quality and liquidity constant so that the scale effect
is visible. A live capacity study should allow alpha, volatility, spreads,
available volume and execution speed to change with market conditions.

The square-root equation is an empirical approximation rather than a universal
law. The coefficient in this example is assumed, not fitted. Results have no
probability interpretation and do not represent investment advice.
