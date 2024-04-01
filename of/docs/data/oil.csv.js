import {csvParse, csvFormat} from "d3-dsv";
import {utcParse} from "d3-time-format";

async function text(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`fetch failed: ${response.status}`);
  return response.text();
}


// Load and parse.
const oilPrices = csvParse(await text("https://raw.githubusercontent.com/chrowe/log-heating-oil-price/main/irving_oil_prices.csv"));

// Write out csv formatted data.
process.stdout.write(csvFormat(oilPrices));
