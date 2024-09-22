const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {

  console.info('Started.....')
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  // Go to web page
  await page.goto('https://www.akc.org/dog-breeds/', {
    waitUntil: 'domcontentloaded',
  });

  // Wait for the DOM to load
  await page.waitForSelector('.breed-type-card__title');
  console.info('Fetching.....')

  // Extract the content
  const dog_names = await page.$$eval('.breed-type-card__title', elements =>
    elements.map(element => element.textContent.trim())
  );

  console.info('Writing.....')

  // Write the data to a file
  fs.writeFile('dog_names.json', JSON.stringify(dog_names, null, 2), err => {
    if (err) throw err;
    console.log('Data written to file');
  });

  console.info('File created successfully.....')

  console.info(dog_names);

  // Close the browser
  await browser.close();
})();


