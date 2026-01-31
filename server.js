// server.js - Backend API pre OddlzenieOnline.sk
// Node.js + Express + SendGrid

const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(cors({
  origin: ['https://oddlzenieonline.sk', 'https://www.oddlzenieonline.sk']
}));

// Rate limiting - max 3 žiadosti za 15 minút
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 3,
  message: { error: 'Príliš veľa žiadostí. Skúste znova o 15 minút.' }
});

// Gmail SMTP setup s Nodemailer
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_APP_PASSWORD
  }
});

// Email konfigurácia
const RECIPIENT_EMAIL = 'propertyholdinglimited@gmail.com';
const FROM_EMAIL = process.env.GMAIL_USER;

// ============================================
// HLAVNÝ ENDPOINT - Odoslanie formulára
// ============================================
app.post('/api/submit-form', apiLimiter, async (req, res) => {
  try {
    const formData = req.body;
    
    // 1. Validácia
    if (!formData.meno || !formData.priezvisko || !formData.email) {
      return res.status(400).json({ 
        error: 'Chýbajúce povinné údaje' 
      });
    }
    
    // 2. TODO: Generovanie PDF (zatiaľ placeholder)
    console.log('Generujem PDF dokumenty...');
    const pdfFiles = await generatePDFs(formData);
    
    // 3. Odoslanie emailu právnikovi
    await sendEmailToLawyer(formData, pdfFiles);
    
    // 4. Odoslanie potvrdenia klientovi
    await sendConfirmationToClient(formData);
    
    // 5. TODO: Uloženie do databázy
    console.log('Ukladám do databázy...');
    
    res.json({ 
      success: true, 
      message: 'Žiadosť úspešne odoslaná' 
    });
    
  } catch (error) {
    console.error('Chyba:', error);
    res.status(500).json({ 
      error: 'Chyba pri spracovaní žiadosti' 
    });
  }
});

// ============================================
// Odoslanie emailu právnikovi
// ============================================
async function sendEmailToLawyer(formData, pdfFiles) {
  const mailOptions = {
    from: FROM_EMAIL,
    to: RECIPIENT_EMAIL,
    subject: `Nová žiadosť o osobný bankrot - ${formData.meno} ${formData.priezvisko}`,
    text: `
Dobrý deň,

Do systému OddlženieOnline.sk bola podaná nová žiadosť.

KLIENT:
- Meno: ${formData.meno} ${formData.priezvisko}
- Email: ${formData.email}
- Telefón: ${formData.telefon}
- Rodné číslo: ${formData.rodneCislo}
- Adresa: ${formData.ulica} ${formData.cislo}, ${formData.obec}

V prílohe sú vyplnené PDF dokumenty.

ĎALŠÍ POSTUP:
1. Skontrolujte dokumenty (15-30 minút)
2. Kontaktujte klienta na: ${formData.email}
3. Dohodnite platbu 349 EUR
4. Po platbe odovzdajte dokumenty

S pozdravom,
OddlženieOnline.sk systém
    `,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Nová žiadosť o osobný bankrot</h2>
        
        <h3>Informácie o klientovi:</h3>
        <table style="border-collapse: collapse; width: 100%;">
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f8fafc;"><b>Meno:</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">${formData.meno} ${formData.priezvisko}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f8fafc;"><b>Email:</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">${formData.email}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f8fafc;"><b>Telefón:</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">${formData.telefon}</td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd; background: #f8fafc;"><b>Rodné číslo:</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">${formData.rodneCislo}</td>
          </tr>
        </table>
        
        <p style="margin-top: 20px;">V prílohe sú vyplnené PDF dokumenty na kontrolu.</p>
        
        <h3>Ďalší postup:</h3>
        <ol>
          <li>Skontrolujte dokumenty (15-30 minút)</li>
          <li>Kontaktujte klienta na <a href="mailto:${formData.email}">${formData.email}</a></li>
          <li>Dohodnite platbu 349 EUR</li>
          <li>Po platbe odovzdajte dokumenty</li>
        </ol>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #e2e8f0;">
        <p style="font-size: 12px; color: #64748b;">
          OddlženieOnline.sk | Property Holding Limited, s.r.o.<br>
          Mostná 72, 949 01 Nitra, SK
        </p>
      </div>
    `
    attachments: pdfFiles
  };
  
  await transporter.sendMail(mailOptions);
  console.log('✅ Email odoslaný právnikovi');
}

// ============================================
// Odoslanie potvrdenia klientovi
// ============================================
async function sendConfirmationToClient(formData) {
  const mailOptions = {
    from: FROM_EMAIL,
    to: formData.email,
    subject: 'Žiadosť prijatá - OddlženieOnline.sk',
    text: `
Dobrý deň ${formData.meno},

Vaša žiadosť o osobný bankrot bola úspešne prijatá!

ČO ĎALEJ:
1. Právnik skontroluje vaše dokumenty (24-48 hodín)
2. Ozveme sa vám s informáciami o ďalšom postupe
3. Po kontrole a úhrade 349 EUR dostanete hotové dokumenty

Ak máte akékoľvek otázky, neváhajte nás kontaktovať.

S pozdravom,
Tím OddlženieOnline.sk
    `,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Žiadosť úspešne prijatá</h2>
        
        <p>Dobrý deň ${formData.meno},</p>
        
        <p>Vaša žiadosť o osobný bankrot bola úspešne prijatá!</p>
        
        <div style="background: #dcfce7; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="margin-top: 0;">Čo ďalej:</h3>
          <ol style="margin-bottom: 0;">
            <li style="margin-bottom: 10px;"><b>Právnik skontroluje vaše dokumenty</b> (24-48 hodín)</li>
            <li style="margin-bottom: 10px;"><b>Ozveme sa vám</b> s informáciami o ďalšom postupe</li>
            <li><b>Po kontrole a úhrade 349 EUR</b> dostanete hotové dokumenty</li>
          </ol>
        </div>
        
        <p>Ak máte akékoľvek otázky, neváhajte nás kontaktovať.</p>
        
        <p>S pozdravom,<br><b>Tím OddlženieOnline.sk</b></p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #e2e8f0;">
        <p style="font-size: 12px; color: #64748b;">
          OddlženieOnline.sk | Property Holding Limited, s.r.o.<br>
          Mostná 72, 949 01 Nitra, SK
        </p>
      </div>
    `
  };
  
  await transporter.sendMail(mailOptions);
  console.log('✅ Potvrdenie odoslané klientovi');
}

