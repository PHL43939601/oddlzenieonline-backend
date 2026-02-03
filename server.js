// server.js - Backend API pre OddlzenieOnline.sk
// Node.js + Express + SendGrid

const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const sgMail = require('@sendgrid/mail');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Trust Railway proxy
app.set('trust proxy', 1);

// Middleware
app.use(express.json());
app.use(cors({
  origin: true, // Allow all origins for testing
  credentials: true
}));

// Rate limiting - max 3 žiadosti za 15 minút
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 3,
  message: { error: 'Príliš veľa žiadostí. Skúste znova o 15 minút.' }
});

// SendGrid setup
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

// Email konfigurácia
const RECIPIENT_EMAIL = process.env.RECIPIENT_EMAIL || 'propertyholdinglimited@gmail.com';
const FROM_EMAIL = 'OddlženieOnline.sk <info@oddlzenieonline.sk>';
const REPLY_TO_EMAIL = 'info@oddlzenieonline.sk';

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
    
    // 2. Generovanie PDF
    console.log('Generujem PDF dokumenty...');
    const pdfFiles = await generatePDFs(formData);
    
    // 3. Odoslanie emailu právnikovi
    await sendEmailToLawyer(formData, pdfFiles);
    
    // 4. Odoslanie potvrdenia klientovi
    await sendConfirmationToClient(formData);
    
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
  try {
    const msg = {
      to: RECIPIENT_EMAIL,
      from: FROM_EMAIL,
      replyTo: REPLY_TO_EMAIL,
      subject: `Nová žiadosť o osobný bankrot - ${formData.meno} ${formData.priezvisko}`,
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
      `,
      attachments: pdfFiles
    };

    await sgMail.send(msg);
    console.log('✅ Email odoslaný právnikovi');
  } catch (error) {
    console.error('Email error:', error);
    if (error.response) {
      console.error('SendGrid error body:', error.response.body);
    }
    throw error;
  }
}

// ============================================
// Odoslanie potvrdenia klientovi
// ============================================
async function sendConfirmationToClient(formData) {
  try {
    const msg = {
      to: formData.email,
      from: FROM_EMAIL,
      replyTo: REPLY_TO_EMAIL,
      subject: 'Žiadosť prijatá - OddlženieOnline.sk',
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

    await sgMail.send(msg);
    console.log('✅ Potvrdenie odoslané klientovi');
  } catch (error) {
    console.error('Email error:', error);
    if (error.response) {
      console.error('SendGrid error body:', error.response.body);
    }
    throw error;
  }
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
        
        const pdfFilePaths = [
          path.join(tempDir, `Zivotopis_${meno}_${priezvisko}.pdf`),
          path.join(tempDir, `Majetok_${meno}_${priezvisko}.pdf`),
          path.join(tempDir, `Majetok_Historia_${meno}_${priezvisko}.pdf`),
          path.join(tempDir, `Veritelia_${meno}_${priezvisko}.pdf`)
        ];
        
        // Konverzia súborov pre SendGrid attachments
        const attachments = [];
        for (const filePath of pdfFilePaths) {
          try {
            const content = await fs.readFile(filePath);
            const filename = path.basename(filePath);
            attachments.push({
              content: content.toString('base64'),
              filename: filename,
              type: 'application/pdf',
              disposition: 'attachment'
            });
          } catch (err) {
            console.error(`Chyba pri čítaní súboru ${filePath}:`, err);
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
  console.log(`📧 Emaily sa posielajú cez SendGrid API`);
  console.log(`📧 From: ${FROM_EMAIL}`);
  console.log(`📧 Recipient: ${RECIPIENT_EMAIL}`);
});
