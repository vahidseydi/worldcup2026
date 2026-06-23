<template>
  <!-- Help trigger button -->
  <button class="help-fab" @click="open" title="How to use this dashboard">?</button>

  <!-- Modal overlay -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="help-overlay" @click.self="close">
        <div class="help-modal">

          <!-- Dark header band -->
          <div class="help-header">
            <div class="step-counter">{{ step + 1 }}<span class="of-total">/{{ steps.length }}</span></div>
            <div class="header-text">
              <div class="header-eyebrow">World Cup 2026 Dashboard</div>
              <h2 class="header-title">{{ steps[step].title }}</h2>
            </div>
            <button class="help-close" @click="close">✕</button>
          </div>

          <!-- Progress bar -->
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${((step + 1) / steps.length) * 100}%` }" />
          </div>

          <!-- Body -->
          <div class="help-body">
            <div class="step-icon">{{ steps[step].icon }}</div>
            <p class="step-desc" v-html="steps[step].desc" />
            <div v-if="steps[step].hint" class="hint-wrap">
              <div class="hint-label">Example</div>
              <div class="hint-box" v-html="steps[step].hint" />
            </div>
          </div>

          <!-- Footer -->
          <div class="help-footer">
            <div class="dot-row">
              <button
                v-for="(s, i) in steps"
                :key="i"
                class="dot"
                :class="{ active: i === step, done: i < step }"
                @click="step = i"
              />
            </div>
            <div class="nav-btns">
              <button v-if="step > 0" class="btn-back" @click="step--">← Back</button>
              <button v-if="step < steps.length - 1" class="btn-next" @click="step++">
                Next <span class="btn-arrow">→</span>
              </button>
              <button v-else class="btn-next btn-done" @click="close">
                Let's go! 🏆
              </button>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const visible = ref(false)
const step    = ref(0)

const steps = [
  {
    icon: '🌍',
    title: 'What is this?',
    desc: 'A <strong>live probabilistic dashboard</strong> for the 2026 FIFA World Cup. A Bayesian model updates every 60 seconds with real match results, estimating each team\'s chances of qualifying, reaching the knockouts, and winning the trophy.',
    hint: `
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <div style="background:rgba(16,185,129,0.15);border:1px solid #10b981;color:#10b981;border-radius:6px;padding:7px 14px;font-weight:700;font-size:0.9rem">87% qualify</div>
        <div style="background:rgba(245,158,11,0.15);border:1px solid #f59e0b;color:#f59e0b;border-radius:6px;padding:7px 14px;font-weight:700;font-size:0.9rem">43% qualify</div>
        <div style="background:rgba(239,68,68,0.15);border:1px solid #ef4444;color:#ef4444;border-radius:6px;padding:7px 14px;font-weight:700;font-size:0.9rem">12% qualify</div>
      </div>
      <p style="margin:8px 0 0;font-size:0.75rem;color:#9ca3af">Green = strong favourite, Yellow = uncertain, Red = unlikely</p>
    `,
  },
  {
    icon: '🔍',
    title: 'Browse teams on the home page',
    desc: 'All 48 teams are shown grouped by their group (A to L). Each tile shows the team\'s <strong>probability of qualifying</strong> for the knockout round. Use the <strong>search bar</strong> to find a team quickly, or just browse.',
    hint: `
      <div style="border:1px solid #374151;border-radius:8px;padding:10px 12px;font-size:0.8rem">
        <div style="font-weight:700;margin-bottom:8px;color:#9ca3af;font-size:0.7rem;text-transform:uppercase;letter-spacing:.06em">Group G</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <div style="background:#1f2937;border:1px solid #374151;border-radius:8px;padding:8px 12px;text-align:center;min-width:72px">
            <div>🇮🇷</div>
            <div style="font-size:0.73rem;font-weight:600;color:#d1d5db;margin:3px 0">Iran</div>
            <div style="font-size:1rem;font-weight:800;color:#10b981">71%</div>
          </div>
          <div style="background:#1f2937;border:1px solid #374151;border-radius:8px;padding:8px 12px;text-align:center;min-width:72px">
            <div>🇧🇪</div>
            <div style="font-size:0.73rem;font-weight:600;color:#d1d5db;margin:3px 0">Belgium</div>
            <div style="font-size:1rem;font-weight:800;color:#f59e0b">48%</div>
          </div>
          <div style="background:#1f2937;border:1px solid #374151;border-radius:8px;padding:8px 12px;text-align:center;min-width:72px">
            <div>🇪🇬</div>
            <div style="font-size:0.73rem;font-weight:600;color:#d1d5db;margin:3px 0">Egypt</div>
            <div style="font-size:1rem;font-weight:800;color:#ef4444">21%</div>
          </div>
        </div>
      </div>
      <p style="margin:8px 0 0;font-size:0.75rem;color:#9ca3af">Click any team tile to open that team's detail page</p>
    `,
  },
  {
    icon: '📊',
    title: 'Explore a team\'s page',
    desc: 'Click any team to see their full picture: a <strong>Tournament Path</strong> chart showing the probability of reaching each stage, <strong>Possible Opponents</strong> in each knockout round, and <strong>Group Matches</strong> with live standings.',
    hint: `
      <div style="border:1px solid #374151;border-radius:8px;padding:10px 12px">
        <div style="font-size:0.72rem;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px">Tournament Path</div>
        <div style="display:flex;gap:5px;align-items:flex-end;height:64px">
          ${['Qualify:71%:10b981:43', 'R32:55%:10b981:35', 'R16:28%:f59e0b:18', 'QF:9%:f59e0b:6', 'SF:3%:ef4444:2', 'Final:1%:6b7280:1'].map(s => {
            const [label, pct, col, h] = s.split(':')
            return `<div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
              <span style="font-size:0.6rem;font-weight:700;color:#${col}">${pct}</span>
              <div style="width:100%;background:#${col};border-radius:3px 3px 0 0;height:${h}px;opacity:0.85"></div>
              <span style="font-size:0.58rem;color:#9ca3af">${label}</span>
            </div>`
          }).join('')}
        </div>
      </div>
      <p style="margin:8px 0 0;font-size:0.75rem;color:#9ca3af">Each bar shows the probability of reaching that stage</p>
    `,
  },
  {
    icon: '⚡',
    title: 'Predict matches yourself',
    desc: 'Use the <strong>Scenario Predictions</strong> card on any team page. Pick a group, pick a match, type a predicted score, and hit <strong>+ Add</strong>. Stack as many predictions as you like across any group. Nothing changes the real data, it\'s your private "what if" sandbox.',
    hint: `
      <div style="border:1px solid #374151;border-left:3px solid #f59e0b;border-radius:8px;padding:10px 12px;font-size:0.8rem">
        <div style="font-weight:700;color:#f59e0b;margin-bottom:8px;font-size:0.72rem;text-transform:uppercase;letter-spacing:.05em">⚡ Scenario Predictions</div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px">
          <select style="padding:4px 8px;border:1px solid #374151;background:#1f2937;color:#d1d5db;border-radius:5px;font-size:0.75rem" disabled>
            <option>Group G</option>
          </select>
          <select style="padding:4px 8px;border:1px solid #374151;background:#1f2937;color:#d1d5db;border-radius:5px;font-size:0.75rem;flex:1" disabled>
            <option>Iran vs Egypt</option>
          </select>
        </div>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
          <span style="font-size:0.78rem;font-weight:600;color:#d1d5db">🇮🇷 Iran</span>
          <input type="number" value="2" style="width:36px;text-align:center;padding:3px;border:1px solid #f59e0b;background:#1f2937;color:#f59e0b;border-radius:5px;font-weight:700" readonly />
          <span style="font-weight:700;color:#6b7280">–</span>
          <input type="number" value="0" style="width:36px;text-align:center;padding:3px;border:1px solid #f59e0b;background:#1f2937;color:#f59e0b;border-radius:5px;font-weight:700" readonly />
          <span style="font-size:0.78rem;font-weight:600;color:#d1d5db">Egypt 🇪🇬</span>
          <button style="background:#f59e0b;color:#111;border:none;border-radius:5px;padding:4px 12px;font-size:0.75rem;font-weight:700">+ Add</button>
        </div>
      </div>
      <p style="margin:8px 0 0;font-size:0.75rem;color:#9ca3af">Your predictions are private and never affect the real data</p>
    `,
  },
  {
    icon: '📈',
    title: 'Read the scenario overlay',
    desc: 'After adding predictions, the <strong>Tournament Path</strong> chart shows an <strong style="color:#f59e0b">amber bar</strong> alongside the actual bar. A <strong style="color:#10b981">+5%</strong> means your scenario helps, a <strong style="color:#ef4444">-3%</strong> means it hurts. The Possible Opponents section updates too. Remove any prediction with ✕, or wipe them all with "Clear all".',
    hint: `
      <div style="border:1px solid #374151;border-radius:8px;padding:10px 12px">
        <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:5px;padding:4px 10px;font-size:0.7rem;font-weight:600;color:#f59e0b;margin-bottom:10px">⚡ Scenario mode, predictions applied</div>
        <div style="display:flex;gap:5px;align-items:flex-end;height:64px">
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.6rem;font-weight:700;color:#10b981">+6%</span>
            <div style="width:100%;position:relative;height:43px">
              <div style="position:absolute;bottom:0;width:100%;background:#10b981;opacity:0.35;border-radius:3px 3px 0 0;height:43px"></div>
              <div style="position:absolute;bottom:0;right:0;width:42%;background:#f59e0b;border-radius:3px 3px 0 0;height:49px;opacity:0.9"></div>
            </div>
            <span style="font-size:0.58rem;color:#9ca3af">Qualify</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.6rem;font-weight:700;color:#10b981">+4%</span>
            <div style="width:100%;position:relative;height:35px">
              <div style="position:absolute;bottom:0;width:100%;background:#10b981;opacity:0.35;border-radius:3px 3px 0 0;height:35px"></div>
              <div style="position:absolute;bottom:0;right:0;width:42%;background:#f59e0b;border-radius:3px 3px 0 0;height:39px;opacity:0.9"></div>
            </div>
            <span style="font-size:0.58rem;color:#9ca3af">R32</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.6rem;font-weight:700;color:#ef4444">-2%</span>
            <div style="width:100%;position:relative;height:18px">
              <div style="position:absolute;bottom:0;width:100%;background:#f59e0b;opacity:0.35;border-radius:3px 3px 0 0;height:18px"></div>
              <div style="position:absolute;bottom:0;right:0;width:42%;background:#f59e0b;border-radius:3px 3px 0 0;height:14px;opacity:0.9"></div>
            </div>
            <span style="font-size:0.58rem;color:#9ca3af">R16</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.6rem;font-weight:700;color:#6b7280">0%</span>
            <div style="width:100%;position:relative;height:5px">
              <div style="position:absolute;bottom:0;width:100%;background:#374151;border-radius:3px 3px 0 0;height:5px"></div>
            </div>
            <span style="font-size:0.58rem;color:#9ca3af">QF</span>
          </div>
        </div>
        <div style="display:flex;gap:14px;margin-top:8px;font-size:0.68rem;color:#9ca3af">
          <span><span style="display:inline-block;width:10px;height:10px;background:#10b981;opacity:0.4;border-radius:2px;margin-right:3px;vertical-align:middle"></span>Actual</span>
          <span><span style="display:inline-block;width:10px;height:10px;background:#f59e0b;border-radius:2px;margin-right:3px;vertical-align:middle"></span>Your scenario</span>
        </div>
      </div>
    `,
  },
]

function open() {
  step.value = 0
  visible.value = true
}

function close() {
  visible.value = false
  localStorage.setItem('wc2026_help_seen', '1')
}

function onKey(e) {
  if (!visible.value) return
  if (e.key === 'Escape') close()
  if (e.key === 'ArrowRight' && step.value < steps.length - 1) step.value++
  if (e.key === 'ArrowLeft'  && step.value > 0) step.value--
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  if (!localStorage.getItem('wc2026_help_seen')) {
    setTimeout(() => { visible.value = true }, 800)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
})
</script>

<style scoped>
/* ── FAB ── */
.help-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 900;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #111827;
  color: #f59e0b;
  border: 2px solid #f59e0b;
  font-size: 1.15rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 4px 18px rgba(245,158,11,0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, transform 0.15s, box-shadow 0.15s;
  font-family: inherit;
}
.help-fab:hover {
  background: #f59e0b;
  color: #111;
  transform: scale(1.08);
  box-shadow: 0 6px 24px rgba(245,158,11,0.5);
}

/* ── Overlay ── */
.help-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.65);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  backdrop-filter: blur(3px);
}

/* ── Modal shell ── */
.help-modal {
  background: #111827;
  border: 1px solid #1f2937;
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(245,158,11,0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #f9fafb;
}

/* ── Header ── */
.help-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px 16px;
  background: #0f172a;
  border-bottom: 1px solid #1f2937;
}

.step-counter {
  font-size: 2rem;
  font-weight: 900;
  color: #f59e0b;
  line-height: 1;
  min-width: 36px;
}
.of-total {
  font-size: 0.9rem;
  color: #4b5563;
  font-weight: 600;
}

.header-text { flex: 1; }
.header-eyebrow {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #f59e0b;
  margin-bottom: 3px;
}
.header-title {
  font-size: 1rem;
  font-weight: 800;
  color: #f9fafb;
  margin: 0;
  line-height: 1.3;
}

.help-close {
  background: none;
  border: 1px solid #374151;
  color: #6b7280;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 6px;
  transition: border-color 0.15s, color 0.15s;
  flex-shrink: 0;
}
.help-close:hover { border-color: #ef4444; color: #ef4444; }

/* ── Progress bar ── */
.progress-track {
  height: 3px;
  background: #1f2937;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #fcd34d);
  transition: width 0.35s ease;
}

/* ── Body ── */
.help-body {
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  min-height: 290px;
}

.step-icon { font-size: 2.8rem; line-height: 1; }

.step-desc {
  font-size: 0.88rem;
  text-align: center;
  color: #d1d5db;
  line-height: 1.65;
  max-width: 400px;
  margin: 0;
}
.step-desc :deep(strong) { color: #f9fafb; }

.hint-wrap { width: 100%; }
.hint-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #4b5563;
  margin-bottom: 6px;
}
.hint-box {
  background: #0f172a;
  border: 1px solid #1f2937;
  border-radius: 10px;
  padding: 12px;
  font-size: 0.82rem;
  color: #d1d5db;
}

/* ── Footer ── */
.help-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-top: 1px solid #1f2937;
  background: #0f172a;
  gap: 12px;
  flex-wrap: wrap;
}

.dot-row { display: flex; gap: 5px; align-items: center; }
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  border: none;
  background: #374151;
  cursor: pointer;
  padding: 0;
  transition: background 0.2s, width 0.2s, border-radius 0.2s;
}
.dot.active  { background: #f59e0b; width: 20px; border-radius: 4px; }
.dot.done    { background: #78350f; }

.nav-btns { display: flex; gap: 8px; align-items: center; }

.btn-back {
  background: none;
  border: 1px solid #374151;
  color: #9ca3af;
  padding: 7px 16px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
  font-family: inherit;
}
.btn-back:hover { border-color: #6b7280; color: #f9fafb; }

.btn-next {
  background: #f59e0b;
  color: #111827;
  border: none;
  padding: 8px 22px;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 800;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
  font-family: inherit;
  display: flex;
  align-items: center;
  gap: 4px;
}
.btn-next:hover { background: #fbbf24; transform: translateY(-1px); }
.btn-arrow { font-size: 1rem; }
.btn-done { background: #10b981; }
.btn-done:hover { background: #059669; }

/* ── Transition ── */
.modal-fade-enter-active { transition: opacity 0.22s, transform 0.22s; }
.modal-fade-leave-active { transition: opacity 0.18s, transform 0.18s; }
.modal-fade-enter-from { opacity: 0; transform: scale(0.96) translateY(8px); }
.modal-fade-leave-to  { opacity: 0; transform: scale(0.96) translateY(8px); }
</style>
