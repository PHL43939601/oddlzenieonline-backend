# 🚂 RAILWAY DEPLOYMENT - Kompletný návod

## 🎯 Railway.app - Backend Hosting za $5/mesiac

Railway je najjednoduchší spôsob ako nasadiť Node.js backend do cloudu.

---

## 📋 PRÍPRAVA (5 minút)

### **1. Registrácia na Railway**

```
1. Choďte na: https://railway.app/
2. Kliknite "Login" vpravo hore
3. Vyberte "Login with GitHub"
4. Autorizujte Railway prístup k GitHub
5. Hotovo! ✅
```

### **2. Vytvorte GitHub repozitár (voliteľné)**

**Ak chcete:**
```
1. Choďte na: https://github.com/new
2. Repository name: oddlzenieonline-backend
3. Private repository
4. Kliknite "Create repository"
5. Nahrajte súbory z /outputs/
```

**ALEBO použite Railway bez GitHu:**
```
→ Railway podporuje deploy z lokálnych súborov
→ Použijeme Railway CLI
```

---

## 🚀 DEPLOYMENT - METÓDA 1: Railway CLI (najrýchlejšie)

### **Krok 1: Inštalácia Railway CLI**

**Linux/Mac:**
```bash
npm install -g @railway/cli
```

**Windows:**
```bash
npm install -g @railway/cli
```

### **Krok 2: Login**

```bash
railway login
```

→ Otvorí sa browser, prihláste sa

### **Krok 3: Inicializácia projektu**

```bash
cd /cesta/k/backend/suborom
railway init
```

→ Vyberte "Create new project"
→ Názov: "oddlzenieonline-backend"

### **Krok 4: Deploy**

```bash
railway up
```

→ Nahrá všetky súbory
→ Automaticky detekuje Node.js
→ Spustí `npm install && npm start`

### **Krok 5: Nastavenie environment variables**

```bash
railway variables set GMAIL_USER=propertyholdinglimited@gmail.com
railway variables set GMAIL_APP_PASSWORD="tevd cpuu dccb nwbp"
railway variables set RECIPIENT_EMAIL=propertyholdinglimited@gmail.com
railway variables set NODE_ENV=production
```

### **Krok 6: Získanie URL**

```bash
railway domain
```

→ Vygeneruje URL: `https://oddlzenieonline-backend-production.up.railway.app`

---

## 🚀 DEPLOYMENT - METÓDA 2: Railway Dashboard (GUI)

### **Krok 1: Vytvorenie projektu**

```
1. Prihláste sa na: https://railway.app/
2. Kliknite "New Project"
3. Vyberte "Deploy from GitHub repo"
   ALEBO
   "Empty Project" (ak nemáte GitHub)
```

### **Krok 2: Nastavenie služby**

```
1. Kliknite "New"
2. Vyberte "GitHub Repo" alebo "Empty Service"
3. Názov: oddlzenieonline-backend
```

### **Krok 3: Nahranie kódu**

**Ak máte GitHub:**
```
→ Vyberte váš repozitár
→ Railway automaticky detekuje Node.js
→ Spustí build
```

**Ak nemáte GitHub:**
```
1. Otvorte Terminal/CMD
2. Spustite: railway login
3. Spustite: railway up
```

### **Krok 4: Environment Variables**

```
1. V Railway dashboard → váš projekt
2. Kliknite na službu
3. Záložka "Variables"
4. Kliknite "Add Variable"

Pridajte:
GMAIL_USER = propertyholdinglimited@gmail.com
GMAIL_APP_PASSWORD = tevd cpuu dccb nwbp
RECIPIENT_EMAIL = propertyholdinglimited@gmail.com
NODE_ENV = production
```

### **Krok 5: Custom doména**

```
1. V službe → záložka "Settings"
2. Sekcia "Domains"
3. Kliknite "Generate Domain"
4. Skopírujte URL (napr. xxx.up.railway.app)

ALEBO pridajte vlastnú doménu:
5. Kliknite "Custom Domain"
6. Zadajte: api.oddlzenieonline.sk
7. Railway vám ukáže CNAME záznam
8. Pridajte ho do Websupport DNS
```

