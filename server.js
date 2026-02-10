// server.js - Backend API pre OddlzenieOnline.sk
// Node.js + Express + Nodemailer (Gmail) + Python PDF

const express = require('express');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Trust Railway proxy
app.set('trust proxy', 1);

// Middleware
app.use(express.json({ limit: '5mb' }));
app.use(cors({
  origin: true,
  credentials: true
}));

// ============================================
// PASSWORD PROTECTION (remove when ready to launch)
// ============================================
const SITE_PASSWORD = process.env.SITE_PASSWORD || '';
const COOKIE_NAME = 'oddlzenie_access';
const COOKIE_MAX_AGE = 7 * 24 * 60 * 60 * 1000; // 7 dní

// Password verification endpoint
app.post('/api/verify-password', express.urlencoded({ extended: false }), (req, res) => {
  const { password } = req.body;
  if (password === SITE_PASSWORD) {
    res.cookie(COOKIE_NAME, 'granted', {
      maxAge: COOKIE_MAX_AGE,
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production'
    });
    const redirect = req.query.redirect || '/';
    res.redirect(redirect);
  } else {
    res.send(getPasswordPage('Nesprávne heslo. Skúste znova.', req.originalUrl));
  }
});

function parseCookies(req) {
  const raw = req.headers.cookie || '';
  return Object.fromEntries(raw.split(';').map(c => c.trim().split('=')).filter(c => c.length === 2));
}

function getPasswordPage(error = '', action = '/api/verify-password') {
  return `<!DOCTYPE html>
<html lang="sk"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OddlženieOnline.sk</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial,sans-serif;background:#0d1b3e;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}
.box{background:#fff;border-radius:12px;padding:48px 40px;max-width:400px;width:100%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.logo{font-family:Georgia,serif;font-size:24px;margin-bottom:8px}
.logo b{color:#c5a255}.logo span{color:#0d1b3e}
.sub{color:#999;font-size:13px;margin-bottom:32px}
input[type=password]{width:100%;padding:14px 16px;border:2px solid #e5e7eb;border-radius:8px;font-size:16px;outline:none;transition:border .2s}
input[type=password]:focus{border-color:#c5a255}
button{width:100%;padding:14px;background:#c5a255;color:#0d1b3e;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer;margin-top:12px;transition:background .2s}
button:hover{background:#d4b76a}
.err{color:#dc2626;font-size:13px;margin-bottom:16px}
</style></head><body>
<div class="box">
  <div class="logo"><b>Oddlženie</b><span>Online.sk</span></div>
  <p class="sub">Stránka je v príprave. Prístup je chránený heslom.</p>
  ${error ? `<p class="err">${error}</p>` : ''}
  <form method="POST" action="${action}">
    <input type="password" name="password" placeholder="Zadajte heslo" autofocus required>
    <button type="submit">Vstúpiť</button>
  </form>
</div>
</body></html>`;
}

// Password gate middleware
function passwordGate(req, res, next) {
  // Skip if no password set (protection disabled)
  if (!SITE_PASSWORD) return next();
  // Skip API and health endpoints
  if (req.path.startsWith('/api/') || req.path === '/health') return next();
  // Check cookie
  const cookies = parseCookies(req);
  if (cookies[COOKIE_NAME] === 'granted') return next();
  // Show password page
  res.send(getPasswordPage('', `/api/verify-password?redirect=${encodeURIComponent(req.originalUrl)}`));
}

app.use(passwordGate);

// ============================================
// STATIC FILES + ROUTING
// ============================================

// /formular → formular.html (must be before static middleware)
app.get('/formular', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'formular.html'));
});

// Serve static files from /public (landing = index.html)
app.use(express.static(path.join(__dirname, 'public')));

// ============================================
// RATE LIMITING
// ============================================
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minút
  max: 10,
  message: { error: 'Príliš veľa žiadostí. Skúste znova o 15 minút.' }
});

// ============================================
// EMAIL CONFIGURATION (Gmail SMTP)
// ============================================
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_APP_PASSWORD
  }
});

const RECIPIENT_EMAIL = process.env.RECIPIENT_EMAIL || 'propertyholdinglimited@gmail.com';
const FROM_NAME = 'OddlženieOnline.sk';

