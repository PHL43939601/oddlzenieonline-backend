// test-email.js
// Jednoduchý test script na overenie Gmail SMTP

require('dotenv').config();
const nodemailer = require('nodemailer');

console.log('🧪 Testujem Gmail SMTP...\n');

// Kontrola environment variables
if (!process.env.GMAIL_USER || !process.env.GMAIL_APP_PASSWORD) {
  console.error('❌ CHYBA: .env súbor nie je správne nastavený!');
  console.log('\nSkontrolujte že máte v .env súbore:');
  console.log('GMAIL_USER=propertyholdinglimited@gmail.com');
  console.log('GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx\n');
  process.exit(1);
}

console.log('✓ Environment variables načítané');
console.log(`✓ Gmail účet: ${process.env.GMAIL_USER}\n`);

// Vytvorenie transportera
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_APP_PASSWORD
  }
});

console.log('✓ Transporter vytvorený');
console.log('📧 Odosielam testovací email...\n');

// Email options
const mailOptions = {
  from: process.env.GMAIL_USER,
  to: process.env.GMAIL_USER, // Odosielame sami sebe
  subject: '✅ Test email z OddlženieOnline.sk',
  text: `
Gratulujeme!

Ak vidíte tento email, Gmail SMTP je správne nakonfigurované a funguje!

Teraz môžete:
1. Spustiť backend server (npm run dev)
2. Odosielať emaily z aplikácie
3. Pokračovať s vývojom

Detaily:
- Odosielateľ: ${process.env.GMAIL_USER}
- Dátum: ${new Date().toLocaleString('sk-SK')}
- Backend: OddlženieOnline.sk

S pozdravom,
Test Script
  `,
  html: `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #2563eb;">✅ Gmail SMTP Test Úspešný!</h2>
      
      <p>Gratulujeme!</p>
      
      <p>Ak vidíte tento email, Gmail SMTP je správne nakonfigurované a funguje!</p>
      
      <div style="background: #dcfce7; padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h3 style="margin-top: 0;">Teraz môžete:</h3>
        <ol>
          <li>Spustiť backend server (<code>npm run dev</code>)</li>
          <li>Odosielať emaily z aplikácie</li>
          <li>Pokračovať s vývojom</li>
        </ol>
      </div>
      
      <h3>Detaily:</h3>
      <ul style="list-style: none; padding: 0;">
        <li>📧 Odosielateľ: <code>${process.env.GMAIL_USER}</code></li>
        <li>📅 Dátum: ${new Date().toLocaleString('sk-SK')}</li>
        <li>🚀 Backend: OddlženieOnline.sk</li>
      </ul>
      
      <hr style="margin: 30px 0; border: none; border-top: 1px solid #e2e8f0;">
      <p style="font-size: 12px; color: #64748b;">
        Tento email bol odoslaný test scriptom.<br>
        OddlženieOnline.sk | Property Holding Limited, s.r.o.
      </p>
    </div>
  `
};

// Odoslanie emailu
transporter.sendMail(mailOptions, (error, info) => {
  if (error) {
    console.log('❌ CHYBA pri odosielaní emailu:');
    console.log(error.message);
    console.log('\nNajčastejšie problémy:');
    console.log('1. App Password nie je správne nastavené');
    console.log('2. 2-Step Verification nie je zapnuté');
    console.log('3. App Password má preklepy');
    console.log('\nPozrite GMAIL-SETUP-NAVOD.md pre pomoc.\n');
    process.exit(1);
  } else {
    console.log('✅ EMAIL ÚSPEŠNE ODOSLANÝ!');
    console.log(`\nResponse: ${info.response}`);
    console.log(`Message ID: ${info.messageId}\n`);
    console.log('🎉 Gmail SMTP funguje perfektne!');
    console.log('📬 Skontrolujte si inbox na: ' + process.env.GMAIL_USER);
    console.log('\n✅ Môžete pokračovať s vývojom!\n');
  }
});
