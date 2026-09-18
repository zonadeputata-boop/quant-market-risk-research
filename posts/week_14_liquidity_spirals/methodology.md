# Methodology

## Question

How can a price shock create additional forced selling when a leveraged investor must restore a maximum leverage ratio?

## Balance-sheet setup

The stylized investor starts with $250 of risky assets, $150 of debt and $100 of equity. Assets-to-equity leverage therefore equals 2.5x. An exogenous 4% asset-price decline reduces assets to $240 and equity to $90 while debt stays at $150. Leverage rises to 2.67x.

If sale proceeds repay debt, a sale executed at the current price reduces assets and debt by the same amount. Equity does not change at execution. The sale required to restore a maximum leverage ratio L is:

`sale = max(0, assets - L * equity)`

For the first round, the required sale is $15.

## Feedback assumption

After each sale, the model applies a stylized price-impact return to the remaining assets:

`impact return = -impact sensitivity * sale / pre-sale assets`

The model then recalculates equity and leverage and repeats the sale until leverage returns to the 2.5x limit. The three sensitivities are 0.0, 0.2 and 0.4. These values create controlled comparisons. They are not estimates from market data.

## Interpretation

The scenario demonstrates a mechanism. A first loss breaches the leverage limit. A sale restores the limit at the current price. Price impact then reduces the value of the remaining assets and creates another breach. Stronger feedback requires larger cumulative sales and produces a larger equity loss.

The results do not estimate the probability of a liquidity spiral or the causal price impact of actual trades. The single-asset balance sheet omits order-book dynamics, cross-asset liquidation, changing haircuts, fresh capital, strategic buyers and price recovery.

## Empirical case study

The Bank of England's December 2022 Financial Stability Report describes a real feedback episode in the UK gilt market. It reports margin and collateral calls above £70 billion for LDI funds and pension schemes. Between 23 September and 14 October 2022, it reports around £23 billion of net gilt sales by LDI funds and around £14 billion by DB pension schemes.

Those figures support the relevance of the mechanism. They do not calibrate the model's impact sensitivities.

## Sources

- Brunnermeier, M. K. and Pedersen, L. H. (2009), *Market Liquidity and Funding Liquidity*, Review of Financial Studies 22(6), 2201-2238. https://academic.oup.com/rfs/article/22/6/2201/1592184
- Bank of England (2022), *Financial Stability Report, December 2022*, Section 5. https://www.bankofengland.co.uk/financial-stability-report/2022/december-2022
- Financial Stability Board (2024), *Liquidity Preparedness for Margin and Collateral Calls*. https://www.fsb.org/2024/12/liquidity-preparedness-for-margin-and-collateral-calls-final-report/
- Bank for International Settlements (2026), *Liquidity preparedness for margin and collateral calls*. https://www.bis.org/publications/fsi-summary-liquidity-preparedness-margin-and-collateral-calls-executive-summary

