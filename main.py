<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WaDih — Analyse de CGU en Darija</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>

<!-- NAVBAR -->
<nav>
  <a class="logo" href="#" onclick="showPage('upload')">
    <div class="logo-mark">W</div>
    WaDih
    <span class="loi-badge">Loi 09-08</span>
  </a>
  <div class="nav-right">
    <a class="nav-link" onclick="showPage('upload')">Analyser</a>
    <a class="nav-link" href="https://github.com" target="_blank">GitHub</a>
    <button class="btn btn-primary" onclick="runDemo()">Démo rapide</button>
  </div>
</nav>

<!-- PAGE : UPLOAD -->
<div class="page active" id="page-upload">
  <div class="upload-page">
    <div class="hero-tag">🛡️ Protection vie privée · Conformité Loi 09-08</div>
    <h1 class="hero-title">Comprends ce que<br>tu signes, en Darija</h1>
    <p class="hero-sub">
      WaDih analyse tes contrats numériques et CGU en français ou arabe,
      détecte les clauses risquées, et t'explique tout simplement.
    </p>

    <div class="input-tabs">
      <button class="itab active" onclick="switchInputTab('file', this)">📄 PDF / Image</button>
      <button class="itab"        onclick="switchInputTab('text', this)">📝 Texte</button>
      <button class="itab"        onclick="switchInputTab('url',  this)">🔗 URL</button>
    </div>

    <div class="input-panel active" id="panel-file">
      <div class="dropzone" id="dropzone"
        ondragover="event.preventDefault(); this.classList.add('dragging')"
        ondragleave="this.classList.remove('dragging')"
        ondrop="handleDrop(event)">
        <input type="file" accept=".pdf,.png,.jpg,.jpeg,.webp" onchange="handleFileSelect(event)" />
        <div class="dz-icon">📂</div>
        <div class="dz-title">Glisse ton fichier ici</div>
        <p class="dz-sub">ou clique pour parcourir</p>
        <div class="type-pills">
          <span class="type-pill">PDF</span>
          <span class="type-pill">PNG</span>
          <span class="type-pill">JPG</span>
          <span class="type-pill">WEBP</span>
        </div>
      </div>
    </div>

    <div class="input-panel" id="panel-text">
      <div class="text-panel">
        <textarea id="text-input" placeholder="Colle ici le texte de ton contrat ou CGU..." oninput="updateCharCount()"></textarea>
        <div class="text-panel-footer">
          <span class="char-count" id="char-count">0 caractères</span>
          <button class="btn btn-primary" onclick="startAnalysis()">Analyser →</button>
        </div>
      </div>
    </div>

    <div class="input-panel" id="panel-url">
      <div class="url-panel">
        <div class="url-input-group">
          <input type="text" id="url-input" placeholder="https://exemple.com/cgu" />
          <button class="btn btn-primary" onclick="startAnalysis()">Analyser →</button>
        </div>
        <div>
          <div style="font-size:12px; color:var(--muted); margin-bottom:8px;">Exemples :</div>
          <div class="url-examples">
            <div class="url-ex" onclick="fillUrl('https://www.cih.co.ma/cgu')">CIH Bank CGU</div>
            <div class="url-ex" onclick="fillUrl('https://www.attijaribank.co.ma/legal')">Attijariwafa Bank</div>
            <div class="url-ex" onclick="fillUrl('https://play.google.com/store/apps')">App Google Play</div>
          </div>
        </div>
      </div>
    </div>

    <div class="demo-strip">
      <div class="demo-left">
        <div class="demo-icon">🏦</div>
        <div class="demo-text">
          Voir un exemple de résultat
          <small>CGU Application bancaire marocaine — Risque élevé</small>
        </div>
      </div>
      <button class="btn btn-outline" onclick="runDemo()">Voir le résultat →</button>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-number" style="color:var(--red)">87%</div>
        <div class="stat-label">des Marocains acceptent les CGU sans les lire</div>
      </div>
      <div class="stat-card">
        <div class="stat-number" style="color:var(--amber)">09-08</div>
        <div class="stat-label">Loi marocaine de protection des données ignorée</div>
      </div>
      <div class="stat-card">
        <div class="stat-number" style="color:var(--blue)">24+</div>
        <div class="stat-label">langues juridiques incompréhensibles pour le citoyen</div>
      </div>
    </div>
  </div>