// ============================================
// Generovanie PDF (Python ReportLab)
// ============================================
async function generatePDFs(formData) {
  const { exec } = require('child_process');
  const fs = require('fs').promises;
  const path = require('path');
  
  return new Promise(async (resolve, reject) => {
    try {
      // Vytvorenie dočasného priečinka
      const tempDir = `/tmp/oddlzenie_${Date.now()}`;
      await fs.mkdir(tempDir, { recursive: true });
      
      // Uloženie dát do JSON súboru
      const dataFile = path.join(tempDir, 'data.json');
      await fs.writeFile(dataFile, JSON.stringify(formData, null, 2));
      
      // Spustenie Python PDF generátora
      const pythonScript = path.join(__dirname, 'pdf_generator.py');
      const command = `python3 ${pythonScript} ${dataFile} ${tempDir}`;
      
      exec(command, { cwd: tempDir }, async (error, stdout, stderr) => {
        if (error) {
          console.error('PDF generation error:', error);
          reject(error);
          return;
        }
        
        console.log('PDF generation output:', stdout);
        
        // Načítanie vygenerovaných PDF súborov
        const meno = formData.meno || 'Dlznik';
        const priezvisko = formData.priezvisko || 'Neznamy';
        
        const pdfFiles = [
          {
            filename: `Zivotopis_${meno}_${priezvisko}.pdf`,
            path: path.join(tempDir, `Zivotopis_${meno}_${priezvisko}.pdf`)
          },
          {
            filename: `Majetok_${meno}_${priezvisko}.pdf`,
            path: path.join(tempDir, `Majetok_${meno}_${priezvisko}.pdf`)
          },
          {
            filename: `Majetok_Historia_${meno}_${priezvisko}.pdf`,
            path: path.join(tempDir, `Majetok_Historia_${meno}_${priezvisko}.pdf`)
          },
          {
            filename: `Veritelia_${meno}_${priezvisko}.pdf`,
            path: path.join(tempDir, `Veritelia_${meno}_${priezvisko}.pdf`)
          }
        ];
        
        // Konverzia súborov na base64 pre email prílohy
        const attachments = [];
        for (const file of pdfFiles) {
          try {
            const content = await fs.readFile(file.path);
            attachments.push({
              filename: file.filename,
              content: content,
              contentType: 'application/pdf'
            });
          } catch (err) {
            console.error(`Chyba pri čítaní súboru ${file.filename}:`, err);
          }
        }
        
        // Vyčistenie dočasných súborov
        setTimeout(async () => {
          try {
            await fs.rm(tempDir, { recursive: true, force: true });
          } catch (err) {
            console.error('Chyba pri čistení temp súborov:', err);
          }
        }, 60000); // Vyčistí po 1 minúte
        
        resolve(attachments);
      });
    } catch (error) {
      console.error('PDF generation setup error:', error);
      reject(error);
    }
  });
}

// ============================================
// Health check endpoint
// ============================================
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// ============================================
// Start server
// ============================================
app.listen(PORT, () => {
  console.log(`🚀 Backend API beží na porte ${PORT}`);
  console.log(`📧 Emaily sa posielajú na: ${RECIPIENT_EMAIL}`);
});