// ============================================
// HLAVNÝ ENDPOINT - Odoslanie formulára
// ============================================
app.post('/api/submit-form', apiLimiter, async (req, res) => {
  try {
    const formData = req.body;

    // Validácia
    if (!formData.meno || !formData.priezvisko || !formData.email) {
      return res.status(400).json({
        error: 'Chýbajúce povinné údaje (meno, priezvisko, email)'
      });
    }

    console.log(`📝 Nová žiadosť: ${formData.meno} ${formData.priezvisko} (${formData.email})`);

    // 1. Generovanie PDF
    console.log('📄 Generujem PDF dokumenty...');
    const pdfFiles = await generatePDFs(formData);
    console.log(`✅ ${pdfFiles.length} PDF vygenerovaných`);

    // 2. Email adminovi s PDF prílohami
    await sendEmailToAdmin(formData, pdfFiles);

    // 3. Potvrdenie klientovi
    await sendConfirmationToClient(formData);

    res.json({
      success: true,
      message: 'Žiadosť úspešne odoslaná'
    });

  } catch (error) {
    console.error('❌ Chyba pri spracovaní:', error);
    res.status(500).json({
      error: 'Chyba pri spracovaní žiadosti. Skúste to znova.'
    });
  }
});

// ============================================
// PDF GENEROVANIE (Python ReportLab)
// ============================================
async function generatePDFs(formData) {
  const { exec } = require('child_process');
  const fs = require('fs').promises;

  return new Promise(async (resolve, reject) => {
    try {
      const tempDir = `/tmp/oddlzenie_${Date.now()}`;
      await fs.mkdir(tempDir, { recursive: true });

      const dataFile = path.join(tempDir, 'data.json');
      await fs.writeFile(dataFile, JSON.stringify(formData, null, 2));

      const pythonScript = path.join(__dirname, 'pdf_generator.py');
      const command = `python3 "${pythonScript}" "${dataFile}" "${tempDir}"`;

      exec(command, { cwd: tempDir, timeout: 30000 }, async (error, stdout, stderr) => {
        if (error) {
          console.error('PDF generation error:', error.message);
          if (stderr) console.error('stderr:', stderr);
          reject(new Error('PDF generovanie zlyhalo'));
          return;
        }

        console.log('PDF output:', stdout.trim());

        const meno = formData.meno || 'Dlznik';
        const priezvisko = formData.priezvisko || 'Neznamy';

        const pdfNames = [
          `Zivotopis_${meno}_${priezvisko}.pdf`,
          `Majetok_${meno}_${priezvisko}.pdf`,
          `Majetok_Historia_${meno}_${priezvisko}.pdf`,
          `Veritelia_${meno}_${priezvisko}.pdf`
        ];

        const attachments = [];
        for (const name of pdfNames) {
          const filePath = path.join(tempDir, name);
          try {
            const content = await fs.readFile(filePath);
            attachments.push({
              filename: name,
              content: content
            });
          } catch (err) {
            console.error(`⚠️ Súbor nenájdený: ${name}`);
          }
        }

        // Cleanup po 2 minútach
        setTimeout(async () => {
          try { await fs.rm(tempDir, { recursive: true, force: true }); } catch (e) {}
        }, 120000);

        resolve(attachments);
      });
    } catch (error) {
      reject(error);
    }
  });
}

// ============================================
// EMAIL ADMINOVI (s PDF prílohami)
// ============================================
async function sendEmailToAdmin(formData, pdfFiles) {
  const mailOptions = {
    from: `${FROM_NAME} <${process.env.GMAIL_USER}>`,
    to: RECIPIENT_EMAIL,
    subject: `Nová žiadosť o oddlženie — ${formData.meno} ${formData.priezvisko}`,
    html: `
      <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
        <div style="background:#0d1b3e;padding:20px 30px;border-radius:8px 8px 0 0;">
          <h2 style="color:#c5a255;margin:0;font-family:Georgia,serif;">Nová žiadosť o oddlženie</h2>
        </div>
        <div style="background:#fff;padding:24px 30px;border:1px solid #e5e7eb;">
          <table style="width:100%;border-collapse:collapse;">
            <tr>
              <td style="padding:8px;border-bottom:1px solid #f0f0f0;color:#666;width:35%;">Meno:</td>
              <td style="padding:8px;border-bottom:1px solid #f0f0f0;font-weight:bold;">${formData.meno} ${formData.priezvisko}</td>
            </tr>
            <tr>
              <td style="padding:8px;border-bottom:1px solid #f0f0f0;color:#666;">Email:</td>
              <td style="padding:8px;border-bottom:1px solid #f0f0f0;"><a href="mailto:${formData.email}">${formData.email}</a></td>
            </tr>
            <tr>
              <td style="padding:8px;border-bottom:1px solid #f0f0f0;color:#666;">Telefón:</td>
              <td style="padding:8px;border-bottom:1px solid #f0f0f0;">${formData.telefon || '—'}</td>
            </tr>
            <tr>
              <td style="padding:8px;border-bottom:1px solid #f0f0f0;color:#666;">Rodné číslo:</td>
              <td style="padding:8px;border-bottom:1px solid #f0f0f0;">${formData.rodneCislo || '—'}</td>
            </tr>
            <tr>
              <td style="padding:8px;color:#666;">Dátum:</td>
              <td style="padding:8px;">${new Date().toLocaleString('sk-SK')}</td>
            </tr>
          </table>
          <p style="margin-top:20px;color:#666;">V prílohe sú 4 PDF dokumenty na kontrolu.</p>
        </div>
        <div style="background:#f8f7f4;padding:16px 30px;border-radius:0 0 8px 8px;border:1px solid #e5e7eb;border-top:none;">
          <p style="margin:0;font-size:12px;color:#999;">OddlženieOnline.sk</p>
        </div>
      </div>
    `,
    attachments: pdfFiles
  };

  await transporter.sendMail(mailOptions);
  console.log('✅ Email odoslaný adminovi');
}

