# Week 15 rendered carousel copy

## 1. Strategy Capacity

Strategy
Capacity

Why alpha shrinks
as AUM grows

A scalable signal can still face
a limited implementation capacity.

## 2. What strategy capacity measures

What strategy capacity measures

Capacity depends on both portfolio economics and the ability to execute the required trades.

ECONOMIC CAPACITY

AUM where modeled
net alpha reaches zero

OPERATIONAL CAPACITY

AUM allowed by trading
and participation limits

The usable limit is the lower of the two.

A strategy can retain positive expected alpha and still breach its execution policy.

## 3. Scenario assumptions

Scenario assumptions

The example isolates scale while holding the signal and market environment fixed.

4.0%

gross annual alpha

10.0%

annual portfolio volatility

Weekly

rebalance frequency

20%

AUM traded per rebalance

5 bps

fixed cost per dollar traded

$500m

effective daily dollar volume

2.0%

daily market volatility

0.50

impact coefficient

All eight values are assumptions, not estimates for a live strategy.

## 4. Cost model

Cost model

Trade size rises with AUM. The impact proxy rises with the square root of market participation.

Impact cost

= 0.50 × 2.0% × √(trade / ADV)

Annual turnover

52 × 20% = 10.4x

Annual fixed cost

10.4 × 5 bps = 0.52%

Annual net alpha = 4.0% minus fixed cost minus annualized impact cost

The coefficient is assumed. A live study should estimate it from execution data.

## 5. Net alpha falls as AUM rises

Net alpha falls as AUM rises

The same percentage turnover creates larger trades and higher modeled market impact.

Economic break-even: about $280m

10% participation policy: $250m

Modeled net alpha: 2.82%, 2.44%, 2.01%, 1.40%, 0.19%, and -1.17%.

## 6. Selected trade economics

Selected trade economics

Fixed costs stay proportional to turnover. Impact costs rise as participation increases.

AUM / Weekly trade / Participation / Annual costs / Net alpha
$10m / $2m / 0.4% / 1.18% / 2.82%
$100m / $20m / 4.0% / 2.60% / 1.40%
$250m / $50m / 10.0% / 3.81% / 0.19%
$500m / $100m / 20.0% / 5.17% / -1.17%

At $250m, the strategy still has positive modeled alpha but reaches the participation limit.

## 7. Capacity is a range, not one number

Capacity is a range, not one number

Changing one assumption can move the economic break-even AUM materially.

The model does not produce a confidence interval. These are alternative scenarios.

Break-even AUM by scenario: $124m, $142m, $168m, $280m, and $464m.

## 8. Evidence and model limits

Evidence and model limits

Research supports the mechanism. The coefficient and scenario inputs still require calibration.

EMPIRICAL SUPPORT

Live institutional trades
show that costs and capacity
vary by strategy.

Market impact is concave.
A square-root form is a
common approximation.

Turnover and implementation rules
can change break-even capacity.

LIMITS OF THIS SCENARIO

The impact coefficient is assumed.
It does not come from executions.

Alpha and market volume stay fixed
as AUM changes.

Execution duration, crowding and
unfilled orders remain outside
the model.

Some data support richer impact surfaces than the square-root approximation.

## 9. Capacity review checklist

Capacity review checklist

A capacity estimate should update when the strategy or market environment changes.

01

Estimate gross alpha at the proposed AUM

02

Translate turnover into trade dollars by asset

03

Measure spread and arrival-price shortfall

04

Stress volume, volatility and execution time

05

Apply participation limits before deployment

How much alpha remains after the trades needed to implement the strategy?