---

## 🔧 POTREBNÉ SÚBORY PRE RAILWAY

Railway automaticky detekuje Node.js projekt ak má:

### **1. package.json** ✅ (už máte)

```json
{
  "name": "oddlzenieonline-backend",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### **2. .railwayignore** (vytvorte)

```
node_modules/
.env
.env.local
*.log
.DS_Store
.git/
```

### **3. Procfile** (voliteľné)

```
web: node server.js
```

---

## 📊 OVERENIE DEPLOYMENTU

### **Test 1: Health Check**

```bash
curl https://your-app.up.railway.app/health
```

**Očakávaný výsledok:**
```json
{
  "status": "OK",
  "timestamp": "2026-01-28T..."
}
```

### **Test 2: API Endpoint**

```bash
curl -X POST https://your-app.up.railway.app/api/submit-form \
  -H "Content-Type: application/json" \
  -d '{
    "meno": "Test",
    "priezvisko": "User",
    "email": "test@email.sk"
  }'
```

**Ak vidíte:** `{"success": true}` → **FUNGUJE! ✅**

---

## 💰 NÁKLADY

```
Railway FREE tier:
✅ $5 kredit/mesiac ZADARMO
✅ 500 hodín runtime
✅ Postačuje pre vývoj

Railway PRO tier (odporúčané):
💵 $5/mesiac
✅ Unlimited runtime
✅ Viac resources
✅ Custom domains
✅ Prioritná podpora
```

**Pre produkciu: Railway PRO ($5/mes)**

---

## 🔒 BEZPEČNOSŤ

### **Environment Variables**

```
⚠️ NIKDY nedávajte .env súbor do GitHub!
⚠️ Používajte Railway Variables (šifrované)
```

### **.gitignore** (vytvorte)

```
node_modules/
.env
.env.local
.env.production
*.log
.DS_Store
```

---

## 📱 MONITORING

### **Railway Dashboard**

```
→ Real-time logs
→ CPU/RAM usage
→ Deploy history
→ Metrics & analytics
```

### **Prístup k logom:**

```bash
railway logs
```

alebo v Railway dashboard → Deployments → Logs

---

## 🆘 TROUBLESHOOTING

### **Chyba: "Python not found"**

```
Railway musí mať Python pre PDF generátor.

Riešenie:
1. Vytvorte nixpacks.toml:

[phases.setup]
aptPkgs = ["python3", "python3-pip"]

[phases.install]
cmds = ["pip3 install reportlab"]
```

### **Chyba: "Module not found"**

```bash
# Uistite sa že package.json obsahuje všetky závislosti
railway run npm install
```

### **Chyba: "Port already in use"**

```javascript
// server.js - Railway automaticky nastaví PORT
const PORT = process.env.PORT || 3000;
```

---

## ✅ POST-DEPLOYMENT CHECKLIST

- [ ] Backend beží na Railway URL
- [ ] Health check endpoint funguje
- [ ] Environment variables nastavené
- [ ] Email sa odosiela (test)
- [ ] PDF sa generujú (test)
- [ ] Custom doména pripojená (voliteľné)
- [ ] Logs sú čitateľné
- [ ] Monitoring nastavený

---

## 🎯 ĎALŠIE KROKY

**Po úspešnom deploym ente:**

1. ✅ Zapíšte si Railway URL
2. ✅ Otestujte API endpoint
3. ✅ Updatnite frontend (API URL)
4. ✅ Nastavte custom doménu (api.oddlzenieonline.sk)
5. ✅ End-to-end test celého systému

---

## 📞 KONTAKTY

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app/
- Status: https://status.railway.app/

**Váš projekt:**
- Dashboard: https://railway.app/project/[your-id]
- API URL: https://[your-app].up.railway.app

---

**HOTOVÉ! Backend je v cloude! 🚀**