// ============================================
// POTVRDENIE KLIENTOVI
// ============================================
async function sendConfirmationToClient(formData) {
  const mailOptions = {
    from: `${FROM_NAME} <${process.env.GMAIL_USER}>`,
    to: formData.email,
    subject: 'Žiadosť prijatá — OddlženieOnline.sk',
    html: `
      <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
        <div style="background:#0d1b3e;padding:20px 30px;border-radius:8px 8px 0 0;text-align:center;">
          <span style="font-family:Georgia,serif;font-size:20px;font-weight:bold;color:#c5a255;">Oddlženie</span><span style="font-family:Georgia,serif;font-size:20px;color:#fff;">Online.sk</span>
        </div>
        <div style="background:#c5a255;height:3px;"></div>
        <div style="background:#fff;padding:32px 30px;border:1px solid #e5e7eb;">
          <div style="text-align:center;margin-bottom:24px;">
            <div style="background:#0d1b3e;width:56px;height:56px;border-radius:50%;display:inline-block;line-height:56px;">
              <span style="font-size:24px;color:#c5a255;">✓</span>
            </div>
          </div>
          <h2 style="text-align:center;color:#0d1b3e;font-family:Georgia,serif;margin:0 0 16px;">Žiadosť úspešne prijatá</h2>
          <p style="color:#4a4a4a;line-height:1.7;">Dobrý deň, <strong>${formData.meno}</strong>,</p>
          <p style="color:#4a4a4a;line-height:1.7;">ďakujeme za využitie služby OddlženieOnline.sk. Vašu žiadosť sme prijali a spracúvame ju.</p>

          <div style="background:#f8f7f4;border:1px solid #e8e4da;border-radius:8px;padding:20px;margin:20px 0;">
            <p style="margin:0 0 12px;font-weight:bold;color:#0d1b3e;">Čo bude nasledovať:</p>
            <p style="margin:4px 0;color:#4a4a4a;">1. Skontrolujeme vaše údaje</p>
            <p style="margin:4px 0;color:#4a4a4a;">2. Pripravíme vaše dokumenty</p>
            <p style="margin:4px 0;color:#4a4a4a;">3. Pošleme vám odkaz na stiahnutie a platbu</p>
          </div>

          <p style="color:#4a4a4a;line-height:1.7;">Ak máte otázky, napíšte nám na <a href="mailto:info@oddlzenieonline.sk" style="color:#2563eb;">info@oddlzenieonline.sk</a>.</p>
          <p style="color:#4a4a4a;">S pozdravom,<br><strong>Tím OddlženieOnline.sk</strong></p>
        </div>
        <div style="background:#0d1b3e;padding:20px 30px;border-radius:0 0 8px 8px;text-align:center;">
          <p style="margin:0;font-size:11px;color:rgba(255,255,255,.4);">© 2026 OddlženieOnline.sk</p>
        </div>
      </div>
    `
  };

  await transporter.sendMail(mailOptions);
  console.log('✅ Potvrdenie odoslané klientovi');
}

// ============================================
// HEALTH CHECK
// ============================================
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    env: process.env.NODE_ENV || 'development'
  });
});

// ============================================
// 404 - Fallback
// ============================================
app.use((req, res) => {
  res.status(404).sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ============================================
// START SERVER
// ============================================
app.listen(PORT, () => {
  console.log(`🚀 OddlženieOnline.sk beží na porte ${PORT}`);
  console.log(`📍 Landing:  http://localhost:${PORT}/`);
  console.log(`📍 Formulár: http://localhost:${PORT}/formular`);
  console.log(`📍 API:      http://localhost:${PORT}/api/submit-form`);
  console.log(`📍 Health:   http://localhost:${PORT}/health`);
  console.log(`📧 Email:    ${process.env.GMAIL_USER || 'NOT SET'}`);
});
