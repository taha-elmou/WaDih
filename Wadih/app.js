/* ══════════════════════════════════════════════════════════════
   WADIH — app.js
   Logique principale de l'interface
   Modifié : intégration backend FastAPI (extraction texte)
══════════════════════════════════════════════════════════════ */

// ── URL du backend FastAPI ──
// Change cette valeur si ton serveur tourne sur un autre port.
const BACKEND_URL = "http://127.0.0.1:8000";

// ── Fichier en cours d'analyse (référence globale) ──
// Stocké ici pour être accessible depuis startAnalysis() et renderExtractedText().
let currentFile = null;


// ══════════════════════════════════════════════════════════════
//  Navigation entre pages
// ══════════════════════════════════════════════════════════════

function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  window.scrollTo(0, 0);
}


// ══════════════════════════════════════════════════════════════
//  Tabs input (page upload)
// ══════════════════════════════════════════════════════════════

function switchInputTab(id, el) {
  document.querySelectorAll('.itab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.input-panel').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('panel-' + id).classList.add('active');
}


// ══════════════════════════════════════════════════════════════
//  Tabs résultats
// ══════════════════════════════════════════════════════════════

function switchResultTab(id, el) {
  document.querySelectorAll('.rtab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.rpanel').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('rpanel-' + id).classList.add('active');
}


// ══════════════════════════════════════════════════════════════
//  Compteur de caractères (textarea)
// ══════════════════════════════════════════════════════════════

function updateCharCount() {
  const n = document.getElementById('text-input').value.length;
  document.getElementById('char-count').textContent = n.toLocaleString() + ' caractères';
}


// ══════════════════════════════════════════════════════════════
//  Remplir le champ URL avec un exemple
// ══════════════════════════════════════════════════════════════

function fillUrl(url) {
  document.getElementById('url-input').value = url;
}


// ══════════════════════════════════════════════════════════════
//  Drag & Drop — capture le fichier ET l'envoie au backend
// ══════════════════════════════════════════════════════════════

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('dropzone').classList.remove('dragging');

  if (e.dataTransfer.files.length > 0) {
    // Sauvegarder la référence du fichier déposé
    currentFile = e.dataTransfer.files[0];
    startAnalysis();
  }
}

function handleFileSelect(e) {
  if (e.target.files.length > 0) {
    // Sauvegarder la référence du fichier sélectionné
    currentFile = e.target.files[0];
    startAnalysis();
  }
}


// ══════════════════════════════════════════════════════════════
//  Animation de chargement + appel backend + transition résultats
// ══════════════════════════════════════════════════════════════

function startAnalysis() {
  showPage('loading');

  const steps = document.querySelectorAll('.lstep');
  let i = 0;

  // Réinitialiser tous les steps
  steps.forEach(s => s.className = 'lstep');

  // ── Détermine si on a un vrai fichier à envoyer ──
  const hasFile = currentFile !== null;

  // ── Lance l'appel API en parallèle de l'animation ──
  // La promesse est stockée pour être attendue à la fin de l'animation.
  let extractionPromise = null;

  if (hasFile) {
    extractionPromise = callExtractAPI(currentFile);
  }

  // ── Animation séquentielle des steps ──
  function nextStep() {
    if (i > 0) steps[i - 1].classList.replace('active', 'done');

    if (i < steps.length) {
      steps[i].classList.add('active');
      i++;
      setTimeout(nextStep, 900 + Math.random() * 400);
    } else {
      // Tous les steps sont passés → attendre la fin de l'API si nécessaire
      if (extractionPromise) {
        // Attendre que l'API réponde, puis afficher les résultats
        extractionPromise
          .then(data => {
            renderExtractedText(data);
            finalizeResults();
          })
          .catch(err => {
            // Afficher l'erreur dans le panel Texte extrait sans bloquer l'UI
            renderExtractedTextError(err.message || "Erreur inconnue");
            finalizeResults();
          });
      } else {
        // Pas de fichier (démo ou texte/URL) → afficher résultats immédiatement
        setTimeout(finalizeResults, 600);
      }
    }
  }

  nextStep();
}


// ══════════════════════════════════════════════════════════════
//  Finalisation : afficher la page résultats avec la date
// ══════════════════════════════════════════════════════════════

function finalizeResults() {
  document.getElementById('analysis-date').textContent =
    new Date().toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });

  showPage('results');
}


// ══════════════════════════════════════════════════════════════
//  Appel API FastAPI — POST /extract
// ══════════════════════════════════════════════════════════════

