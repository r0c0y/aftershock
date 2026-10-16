---
id: doc-14
title: Eng design: channel fee config
state: current
date: 2026-08-14
author: Leo Novak
kind: design
---
Design doc, Leo Novak, 14 Aug 2026. Billing service reads channel_fee_pct from config per channel.
meridian.channel_fee_pct = 14 (9 commission + 5 handling), set per Pricing Handbook.
Corvane fulfilment fee is configured separately at 6. Changes require a config release.
