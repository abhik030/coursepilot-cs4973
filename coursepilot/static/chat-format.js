(function (root) {
  'use strict';

  const escapeHtml = value => String(value == null ? '' : value)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  const placeholders = new Set(['KEEP_A', 'KEEP_B', 'ELECTIVE_1']);

  function safeHref(raw) {
    try {
      const url = new URL(raw);
      return url.protocol === 'http:' || url.protocol === 'https:' ? url.href : null;
    } catch (_) { return null; }
  }

  function inline(source) {
    // Hold generated markup while escaping all remaining source text.
    let raw = String(source);
    const held = [];
    const hold = html => `\u0000${held.push(html) - 1}\u0000`;
    raw = raw.replace(/`([^`\n]+)`/g, (_, code) => hold(`<code>${escapeHtml(code)}</code>`));
    raw = raw.replace(/\[([^\]]+)\]\(([^\s)]+)\)/g, (whole, label, rawUrl) => {
      const href = safeHref(rawUrl);
      return href ? hold(`<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`) : whole;
    });
    let text = escapeHtml(raw);
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>');
    return text.replace(/\u0000(\d+)\u0000/g, (_, index) => held[Number(index)] || '');
  }

  function formatText(input) {
    const lines = String(input == null ? '' : input).replace(/\r\n?/g, '\n').split('\n');
    const out = [];
    let paragraph = [], list = null, code = null, table = [];
    const flushParagraph = () => { if (paragraph.length) { out.push(`<p>${paragraph.map(inline).join('<br>')}</p>`); paragraph = []; } };
    const flushList = () => { if (list) { out.push(`<${list.tag}>${list.items.map(x => `<li>${inline(x)}</li>`).join('')}</${list.tag}>`); list = null; } };
    const flushTable = () => {
      if (!table.length) return;
      const rows = table.filter(row => !/^\s*\|?\s*:?-{3,}/.test(row));
      if (rows.length) {
        const cells = row => row.trim().replace(/^\||\|$/g, '').split('|').map(x => x.trim());
        const head = cells(rows[0]);
        out.push(`<div class="cp-table-wrap"><table><thead><tr>${head.map(x => `<th>${inline(x)}</th>`).join('')}</tr></thead><tbody>${rows.slice(1).map(r => `<tr>${cells(r).map(x => `<td>${inline(x)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`);
      }
      table = [];
    };
    const flush = () => { flushParagraph(); flushList(); flushTable(); };

    for (const line of lines) {
      const fence = line.match(/^\s*```([^`]*)$/);
      if (code !== null) {
        if (fence) { out.push(`<pre class="cp-code-block"><code>${escapeHtml(code.join('\n'))}</code></pre>`); code = null; }
        else code.push(line);
        continue;
      }
      if (fence) { flush(); code = []; continue; }
      if (!line.trim()) { flush(); continue; }
      if (line.includes('|') && /^\s*\|?.+\|.+/.test(line)) { flushParagraph(); flushList(); table.push(line); continue; }
      if (table.length) flushTable();
      const heading = line.match(/^\s{0,3}(#{1,6})\s+(.+)$/);
      if (heading) { flush(); const level = heading[1].length; out.push(`<h${level}>${inline(heading[2])}</h${level}>`); continue; }
      const bullet = line.match(/^\s*[-*+]\s+(.+)$/);
      const numbered = line.match(/^\s*\d+[.)]\s+(.+)$/);
      if (bullet || numbered) {
        flushParagraph(); const tag = bullet ? 'ul' : 'ol';
        if (list && list.tag !== tag) flushList();
        if (!list) list = { tag, items: [] };
        list.items.push((bullet || numbered)[1]); continue;
      }
      flushList(); paragraph.push(line);
    }
    flush();
    if (code !== null) out.push(`<pre class="cp-code-block"><code>${escapeHtml(code.join('\n'))}</code></pre>`);
    return out.join('');
  }

  function reportCard(report, catalog) {
    report = report || {};
    const planId = String(report.plan_id == null ? '' : report.plan_id);
    const title = planId ? (/^plan\s+/i.test(planId)?planId:`Plan ${planId}`) : 'Course plan';
    const sections = Array.isArray(report.sections) ? report.sections : [];
    const courses = sections.map(section => {
      const id = String(section == null ? '' : section);
      if (!id || placeholders.has(id)) return '';
      const item = catalog && catalog[id];
      const label = item && (item.title || item.course) ? `${item.title || item.course}${item.course && item.title && !placeholders.has(item.course) ? ` · ${item.course}` : ''}` : '';
      return `<li>${label ? `<span>${escapeHtml(label)}</span>` : ''}<small>CRN ${escapeHtml(id)}</small></li>`;
    }).filter(Boolean);
    const meta = [];
    if (report.credits != null) meta.push(`${escapeHtml(report.credits)} credits`);
    if (typeof report.feasible === 'boolean') meta.push(report.feasible ? 'Reported feasible' : 'Reported infeasible');
    return `<article class="cp-report-card"><h4 class="cp-report-title">${escapeHtml(title)}</h4>${meta.length ? `<p class="cp-report-meta">${meta.join(' · ')}</p>` : ''}${courses.length ? `<ul class="cp-report-courses">${courses.join('')}</ul>` : ''}</article>`;
  }

  function displayText(text, catalog) {
    let result = String(text == null ? '' : text);
    for (const code of placeholders) {
      const item = catalog && (catalog[code]||Object.values(catalog).find(item=>item.course===code));
      const title = item && (item.title || item.course);
      if (title) result = result.replace(new RegExp(`\\b${code}\\b`, 'g'), String(title));
    }
    return result;
  }

  function renderMessage(message, catalog) {
    const reports = Array.isArray(message.reports) ? message.reports : [];
    const time = message.timestamp ? `<time class="cp-turn-time">${escapeHtml(message.timestamp)}</time>` : '';
    return `<div class="cp-turn-body">${formatText(displayText(message.message, catalog))}${reports.length ? `<div class="cp-report-grid">${reports.map(r => reportCard(r, catalog)).join('')}</div>` : ''}</div>${time}`;
  }

  function renderMessages(messages, catalog) {
    const input = Array.isArray(messages) ? messages : [];
    const out = [];
    for (let i = 0; i < input.length;) {
      const message = input[i] || {};
      if (message.role === 'assistant') {
        const group = [];
        while (i < input.length && input[i] && input[i].role === 'assistant') group.push(input[i++]);
        const earlier = group.slice(0, -1);
        out.push(`<section class="cp-chat-turn cp-assistant-turn"><span class="cp-turn-label">Assistant</span>${earlier.length ? `<details class="cp-activity"><summary>Earlier updates</summary>${earlier.map(m => `<div class="cp-activity-item">${renderMessage(m, catalog)}</div>`).join('')}</details>` : ''}<div class="cp-assistant-main">${renderMessage(group[group.length - 1], catalog)}</div></section>`);
      } else {
        out.push(`<section class="cp-chat-turn cp-user-turn"><span class="cp-turn-label">You</span>${renderMessage(message, catalog)}</section>`);
        i++;
      }
    }
    return out.join('');
  }

  root.CoursePilotChat = { formatText, renderMessages };
})(window);