/**
 * Envoie le fichier au backend FastAPI et retourne la promesse JSON.
 *
 * @param {File} file — L'objet File sélectionné par l'utilisateur
 * @returns {Promise<Object>} — { extracted_text, method, pages, filename, char_count }
 */
async function callExtractAPI(file) {
  const formData = new FormData();

  // Le paramètre "file" correspond au nom attendu par FastAPI : File(...)
  formData.append('file', file);

  const response = await fetch(`${BACKEND_URL}/extract`, {
    method: 'POST',
    body: formData,
    // Ne pas définir Content-Type manuellement : fetch le gère
    // automatiquement avec le bon boundary pour multipart/form-data.
  });

  if (!response.ok) {
    // Extraire le message d'erreur renvoyé par FastAPI
    let errorDetail = `Erreur HTTP ${response.status}`;
    try {
      const errData = await response.json();
      errorDetail = errData.detail || errorDetail;
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return response.json();
}


// ══════════════════════════════════════════════════════════════
//  Rendu du texte extrait dans le panel rpanel-raw
// ══════════════════════════════════════════════════════════════

/**
 * Remplit le panel "Texte extrait" avec la réponse du backend.
 *
 * @param {Object} data — Réponse JSON du backend
 */
function renderExtractedText(data) {
  const bodyEl      = document.getElementById('raw-text-body');
  const metaEl      = document.getElementById('raw-meta');
  const charCountEl = document.getElementById('raw-char-count');
  const tabEl       = document.getElementById('tab-raw');

  // Construire un label lisible pour la méthode utilisée
  const methodLabels = {
    pymupdf_native:    "PyMuPDF — texte natif",
    pymupdf_ocr_mixed: "PyMuPDF + OCR Tesseract (hybride)",
    pymupdf_ocr_full:  "OCR Tesseract — PDF scanné",
    tesseract_ocr:     "OCR Tesseract — image",
  };
  const methodLabel = methodLabels[data.method] || data.method;

  // Remplir l'en-tête (métadonnées)
  metaEl.textContent =
    `${data.filename} · ${data.pages} page(s) · ${methodLabel}`;

  // Remplir le corps
  bodyEl.classList.remove('is-empty', 'is-loading', 'is-error');

  if (data.extracted_text && data.extracted_text.trim().length > 0) {
    bodyEl.textContent = data.extracted_text;
  } else {
    bodyEl.textContent =
      "[Aucun texte détecté. Vérifie la qualité du scan ou la langue du document.]";
    bodyEl.classList.add('is-empty');
  }

  // Compteur de caractères
  const charCount = data.char_count || data.extracted_text?.length || 0;
  charCountEl.textContent = charCount.toLocaleString() + ' caractères';

  // Afficher un badge sur le tab pour indiquer que le texte est disponible
  if (tabEl) {
    tabEl.innerHTML = `📄 Texte extrait <span class="rtab-count count-amber">✓</span>`;
  }
}


/**
 * Affiche un message d'erreur dans le panel "Texte extrait".
 *
 * @param {string} message — Message d'erreur à afficher
 */
function renderExtractedTextError(message) {
  const bodyEl      = document.getElementById('raw-text-body');
  const metaEl      = document.getElementById('raw-meta');
  const charCountEl = document.getElementById('raw-char-count');

  bodyEl.classList.remove('is-empty', 'is-loading');
  bodyEl.classList.add('is-error');

  bodyEl.textContent =
    `⚠️ Erreur lors de l'extraction :\n\n${message}\n\n` +
    `Vérifie que le backend FastAPI est bien lancé :\n` +
    `uvicorn main:app --reload --host 127.0.0.1 --port 8000`;

  metaEl.textContent = "Échec de l'extraction";
  charCountEl.textContent = "—";
}


// ══════════════════════════════════════════════════════════════
//  Copier le texte extrait dans le presse-papiers
// ══════════════════════════════════════════════════════════════

function copyRawText() {
  const bodyEl = document.getElementById('raw-text-body');
  const text = bodyEl.textContent;

  if (!text || bodyEl.classList.contains('is-empty')) {
    alert('Aucun texte à copier.');
    return;
  }

  navigator.clipboard.writeText(text)
    .then(() => {
      // Feedback visuel temporaire sur le bouton
      const btn = event.target;
      const originalText = btn.textContent;
      btn.textContent = '✅ Copié !';
      setTimeout(() => { btn.textContent = originalText; }, 2000);
    })
    .catch(() => {
      alert('Impossible de copier. Sélectionne le texte manuellement.');
    });
}


// ══════════════════════════════════════════════════════════════
//  Démo rapide (sans fichier réel — résultats statiques)
// ══════════════════════════════════════════════════════════════

function runDemo() {
  // Réinitialiser la référence du fichier pour ne pas appeler le backend
  currentFile = null;

  // Préparer un texte de démonstration dans le panel Texte extrait
  prepareRawPanelForDemo();

  startAnalysis();
}


/**
 * Remplit le panel Texte extrait avec un texte de démonstration fictif.
 */
function prepareRawPanelForDemo() {
  const bodyEl      = document.getElementById('raw-text-body');
  const metaEl      = document.getElementById('raw-meta');
  const charCountEl = document.getElementById('raw-char-count');

  const demoText =
`CONDITIONS GÉNÉRALES D'UTILISATION — APPLICATION BANCAIRE MAROC
Version 3.2 — Mise à jour : Janvier 2024

Article 1 – Objet
Les présentes conditions générales d'utilisation régissent l'accès et l'utilisation
de l'application mobile de la banque par tout utilisateur titulaire d'un compte.

Article 3 – Données personnelles collectées
L'application collecte et traite les données suivantes :
- Numéro de téléphone et messages SMS (y compris codes OTP tiers)
- Position géographique en temps réel, y compris en arrière-plan
- Liste complète des contacts téléphoniques
- Photos et fichiers stockés sur l'appareil
- Identifiants publicitaires (IDFA/GAID)
- Données comportementales et historique de navigation

Article 43 – Transferts internationaux
Les données collectées peuvent être transférées et traitées dans des pays
ne disposant pas d'une protection équivalente à la législation marocaine,
notamment pour des raisons d'hébergement, de maintenance ou d'analyse.

Article 12 – Durée de conservation
Les données sont conservées aussi longtemps que nécessaire à la fourniture
des services, sans durée maximale définie.

Article 18 – Partage avec des tiers
La banque se réserve le droit de partager les données avec ses partenaires
commerciaux, filiales, prestataires techniques et acquéreurs potentiels,
dont la liste exhaustive n'est pas communiquée dans le présent contrat.

Article 22 – Droit de suppression
Tout utilisateur peut demander la suppression de ses données.
La banque s'engage à traiter les demandes dans un délai de 90 jours.
Cette suppression ne garantit pas l'effacement chez les partenaires tiers.`;

  bodyEl.classList.remove('is-empty', 'is-loading', 'is-error');
  bodyEl.textContent = demoText;
  metaEl.textContent = "demo-cgu-bancaire.pdf · 1 page · Démo (texte simulé)";
  charCountEl.textContent = demoText.length.toLocaleString() + ' caractères';
}


// ══════════════════════════════════════════════════════════════
//  Téléchargement du rapport
// ══════════════════════════════════════════════════════════════

// Note : cette fonction génère un rapport .txt côté frontend (simulation).
// Elle sera remplacée par un appel à un endpoint /report du backend
// qui générera un vrai PDF quand cette fonctionnalité sera développée.

function downloadReport() {
  const date = new Date().toLocaleDateString('fr-FR');

  const content =
`RAPPORT WADIH — ANALYSE CGU
================================
Document : CGU Application Bancaire Maroc
Date     : ${date}
Score de risque : 78/100 — ÉLEVÉ

ALERTES CRITIQUES (4)
---------------------
1. Accès aux SMS           — Art. 3  Loi 09-08
2. Localisation GPS continu — Art. 3  Loi 09-08
3. Accès contacts           — Art. 3  Loi 09-08
4. Transfert hors Maroc     — Art. 43 Loi 09-08

ALERTES MOYENNES (2)
--------------------
5. Partage avec des tiers non listés
6. Durée de conservation indéfinie

POINT POSITIF (1)
-----------------
7. Droit de suppression prévu (délai 90 jours)

RÉSUMÉ EN DARIJA
----------------
هاد التطبيق كيطلب صلاحيات بزاف وخطيرة.
كيقرا رسائل SMS ديالك، وكيتبع موقعك الجغرافي.
معلوماتك كتمشي لأطراف خارج المغرب.
نصيحة: لا توافق بلا ما تفهم

================================
Rapport généré par WaDih
Protection des données — Loi 09-08`;

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'rapport-wadih.txt';
  a.click();
}