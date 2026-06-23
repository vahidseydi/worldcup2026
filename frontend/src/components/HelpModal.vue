<template>
  <!-- Help trigger button -->
  <button class="help-fab" @click="open" title="How to use this dashboard">?</button>

  <!-- Modal overlay -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="help-overlay" @click.self="close">
        <div class="help-modal">

          <!-- Header -->
          <div class="help-header">
            <span class="help-logo">🏆</span>
            <div>
              <h2 class="help-title">How to use this dashboard</h2>
              <p class="help-step-label">Step {{ step + 1 }} of {{ steps.length }}</p>
            </div>
            <button class="help-close" @click="close">✕</button>
          </div>

          <!-- Progress dots -->
          <div class="help-dots">
            <button
              v-for="(s, i) in steps"
              :key="i"
              class="dot"
              :class="{ active: i === step, done: i < step }"
              @click="step = i"
            />
          </div>

          <!-- Step content -->
          <div class="help-body">
            <div class="step-icon">{{ steps[step].icon }}</div>
            <h3 class="step-title">{{ steps[step].title }}</h3>
            <p class="step-desc" v-html="steps[step].desc" />

            <!-- Visual hint -->
            <div v-if="steps[step].hint" class="step-hint">
              <div class="hint-box" v-html="steps[step].hint" />
            </div>
          </div>

          <!-- Footer nav -->
          <div class="help-footer">
            <button v-if="step > 0" class="btn-nav secondary" @click="step--">← Back</button>
            <span v-else />
            <button v-if="step < steps.length - 1" class="btn-nav primary" @click="step++">
              Next →
            </button>
            <button v-else class="btn-nav primary" @click="close">
              Got it!
            </button>
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
    desc: 'A <strong>live probabilistic dashboard</strong> for the 2026 FIFA World Cup. It uses a Bayesian model — updated every 60 seconds with real match results — to estimate each team\'s chances of qualifying, reaching the knockouts, and winning the trophy.',
    hint: `
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
        <div style="background:#d1fae5;color:#065f46;border-radius:8px;padding:8px 14px;font-weight:700">87% qualify</div>
        <div style="background:#fef3c7;color:#92400e;border-radius:8px;padding:8px 14px;font-weight:700">43% qualify</div>
        <div style="background:#fee2e2;color:#991b1b;border-radius:8px;padding:8px 14px;font-weight:700">12% qualify</div>
      </div>
      <p style="margin:8px 0 0;font-size:0.78rem;color:#6b7280">Green = strong favourite · Yellow = uncertain · Red = unlikely</p>
    `,
  },
  {
    icon: '🔍',
    title: 'The home page',
    desc: 'All 48 teams are shown grouped by their group (A–L). Each tile shows the team\'s <strong>probability of qualifying</strong> for the knockout round. Use the <strong>search bar</strong> to find a team quickly, or browse by group.',
    hint: `
      <div style="border:1.5px solid #e5e7eb;border-radius:10px;padding:10px 14px;font-size:0.82rem">
        <div style="font-weight:700;margin-bottom:6px;color:#6b7280;font-size:0.72rem;text-transform:uppercase;letter-spacing:.05em">Group G</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:8px 10px;text-align:center;min-width:70px">
            🇮🇷<br><span style="font-size:0.75rem;font-weight:600">Iran</span><br>
            <span style="font-size:1rem;font-weight:800;color:#059669">71%</span>
          </div>
          <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:8px 10px;text-align:center;min-width:70px">
            🇧🇪<br><span style="font-size:0.75rem;font-weight:600">Belgium</span><br>
            <span style="font-size:1rem;font-weight:800;color:#d97706">48%</span>
          </div>
        </div>
      </div>
      <p style="margin:8px 0 0;font-size:0.78rem;color:#6b7280">Click any team tile to open that team's detail page</p>
    `,
  },
  {
    icon: '📊',
    title: 'A team\'s detail page',
    desc: 'Click any team to see their full picture: <strong>Tournament Path</strong> (probability of reaching each stage), <strong>Possible Opponents</strong> in each knockout round, and their <strong>Group Matches</strong> with live standings.',
    hint: `
      <div style="font-size:0.8rem;border:1.5px solid #e5e7eb;border-radius:10px;padding:10px 14px">
        <div style="font-weight:700;margin-bottom:8px">Tournament Path</div>
        <div style="display:flex;gap:4px;align-items:flex-end;height:60px">
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.65rem;font-weight:700">71%</span>
            <div style="width:100%;background:#10b981;border-radius:3px 3px 0 0;height:43px"></div>
            <span style="font-size:0.6rem;color:#6b7280">Qualify</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.65rem;font-weight:700">55%</span>
            <div style="width:100%;background:#3b82f6;border-radius:3px 3px 0 0;height:33px"></div>
            <span style="font-size:0.6rem;color:#6b7280">R32</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.65rem;font-weight:700">28%</span>
            <div style="width:100%;background:#3b82f6;border-radius:3px 3px 0 0;height:17px"></div>
            <span style="font-size:0.6rem;color:#6b7280">R16</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.65rem;font-weight:700">9%</span>
            <div style="width:100%;background:#f59e0b;border-radius:3px 3px 0 0;height:5px"></div>
            <span style="font-size:0.6rem;color:#6b7280">QF</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.65rem;font-weight:700">3%</span>
            <div style="width:100%;background:#e5e7eb;border-radius:3px 3px 0 0;height:2px"></div>
            <span style="font-size:0.6rem;color:#6b7280">SF</span>
          </div>
        </div>
      </div>
      <p style="margin:8px 0 0;font-size:0.78rem;color:#6b7280">Each bar = probability of reaching that round</p>
    `,
  },
  {
    icon: '⚡',
    title: 'Predicting matches',
    desc: 'Want to play "what if"? Use the <strong>Scenario Predictions</strong> card on any team page. Pick a group, pick a match, enter a predicted score, and hit <strong>+ Add</strong>. You can stack as many predictions as you like across different groups.',
    hint: `
      <div style="border:1.5px solid #ddd6fe;border-left:3px solid #7c3aed;border-radius:10px;padding:10px 14px;font-size:0.8rem">
        <div style="font-weight:700;color:#7c3aed;margin-bottom:8px">Scenario Predictions</div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px">
          <select style="padding:4px 8px;border:1.5px solid #e5e7eb;border-radius:6px;font-size:0.78rem" disabled>
            <option>Group G</option>
          </select>
          <select style="padding:4px 8px;border:1.5px solid #e5e7eb;border-radius:6px;font-size:0.78rem;flex:1" disabled>
            <option>Iran vs Egypt</option>
          </select>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-size:0.78rem;font-weight:600">🇮🇷 Iran</span>
          <input type="number" value="2" style="width:36px;text-align:center;padding:3px;border:1.5px solid #7c3aed;border-radius:5px;font-weight:700" readonly />
          <span style="font-weight:700;color:#9ca3af">–</span>
          <input type="number" value="0" style="width:36px;text-align:center;padding:3px;border:1.5px solid #7c3aed;border-radius:5px;font-weight:700" readonly />
          <span style="font-size:0.78rem;font-weight:600">Egypt 🇪🇬</span>
          <button style="background:#7c3aed;color:#fff;border:none;border-radius:6px;padding:5px 12px;font-size:0.78rem;font-weight:600">+ Add</button>
        </div>
      </div>
      <p style="margin:8px 0 0;font-size:0.78rem;color:#6b7280">Predictions are private — they never change the actual data</p>
    `,
  },
  {
    icon: '📈',
    title: 'Reading the scenario overlay',
    desc: 'Once you add predictions, the <strong>Tournament Path</strong> chart shows a <strong style="color:#7c3aed">purple bar</strong> alongside the actual bar. A green <strong style="color:#7c3aed">+5%</strong> means your scenario helps; a red <strong style="color:#ef4444">−3%</strong> means it hurts. The <strong>Possible Opponents</strong> section also updates to reflect your scenario.',
    hint: `
      <div style="font-size:0.8rem;border:1.5px solid #ddd6fe;border-radius:10px;padding:10px 14px">
        <div style="background:#f5f3ff;border:1px solid #ddd6fe;border-radius:6px;padding:4px 10px;font-size:0.72rem;font-weight:600;color:#7c3aed;margin-bottom:10px">⚡ Scenario mode — predictions applied</div>
        <div style="display:flex;gap:4px;align-items:flex-end;height:60px">
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.6rem;font-weight:700;color:#7c3aed">+6%</span>
            <div style="width:100%;position:relative;height:43px">
              <div style="position:absolute;bottom:0;width:100%;background:#10b981;border-radius:3px 3px 0 0;height:43px"></div>
              <div style="position:absolute;bottom:0;right:0;width:40%;background:#7c3aed;border-radius:3px 3px 0 0;height:49px;opacity:0.85"></div>
            </div>
            <span style="font-size:0.6rem;color:#6b7280">Qualify</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.6rem;font-weight:700;color:#7c3aed">+4%</span>
            <div style="width:100%;position:relative;height:33px">
              <div style="position:absolute;bottom:0;width:100%;background:#3b82f6;border-radius:3px 3px 0 0;height:33px"></div>
              <div style="position:absolute;bottom:0;right:0;width:40%;background:#7c3aed;border-radius:3px 3px 0 0;height:37px;opacity:0.85"></div>
            </div>
            <span style="font-size:0.6rem;color:#6b7280">R32</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:2px;justify-content:flex-end">
            <span style="font-size:0.6rem;font-weight:700;color:#ef4444">−2%</span>
            <div style="width:100%;position:relative;height:17px">
              <div style="position:absolute;bottom:0;width:100%;background:#3b82f6;border-radius:3px 3px 0 0;height:17px"></div>
              <div style="position:absolute;bottom:0;right:0;width:40%;background:#7c3aed;border-radius:3px 3px 0 0;height:14px;opacity:0.85"></div>
            </div>
            <span style="font-size:0.6rem;color:#6b7280">R16</span>
          </div>
        </div>
        <div style="display:flex;gap:12px;margin-top:8px;font-size:0.7rem;color:#6b7280">
          <span><span style="display:inline-block;width:10px;height:10px;background:#10b981;border-radius:2px;margin-right:3px"></span>Actual</span>
          <span><span style="display:inline-block;width:10px;height:10px;background:#7c3aed;border-radius:2px;margin-right:3px"></span>Your scenario</span>
        </div>
      </div>
      <p style="margin:8px 0 0;font-size:0.78rem;color:#6b7280">Remove any prediction with ✕ · Clear all with "Clear all predictions"</p>
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
/* ── FAB button ── */
.help-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 900;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #7c3aed;
  color: #fff;
  border: none;
  font-size: 1.2rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(124,58,237,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, transform 0.15s;
}
.help-fab:hover { background: #6d28d9; transform: scale(1.08); }

/* ── Overlay ── */
.help-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

/* ── Modal ── */
.help-modal {
  background: var(--surface, #fff);
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Header ── */
.help-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--border, #e5e7eb);
}
.help-logo { font-size: 1.8rem; line-height: 1; }
.help-title { font-size: 1rem; font-weight: 800; margin: 0; }
.help-step-label { font-size: 0.72rem; color: var(--text-muted, #6b7280); margin: 2px 0 0; }
.help-close {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1rem;
  color: var(--text-muted, #9ca3af);
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
}
.help-close:hover { background: var(--border, #f3f4f6); }

/* ── Dots ── */
.help-dots {
  display: flex;
  gap: 6px;
  justify-content: center;
  padding: 12px 20px 0;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  background: var(--border, #e5e7eb);
  cursor: pointer;
  padding: 0;
  transition: background 0.2s, width 0.2s;
}
.dot.active { background: #7c3aed; width: 22px; border-radius: 4px; }
.dot.done   { background: #a78bfa; }

/* ── Body ── */
.help-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  min-height: 280px;
}
.step-icon { font-size: 2.6rem; line-height: 1; }
.step-title {
  font-size: 1.1rem;
  font-weight: 800;
  text-align: center;
  margin: 0;
}
.step-desc {
  font-size: 0.88rem;
  text-align: center;
  color: var(--text, #1f2937);
  line-height: 1.6;
  max-width: 400px;
  margin: 0;
}

.step-hint { width: 100%; }
.hint-box {
  background: var(--bg, #f9fafb);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 10px;
  padding: 12px;
  font-size: 0.82rem;
}

/* ── Footer ── */
.help-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-top: 1px solid var(--border, #e5e7eb);
  gap: 12px;
}
.btn-nav {
  padding: 8px 22px;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: background 0.15s;
}
.btn-nav.primary {
  background: #7c3aed;
  color: #fff;
}
.btn-nav.primary:hover { background: #6d28d9; }
.btn-nav.secondary {
  background: var(--bg, #f3f4f6);
  color: var(--text, #374151);
  border: 1px solid var(--border, #e5e7eb);
}
.btn-nav.secondary:hover { background: var(--border, #e5e7eb); }

/* ── Transition ── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
