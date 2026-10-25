// Local semantic retrieval over precomputed PDF embeddings (no query API).
const form = document.getElementById('semantic-form');
const queryInput = document.getElementById('semantic-query');
const go = document.getElementById('semantic-go');
const status = document.getElementById('semantic-status');
const results = document.getElementById('semantic-results');
const subject = document.getElementById('semantic-subject');
const includeArchive = document.getElementById('semantic-archive');

let indexPromise = null;
let extractorPromise = null;

function message(value) { status.textContent = value; }
function internalLink(value) {
  // Catalog-relative paths only, never link to a remote origin.
  const path = String(value || '').replace(/^\/+/, '');
  return '/pub/' + path;
}

async function loadIndex() {
  if (!indexPromise) {
    indexPromise = (async () => {
      const [metaResponse, vectorsResponse] = await Promise.all([
        fetch('/pub/semantic-index.json'),
        fetch('/pub/semantic-vectors.i8')
      ]);
      if (!metaResponse.ok || !vectorsResponse.ok) {
        throw new Error('The semantic index is not published yet. Its GitHub Actions build may still need to run.');
      }
      const meta = await metaResponse.json();
      const vectors = new Int8Array(await vectorsResponse.arrayBuffer());
      if (meta.schema !== 1 || meta.dimensions !== 384 ||
          meta.format !== 'signed-int8-row-major-scale-127' ||
          vectors.length !== meta.passages.length * meta.dimensions) {
        throw new Error('Semantic index files are incompatible or incomplete.');
      }
      const cats = [...new Set(meta.publications.map(a => a.subject))].filter(Boolean).sort();
      subject.replaceChildren(new Option('All subjects', ''));
      for (const cat of cats) subject.add(new Option(cat, cat));
      return {meta, vectors};
    })().catch(err => { indexPromise = null; throw err; });
  }
  return indexPromise;
}

async function loadModel() {
  if (!extractorPromise) {
    extractorPromise = (async () => {
      message('Loading the local semantic model. The first download may be substantial…');
      const {pipeline} = await import('https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1');
      return pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2', {
        dtype: 'q8',
        progress_callback: progress => {
          if (progress.status === 'progress' && Number.isFinite(progress.progress)) {
            message('Loading semantic model: ' + Math.round(progress.progress) + '%');
          }
        }
      });
    })().catch(err => { extractorPromise = null; throw err; });
  }
  return extractorPromise;
}

function makeResult(article, hit) {
  const card = document.createElement('article');
  card.className = 'semantic-result';
  const heading = document.createElement('h2');
  const articleLink = document.createElement('a');
  articleLink.href = internalLink(article.href);
  articleLink.textContent = article.title;
  heading.append(articleLink);
  card.append(heading);
  const meta = document.createElement('p');
  meta.className = 'semantic-meta';
  meta.textContent = article.subject + (article.archived ? ' · Archived' : '') +
    (hit.p ? ' · PDF page ' + hit.p : ' · Article metadata');
  card.append(meta);
  const excerpt = document.createElement('p');
  excerpt.className = 'semantic-snippet';
  excerpt.textContent = hit.s;
  card.append(excerpt);
  if (hit.p && article.pdf) {
    const links = document.createElement('div');
    links.className = 'semantic-links';
    const pdfLink = document.createElement('a');
    pdfLink.href = internalLink(article.pdf) + '#page=' + hit.p;
    pdfLink.target = '_blank';
    pdfLink.rel = 'noopener noreferrer';
    pdfLink.textContent = 'Open PDF at page ' + hit.p;
    links.append(pdfLink);
    card.append(links);
  }
  return card;
}

function search(meta, vectors, query, embedding) {
  const best = new Map();
  const terms = query.toLowerCase().split(/\s+/).filter(x => x.length > 2);
  const dims = meta.dimensions;
  for (let i = 0; i < meta.passages.length; i++) {
    const pass = meta.passages[i];
    const article = meta.publications[pass.a];
    if ((!includeArchive.checked && article.archived) ||
        (subject.value && article.subject !== subject.value)) continue;
    const offset = i * dims;
    let dot = 0;
    for (let j = 0; j < dims; j++) dot += embedding[j] * vectors[offset + j];
    let score = dot / 127;
    // A small exact-name bonus assists formula-like proper names such as AMLD+0.
    const title = article.title.toLowerCase();
    if (terms.length && terms.every(t => title.includes(t))) score += .06;
    const old = best.get(pass.a);
    if (!old || score > old.score) best.set(pass.a, {score, pass});
  }
  return [...best.entries()].sort((a, b) => b[1].score - a[1].score).slice(0, 20);
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (query.length < 2) return;
  go.disabled = true;
  results.replaceChildren();
  try {
    message('Loading the public publication index…');
    const {meta, vectors} = await loadIndex();
    const model = await loadModel();
    message('Comparing your question with article passages…');
    const output = await model(query, {pooling: 'mean', normalize: true});
    const embedding = output.data;
    if (!embedding || embedding.length !== meta.dimensions) {
      throw new Error('Unexpected embedding dimensions.');
    }
    const ranked = search(meta, vectors, query, embedding);
    for (const [articleIndex, hit] of ranked) {
      results.append(makeResult(meta.publications[articleIndex], hit.pass));
    }
    message(
      ranked.length + ' related publication' + (ranked.length === 1 ? '' : 's') +
      ' shown, ranked by passage similarity. Indexed passages: ' + meta.passage_count +
      (meta.unavailable_pdfs.length ? '. Some PDFs were unavailable for extraction.' : '.')
    );
  } catch (err) {
    message('Semantic search unavailable: ' + (err && err.message ? err.message : String(err)));
    const link = document.createElement('a');
    link.href = '/pub/';
    link.textContent = 'Use the existing publication search';
    results.append(link);
  } finally {
    go.disabled = false;
  }
});
