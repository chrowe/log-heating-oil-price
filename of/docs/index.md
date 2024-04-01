<style>

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 8rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 2rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: 34em;
  font-size: 20px;
  font-style: initial;
  font-weight: 500;
  line-height: 1.5;
  color: var(--theme-foreground-muted);
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 90px;
  }
}

</style>

<div class="hero">
  <h1>VSECU Oil Price</h1>
  <h2>This is a log of the price of Irving Oil from VSECU</h2>
  <a href="https://www.vsecu.com/personal/home-heating/fuel-buying-program" target="_blank">See details<span style="display: inline-block; margin-left: 0.25rem;">↗︎</span></a>
</div>

<div class="grid grid-cols-1" style="grid-auto-rows: 504px;">
  <div class="card">${
    resize((width) => Plot.plot({
      title: "Irving heating oil",
      subtitle: "price over time",
      width,
      y: {grid: true, label: "$"},
      marks: [
        Plot.ruleY([0]),
        Plot.lineY(oil, {x: "date", y: "price", tip: true})
      ]
    }))
  }</div>
  <div class="card">${
    resize((width) => Inputs.table(oil, {sort: "date", reverse: true})
    )
  }</div>
</div>

```js
const oil = FileAttachment("data/oil.csv").csv({typed: true});
```

---