</div>

<!-- PAGE : LOADING -->
<div class="page" id="page-loading">
  <div class="loading-page">
    <div class="loading-spinner"></div>
    <div class="loading-title">Analyse en cours...</div>
    <p style="color:var(--muted); font-size:14px">Cela prend généralement 5 à 15 secondes</p>
    <div class="loading-steps" id="loading-steps">
      <div class="lstep" id="lstep-0"><div class="lstep-dot"></div><span>Extraction du texte (OCR / PyMuPDF)</span></div>
      <div class="lstep" id="lstep-1"><div class="lstep-dot"></div><span>Détection de la langue (français / arabe)</span></div>
      <div class="lstep" id="lstep-2"><div class="lstep-dot"></div><span>Analyse NLP des clauses (AraBERT / CamemBERT)</span></div>
      <div class="lstep" id="lstep-3"><div class="lstep-dot"></div><span>Calcul du score de risque (Loi 09-08)</span></div>
      <div class="lstep" id="lstep-4"><div class="lstep-dot"></div><span>Génération du résumé en Darija (GPT-4o)</span></div>
    </div>
  </div>
</div>

<!-- PAGE : RÉSULTATS -->
<div class="page" id="page-results">
  <div class="results-page">

    <div class="results-topbar">
      <div>
        <button class="back-btn" onclick="showPage('upload')">← Nouvelle analyse</button>
        <h1 class="results-title">CGU — Application Bancaire Maroc</h1>
        <div class="results-meta">Analysé le <span id="analysis-date"></span> · 2 847 mots · PDF natif</div>
      </div>
      <span class="risk-pill risk-high">⚠️ Risque élevé</span>
    </div>

    <div class="score-card">
      <div class="score-item">
        <div class="score-val" style="color:var(--red)">78/100</div>
        <div class="score-label">Score de risque</div>
      </div>
      <div class="score-item">
        <div class="score-val" style="color:var(--red)">4</div>
        <div class="score-label">Alertes critiques</div>
      </div>
      <div class="score-item">
        <div class="score-val" style="color:var(--amber)">2</div>
        <div class="score-label">Alertes moyennes</div>
      </div>
      <div class="score-item">
        <div class="score-val" style="color:var(--green-dark)">1</div>
        <div class="score-label">Point positif</div>
      </div>
    </div>

    <div class="rtabs">
      <button class="rtab active" onclick="switchResultTab('alerts', this)">
        Alertes <span class="rtab-count count-red">4</span>
      </button>
      <button class="rtab" onclick="switchResultTab('darija', this)">Résumé Darija</button>
      <button class="rtab" onclick="switchResultTab('clauses', this)">Clauses détectées</button>
      <!-- Tab ajouté pour afficher le texte brut extrait par le backend -->
      <button class="rtab" id="tab-raw" onclick="switchResultTab('raw', this)">
        📄 Texte extrait
      </button>
    </div>

    <!-- PANEL ALERTES -->
    <div class="rpanel active" id="rpanel-alerts">
      <div class="alerts-list">
        <div class="alert-card sev-high">
          <div class="alert-icon-wrap icon-red">💬</div>
          <div class="alert-body">
            <div class="alert-header">
              <span class="alert-title">Accès aux SMS</span>
              <span class="loi-tag">Art. 3 Loi 09-08</span>
              <span class="sev-tag high">Élevé</span>
            </div>
            <p class="alert-desc">L'application demande à lire tous tes messages SMS, y compris les codes de vérification bancaires d'autres applications. Aucun consentement explicite n'est requis.</p>
          </div>
        </div>
        <div class="alert-card sev-high">
          <div class="alert-icon-wrap icon-red">📍</div>
          <div class="alert-body">
            <div class="alert-header">
              <span class="alert-title">Localisation GPS en continu</span>
              <span class="loi-tag">Art. 3 Loi 09-08</span>
              <span class="sev-tag high">Élevé</span>
            </div>
            <p class="alert-desc">La clause autorise le suivi de ta position géographique même lorsque l'application est fermée en arrière-plan, sans durée limite précisée.</p>
          </div>
        </div>
        <div class="alert-card sev-high">
          <div class="alert-icon-wrap icon-red">🗂️</div>
          <div class="alert-body">
            <div class="alert-header">
              <span class="alert-title">Accès à la liste de contacts</span>
              <span class="loi-tag">Art. 3 Loi 09-08</span>
              <span class="sev-tag high">Élevé</span>
            </div>
            <p class="alert-desc">L'application peut lire et stocker l'ensemble de ton répertoire téléphonique, noms, numéros et emails inclus.</p>
          </div>
        </div>
        <div class="alert-card sev-high">
          <div class="alert-icon-wrap icon-red">🌍</div>
          <div class="alert-body">
            <div class="alert-header">
              <span class="alert-title">Transfert de données hors Maroc</span>
              <span class="loi-tag">Art. 43 Loi 09-08</span>
              <span class="sev-tag high">Élevé</span>
            </div>
            <p class="alert-desc">Les données sont transférables dans des pays sans niveau de protection équivalent à la législation marocaine, sans notification préalable.</p>
          </div>
        </div>
        <div class="alert-card sev-medium">
          <div class="alert-icon-wrap icon-amber">🤝</div>
          <div class="alert-body">
            <div class="alert-header">
              <span class="alert-title">Partage avec des tiers non listés</span>
              <span class="sev-tag medium">Moyen</span>
            </div>
            <p class="alert-desc">Les données peuvent être partagées avec "des partenaires commerciaux" sans liste exhaustive définie dans le contrat.</p>
          </div>
        </div>
        <div class="alert-card sev-medium">
          <div class="alert-icon-wrap icon-amber">⏳</div>
          <div class="alert-body">
            <div class="alert-header">
              <span class="alert-title">Durée de conservation indéfinie</span>
              <span class="sev-tag medium">Moyen</span>
            </div>
            <p class="alert-desc">Les données sont conservées "aussi longtemps que nécessaire", formulation vague non conforme aux bonnes pratiques.</p>
          </div>
        </div>
        <div class="alert-card sev-low">
          <div class="alert-icon-wrap icon-green">✅</div>
          <div class="alert-body">
            <div class="alert-header">
              <span class="alert-title">Droit de suppression prévu</span>
              <span class="sev-tag low">Positif</span>
            </div>
            <p class="alert-desc">Un mécanisme de suppression des données est mentionné, avec un délai de traitement de 90 jours.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- PANEL DARIJA -->
    <div class="rpanel" id="rpanel-darija">
      <div class="darija-card">
        <div class="darija-header">
          <h3>ملخص بالدارجة</h3>
          <span class="model-tag">🤖 توليد بـ GPT-4o + AraBERT</span>
        </div>
        <div class="darija-body">
          <div class="darija-block">
            <div class="darija-label">الملخص / Résumé</div>
            <div class="darija-text">
              هاد التطبيق كيطلب صلاحيات بزاف وخطيرة. كيقرا رسائل SMS ديالك، وكيتبع موقعك الجغرافي حتى منين تسد التطبيق. كذلك معلوماتك كتمشي لأطراف خارج المغرب بلا ما تعرف.
              <br><br>
              هاد التطبيق عندو الحق يقرأ: رسائلك SMS، جهات الاتصال ديالك، الموقع الجغرافي ديالك، والصور في الجهاز ديالك.
            </div>
            <div class="darija-warning">⚠️ نصيحة: لا توافق بلا ما تفهم</div>
          </div>
          <div class="darija-perms">
            <div class="darija-perms-label">الصلاحيات الخطيرة المطلوبة :</div>
            <div class="perm-tags">
              <span class="perm-tag">📱 رسائل SMS</span>
              <span class="perm-tag">📞 جهات الاتصال</span>
              <span class="perm-tag">📍 الموقع GPS</span>
              <span class="perm-tag">📸 الصور</span>
              <span class="perm-tag">🌍 نقل خارج المغرب</span>
            </div>
          </div>
          <div class="conformite-box">
            <div class="conformite-title">📋 Conformité Loi 09-08</div>
            <div class="conformite-text">
              3 violations potentielles détectées : accès aux SMS sans consentement explicite (Art. 3),
              localisation sans limitation (Art. 3), transfert hors Maroc sans garanties (Art. 43).
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- PANEL CLAUSES -->
    <div class="rpanel" id="rpanel-clauses">
      <div class="clauses-grid">
        <div class="clause-card">
          <div class="clause-label">📦 Données collectées</div>
          <div class="clause-val">SMS, contacts, localisation, photos, données bancaires, identifiants publicitaires</div>
        </div>
        <div class="clause-card">
          <div class="clause-label">⏳ Durée de conservation</div>
          <div class="clause-val">Non précisée — "aussi longtemps que nécessaire pour les services"</div>
        </div>
        <div class="clause-card">
          <div class="clause-label">🤝 Partage tiers</div>
          <div class="clause-val">Partenaires commerciaux non nommés, autorités, filiales, acquéreurs potentiels</div>
        </div>
        <div class="clause-card">
          <div class="clause-label">🌍 Transfert international</div>
          <div class="clause-val">Autorisé vers pays sans protection équivalente, sans notification</div>
        </div>
        <div class="clause-card">
          <div class="clause-label">🗑️ Droit de suppression</div>
          <div class="clause-val">Prévu — délai de 90 jours, sans garantie de suppression totale chez les tiers</div>
        </div>
        <div class="clause-card">
          <div class="clause-label">⚖️ Droit applicable</div>
          <div class="clause-val">Droit marocain — Loi 09-08 mentionnée mais clauses partiellement non conformes</div>
        </div>
      </div>
      <div class="export-bar">
        <div class="export-text">
          Rapport complet disponible
          <small>PDF · inclut alertes, résumé Darija et clauses détectées</small>
        </div>
        <div class="export-btns">
          <button class="btn btn-outline" onclick="alert('Disponible avec le backend connecté')">📤 Partager</button>
          <button class="btn btn-primary" onclick="downloadReport()">⬇️ Télécharger</button>
        </div>
      </div>
    </div>

    <!-- PANEL TEXTE EXTRAIT — rempli dynamiquement par app.js -->
    <div class="rpanel" id="rpanel-raw">
      <div class="raw-text-card">

        <!-- En-tête avec métadonnées de l'extraction -->
        <div class="raw-text-header">
          <div class="raw-text-title">Texte brut extrait</div>
          <div class="raw-text-meta" id="raw-meta">—</div>
        </div>

        <!-- Zone d'affichage du texte — remplie par JS -->
        <pre class="raw-text-body" id="raw-text-body">Aucun fichier analysé pour le moment.
Uploade un PDF ou une image pour voir le texte extrait ici.</pre>

        <!-- Barre d'actions -->
        <div class="raw-text-footer">
          <span class="char-count" id="raw-char-count">0 caractères</span>
          <button class="btn btn-outline" onclick="copyRawText()">📋 Copier le texte</button>
        </div>

      </div>
    </div>

  </div>
</div>

<script src="app.js"></script>
</body>
</html>