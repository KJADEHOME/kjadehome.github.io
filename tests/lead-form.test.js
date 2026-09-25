const assert = require('node:assert/strict');
const fs = require('node:fs');
const test = require('node:test');

const inquiry = fs.readFileSync('inquiry.html', 'utf8');

test('KJadeHome inquiry form delivers to bonnie@kjadehome.com, not third parties', () => {
  assert.doesNotMatch(inquiry, /<form[^>]+action=["']mailto:/i);
  assert.match(inquiry, /formsubmit\.co\/bonnie@kjadehome\.com/);
  assert.match(inquiry, /formsubmit\.co\/ajax\/bonnie@kjadehome\.com/);
  assert.doesNotMatch(inquiry, /entrol/i);
  assert.doesNotMatch(inquiry, /wangyan/i);
  assert.doesNotMatch(inquiry, /supabase\.co/i);
});

test('homepage quote form also targets bonnie@kjadehome.com', () => {
  const home = fs.readFileSync('index.html', 'utf8');
  assert.match(home, /formsubmit\.co\/bonnie@kjadehome\.com/);
  assert.doesNotMatch(home, /entrol|wangyan/i);
});

test('about page structured data shows the company email', () => {
  const about = fs.readFileSync('about.html', 'utf8');
  assert.match(about, /bonnie@kjadehome\.com/);
  assert.doesNotMatch(about, /entrol|wangyan/i);
});

test('lead payload includes durable identity, attribution and buyer requirements', () => {
  assert.match(inquiry, /request_id: crypto\.randomUUID\(\)/);
  assert.match(inquiry, /product_interest: products\.join/);
  assert.match(inquiry, /target_market: String\(data\.get\('country'\)/);
  assert.match(inquiry, /source_page: window\.location\.href/);
  assert.match(inquiry, /utm_source: params\.get\('utm_source'\)/);
});

test('real company website is not confused with the anti-spam honeypot', () => {
  assert.match(inquiry, /name="company_website"/);
  assert.match(inquiry, /name="website" tabindex="-1"/);
  assert.match(inquiry, /website: String\(data\.get\('website'\)/);
});

test('homepage quote parameters prefill the detailed inquiry form', () => {
  assert.match(inquiry, /initialParams\.get\(name\)/);
  assert.match(inquiry, /initialParams\.get\('message'\)/);
  assert.match(inquiry, /roleByHomepageType/);
});
