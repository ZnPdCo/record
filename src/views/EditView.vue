<template>
  <div class="app-layout">
    <div class="sidebar">
      <div class="sidebar-header">
        <SuiHeader size="medium" style="margin-bottom:8px;">OI 比赛档案</SuiHeader>
        <router-link to="/" class="ui basic small button" style="margin-bottom:6px;">← 返回展示</router-link>
        <SuiButton primary fluid size="small" @click="newContest">+ 新增比赛</SuiButton>
      </div>
      <div class="sidebar-list">
        <div v-if="!contests.length" class="empty-state">暂无比赛</div>
        <div v-for="(c, i) in contests" :key="i" class="sidebar-item" :class="{ active: i === currentIdx }" @click="selectContest(i)">
          <div>
            <div>{{ c.name || '未命名' }}</div>
            <div class="date">{{ c.date || '无日期' }}</div>
          </div>
        </div>
      </div>
      <div class="sidebar-actions">
        <SuiButton positive fluid @click="saveContest">保存</SuiButton>
        <SuiButton basic fluid size="small" @click="loadFromFile" style="margin-top:6px;">导入</SuiButton>
        <input type="file" accept=".json" style="display:none" ref="fileInput" @change="handleFileImport">
      </div>
      <div class="sidebar-footer">数据保存在 data.json</div>
    </div>

    <div class="main" v-if="currentIdx >= 0 && currentContest">
      <SuiForm>
        <SuiSegment>
          <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(34,36,38,.15);padding-bottom:.714rem;margin-bottom:.714rem;">
            <span style="font-size:1.5rem;font-weight:700;">比赛信息</span>
            <SuiButton negative size="mini" type="button" @click="deleteContest">删除</SuiButton>
          </div>
          <SuiFormGroup widths="equal">
            <SuiFormField label="比赛名称" v-model="currentContest.name" />
            <SuiFormField label="比赛日期" v-model="currentContest.date" placeholder="2025-06-25" />
          </SuiFormGroup>
          <SuiFormField label="比赛链接" v-model="currentContest.link" placeholder="https://..." />
          <SuiFormGroup widths="equal">
            <SuiFormField label="排名" v-model.number="currentContest.rank" type="number" />
            <SuiFormField label="总人数" v-model.number="currentContest.total" type="number" />
            <SuiFormField label="总分" v-model.number="currentContest.totalScore" type="number" />
          </SuiFormGroup>
          <div class="field">
            <label>总体回顾</label>
            <textarea v-model="currentContest.overallReview" rows="4"></textarea>
          </div>
          <div class="field">
            <label>比赛反思</label>
            <div class="reflection-list">
              <div v-for="(r, ri) in currentContest.reflections" :key="ri" class="reflection-row">
                <span class="reflection-name">{{ r.name }}</span>
                <div class="rating-btns">
                  <span v-for="rating in ['worth','unsure','not_worth']" :key="rating"
                    class="rating-btn"
                    :class="[rating, { active: r.rating === rating }]"
                    @click="r.rating = rating"
                  >{{ ratingLabels[rating] }}</span>
                </div>
                <span class="del-btn" @click="removeContestReflection(ri)">✕</span>
              </div>
            </div>
            <div class="custom-input-row" style="margin-top:6px;">
              <div style="position:relative;flex:1;">
                <input type="text" placeholder="添加预设" class="preset-autocomplete" ref="contestRefInput"
                  @focus="contestRefShow = true" @blur="setTimeout(function(){ contestRefShow = false }, 200)"
                  @input="filterContestPresets" @keydown.enter.prevent="addContestReflection">
                <div v-if="contestRefShow && filteredContestPresets.length" class="preset-dropdown">
                  <div v-for="p in filteredContestPresets" :key="p" class="preset-dropdown-item" @mousedown.prevent="addContestReflection(p)">{{ p }}</div>
                </div>
              </div>
              <SuiButton basic size="mini" @click="addCustomContestReflection">自定义</SuiButton>
            </div>
          </div>
        </SuiSegment>

        <SuiSegment>
          <SuiHeader size="small" style="margin-top:0;">时间线</SuiHeader>
          <SuiTable compact celled>
            <SuiTableHeader>
              <SuiTableRow>
                <SuiTableHeaderCell style="width:15%;">时间</SuiTableHeaderCell>
                <SuiTableHeaderCell style="width:38%;">计划</SuiTableHeaderCell>
                <SuiTableHeaderCell style="width:38%;">完成情况</SuiTableHeaderCell>
                <SuiTableHeaderCell style="width:2%;"></SuiTableHeaderCell>
              </SuiTableRow>
            </SuiTableHeader>
            <SuiTableBody>
              <SuiTableRow v-for="(t, ti) in currentContest.timeline" :key="ti" class="tl-row">
                <SuiTableCell><div class="ui input"><input type="text" v-model="t.time" placeholder="00:00"></div></SuiTableCell>
                <SuiTableCell><div class="ui input"><input type="text" v-model="t.plan" placeholder="计划"></div></SuiTableCell>
                <SuiTableCell><div class="ui input"><input type="text" v-model="t.completion" placeholder="完成情况"></div></SuiTableCell>
                <SuiTableCell class="center aligned"><span style="cursor:pointer;color:#e74c3c;font-size:16px;" @click="removeTLRow(ti)">✕</span></SuiTableCell>
              </SuiTableRow>
            </SuiTableBody>
          </SuiTable>
          <SuiButton basic size="small" @click="addTLRow">+ 添加一行</SuiButton>
        </SuiSegment>

        <SuiSegment>
          <SuiHeader size="small" style="margin-top:0;">题目</SuiHeader>
          <SuiSegment secondary v-for="(p, pi) in currentContest.problems" :key="pi" style="padding:16px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
              <span style="font-size:14px;font-weight:600;">题目 {{ pi + 1 }}</span>
              <SuiButton negative size="mini" @click="removeProblem(pi)">删除</SuiButton>
            </div>
            <SuiFormGroup widths="equal">
              <SuiFormField label="题目名称" v-model="p.name" />
              <SuiFormField label="题目链接" v-model="p.link" placeholder="https://..." />
            </SuiFormGroup>
            <SuiFormGroup widths="equal">
              <SuiFormField label="得分" v-model.number="p.score" type="number" />
              <SuiFormField label="满分" v-model.number="p.fullScore" type="number" />
              <div class="field">
                <label>难度</label>
                <select v-model="p.difficulty">
                  <option v-for="d in difficulties" :key="d" :value="d">{{ d }}</option>
                </select>
              </div>
              <div class="field">
                <div class="ui checkbox" style="margin-top:44px;">
                  <input type="checkbox" v-model="p.isWeak">
                  <label>薄弱 ⭐</label>
                </div>
              </div>
              <div class="field">
                <label>订正状态</label>
                <select v-model="p.fixed" style="margin-top:20px;">
                  <option v-for="o in fixedOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
                </select>
              </div>
            </SuiFormGroup>
            <div class="field">
              <label>标签</label>
              <div class="checkbox-grid">
                <div class="ui checkbox" v-for="tag in presetTags" :key="tag">
                  <input type="checkbox" :value="tag" v-model="p.tags">
                  <label>{{ tag }}</label>
                </div>
              </div>
              <div class="custom-input-row">
                <div class="ui input"><input type="text" placeholder="自定义标签（回车添加）" @keydown.enter="addCustomTag(pi, $event)"></div>
                <SuiButton basic size="mini" @click="addCustomTag(pi, $event)">添加</SuiButton>
              </div>
              <div class="custom-tags">
                <span v-for="(t, ti) in customTags(p)" :key="ti" class="ui small label">
                  {{ t }} <i class="delete icon" style="cursor:pointer;margin:0;" @click="removeCustomTag(p, t)"></i>
                </span>
              </div>
            </div>
            <div class="field">
              <label>题目反思</label>
              <div class="reflection-list">
                <div v-for="(r, ri) in p.reflections" :key="ri" class="reflection-row">
                  <span class="reflection-name">{{ r.name }}</span>
                  <div class="rating-btns">
                    <span v-for="rating in ['worth','unsure','not_worth']" :key="rating"
                      class="rating-btn"
                      :class="[rating, { active: r.rating === rating }]"
                      @click="r.rating = rating"
                    >{{ ratingLabels[rating] }}</span>
                  </div>
                  <span class="del-btn" @click="removeProblemReflection(pi, ri)">✕</span>
                </div>
              </div>
              <div class="custom-input-row" style="margin-top:6px;">
                <div style="position:relative;flex:1;">
                  <input type="text" placeholder="添加预设" class="preset-autocomplete"
                    @focus="openProblemRefInput(pi)" @blur="setTimeout(function(){ closeProblemRefInput(pi) }, 200)"
                    :value="problemRefFilter[pi] || ''" @input="filterProblemPresets(pi, $event)" @keydown.enter.prevent="addProblemReflection(pi)">
                  <div v-if="problemRefShow[pi] && filteredProblemPresets(pi).length" class="preset-dropdown">
                    <div v-for="p2 in filteredProblemPresets(pi)" :key="p2" class="preset-dropdown-item" @mousedown.prevent="addProblemReflection(pi, p2)">{{ p2 }}</div>
                  </div>
                </div>
                <SuiButton basic size="mini" @click="addCustomProblemReflection(pi)">自定义</SuiButton>
              </div>
            </div>
            <div class="field">
              <label>部分分计划</label>
              <SuiTable compact celled>
                <SuiTableHeader>
                  <SuiTableRow>
                    <SuiTableHeaderCell style="width:15%;">实际</SuiTableHeaderCell>
                    <SuiTableHeaderCell style="width:15%;">预期</SuiTableHeaderCell>
                    <SuiTableHeaderCell style="width:15%;">满分</SuiTableHeaderCell>
                    <SuiTableHeaderCell style="width:48%;">描述</SuiTableHeaderCell>
                    <SuiTableHeaderCell style="width:2%;"></SuiTableHeaderCell>
                  </SuiTableRow>
                </SuiTableHeader>
                <SuiTableBody>
                  <SuiTableRow v-for="(s, si) in p.subScores" :key="si" class="ss-row">
                    <SuiTableCell><div class="ui input"><input type="text" v-model="s.actual"></div></SuiTableCell>
                    <SuiTableCell><div class="ui input"><input type="text" v-model="s.expected"></div></SuiTableCell>
                    <SuiTableCell><div class="ui input"><input type="text" v-model="s.full"></div></SuiTableCell>
                    <SuiTableCell><div class="ui input"><input type="text" v-model="s.desc" placeholder="描述"></div></SuiTableCell>
                    <SuiTableCell class="center aligned"><span style="cursor:pointer;color:#e74c3c;font-size:16px;" @click="removeSSRow(p, si)">✕</span></SuiTableCell>
                  </SuiTableRow>
                </SuiTableBody>
              </SuiTable>
              <SuiButton basic size="mini" @click="addSSRow(p)">+ 添加一行</SuiButton>
            </div>
            <div class="field">
              <label>反思笔记</label>
              <textarea v-model="p.notes" rows="3"></textarea>
            </div>
          </SuiSegment>
          <SuiButton primary size="small" @click="addProblem">+ 添加题目</SuiButton>
        </SuiSegment>
      </SuiForm>
    </div>

    <div class="main" v-else-if="currentIdx < 0" style="display:flex;align-items:center;justify-content:center;">
      <div style="text-align:center;color:#999;">
        <p style="font-size:16px;">选择左侧比赛进行编辑，或点击「新增比赛」</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { contestReflections, problemReflections, ratingLabels, fixedOptions } from '../constants.js'

const $ = window.$

var presetTags = ['DP', '图论', '数据结构', '贪心', '数论', '字符串', '构造', '思维', 'Ad-Hoc', '模拟', '博弈论']
var difficulties = ['暂无评定', '入门', '普及−', '普及/提高−', '普及+/提高', '提高+/省选−', '省选/NOI−', 'NOI/NOI+/CTSC']

var contests = ref([])
var currentIdx = ref(-1)
var fileInput = ref(null)
var contestRefInput = ref(null)
var contestRefShow = ref(false)
var contestRefFilter = ref('')
var problemRefShow = ref({})
var problemRefFilter = ref({})
var contestAutocomplete = ref('')

var currentContest = computed(function() {
  if (currentIdx.value < 0 || currentIdx.value >= contests.value.length) return null
  return contests.value[currentIdx.value]
})

var filteredContestPresets = computed(function() {
  var f = contestAutocomplete.value.trim()
  var used = new Set((currentContest.value?.reflections || []).map(function(r) { return r.name }))
  if (!f) return contestReflections.filter(function(n) { return !used.has(n) })
  return contestReflections.filter(function(n) { return !used.has(n) && n.indexOf(f) >= 0 })
})

function filterContestPresets() {
  contestAutocomplete.value = contestRefInput.value?.value || ''
}

function addContestReflection(preset) {
  if (!currentContest.value) return
  if (typeof preset !== 'string' || !preset) {
    var input = contestRefInput.value
    if (!input) return
    preset = input.value.trim()
    if (!preset) return
  }
  var used = new Set((currentContest.value.reflections || []).map(function(r) { return r.name }))
  if (used.has(preset)) { if (contestRefInput.value) contestRefInput.value.value = ''; return }
  if (!currentContest.value.reflections) currentContest.value.reflections = []
  currentContest.value.reflections.push({ name: preset, rating: 'unsure' })
  if (contestRefInput.value) { contestRefInput.value.value = ''; contestAutocomplete.value = '' }
  contestRefShow.value = false
}

function addCustomContestReflection() {
  if (!currentContest.value) return
  var input = contestRefInput.value
  if (!input) return
  var val = input.value.trim()
  if (!val) return
  var used = new Set((currentContest.value.reflections || []).map(function(r) { return r.name }))
  if (used.has(val)) { input.value = ''; return }
  if (!currentContest.value.reflections) currentContest.value.reflections = []
  currentContest.value.reflections.push({ name: val, rating: 'unsure' })
  input.value = ''
  contestAutocomplete.value = ''
  contestRefShow.value = false
}

function removeContestReflection(ri) {
  if (!currentContest.value?.reflections) return
  currentContest.value.reflections.splice(ri, 1)
}

function openProblemRefInput(pi) {
  problemRefShow.value[pi] = true
}

function closeProblemRefInput(pi) {
  problemRefShow.value[pi] = false
}

function filteredProblemPresets(pi) {
  var p = currentContest.value?.problems[pi]
  if (!p) return []
  var f = (problemRefFilter.value[pi] || '').trim()
  var used = new Set((p.reflections || []).map(function(r) { return r.name }))
  if (!f) return problemReflections.filter(function(n) { return !used.has(n) })
  return problemReflections.filter(function(n) { return !used.has(n) && n.indexOf(f) >= 0 })
}

function filterProblemPresets(pi, event) {
  problemRefFilter.value[pi] = event?.target?.value || ''
}

function addProblemReflection(pi, preset) {
  var p = currentContest.value?.problems[pi]
  if (!p) return
  var val = preset || (problemRefFilter.value[pi] || '').trim()
  if (!val) return
  var used = new Set((p.reflections || []).map(function(r) { return r.name }))
  if (used.has(val)) { problemRefFilter.value[pi] = ''; return }
  if (!p.reflections) p.reflections = []
  p.reflections.push({ name: val, rating: 'unsure' })
  problemRefFilter.value[pi] = ''
  problemRefShow.value[pi] = false
}

function addCustomProblemReflection(pi) {
  var p = currentContest.value?.problems[pi]
  if (!p) return
  var val = (problemRefFilter.value[pi] || '').trim()
  if (!val) return
  var used = new Set((p.reflections || []).map(function(r) { return r.name }))
  if (used.has(val)) { problemRefFilter.value[pi] = ''; return }
  if (!p.reflections) p.reflections = []
  p.reflections.push({ name: val, rating: 'unsure' })
  problemRefFilter.value[pi] = ''
  problemRefShow.value[pi] = false
}

function removeProblemReflection(pi, ri) {
  var p = currentContest.value?.problems[pi]
  if (!p?.reflections) return
  p.reflections.splice(ri, 1)
}

function selectContest(idx) {
  currentIdx.value = idx
}

function newContest() {
  var c = {
    date: '', name: '', link: '', rank: 0, total: 0,
    totalScore: 0, overallReview: '',
    reflections: [],
    timeline: [{time: '', plan: '', completion: ''}],
    problems: []
  }
  contests.value.unshift(c)
  currentIdx.value = 0
}

function deleteContest() {
  if (currentIdx.value < 0) return
  if (!confirm('确定删除这场比赛吗？')) return
  contests.value.splice(currentIdx.value, 1)
  currentIdx.value = contests.value.length > 0 ? 0 : -1
}

function addTLRow() {
  if (!currentContest.value) return
  currentContest.value.timeline.push({time: '', plan: '', completion: ''})
}

function removeTLRow(ti) {
  if (!currentContest.value) return
  currentContest.value.timeline.splice(ti, 1)
}

function addProblem() {
  if (!currentContest.value) return
  currentContest.value.problems.push({
    name: '', link: '', score: 0, fullScore: 0,
    difficulty: '暂无评定', tags: [], reflections: [], isWeak: false, fixed: 'no',
    subScores: [{actual: '', expected: '', full: '', desc: ''}],
    notes: ''
  })
}

function removeProblem(pi) {
  if (!confirm('确定删除这道题吗？')) return
  currentContest.value.problems.splice(pi, 1)
}

function addSSRow(p) {
  p.subScores.push({actual: '', expected: '', full: '', desc: ''})
}

function removeSSRow(p, si) {
  p.subScores.splice(si, 1)
}

function customTags(p) {
  return (p.tags || []).filter(function(t) { return presetTags.indexOf(t) === -1 })
}

function addCustomTag(pi, event) {
  var input = event.target
  var val = input.value.trim()
  if (!val) return
  var p = currentContest.value.problems[pi]
  if (!p) return
  if (p.tags.includes(val)) { input.value = ''; return }
  p.tags.push(val)
  input.value = ''
}

function removeCustomTag(p, tag) {
  var idx = p.tags.indexOf(tag)
  if (idx >= 0) p.tags.splice(idx, 1)
}

function saveContest() {
  var json = JSON.stringify({ contests: contests.value }, null, 2)
  var blob = new Blob([json], { type: 'application/json' })
  var url = URL.createObjectURL(blob)
  var a = document.createElement('a')
  a.href = url; a.download = 'data.json'
  document.body.appendChild(a); a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  $('body').toast({ message: '保存成功！data.json 已下载', class: 'success', position: 'bottom right', displayTime: 2500 })
}

function loadFromFile() {
  fileInput.value.click()
}

function handleFileImport(e) {
  var file = e.target.files[0]
  if (!file) return
  var reader = new FileReader()
  reader.onload = function(ev) {
    try {
      var d = JSON.parse(ev.target.result)
      if (d.contests) {
        contests.value = d.contests
        currentIdx.value = contests.value.length > 0 ? 0 : -1
        $('body').toast({ message: '导入成功，共 ' + d.contests.length + ' 场比赛', class: 'success', position: 'bottom right', displayTime: 2500 })
      } else {
        $('body').toast({ message: '无效的数据文件', class: 'error', position: 'bottom right', displayTime: 2500 })
      }
    } catch(e) {
      $('body').toast({ message: '文件格式错误', class: 'error', position: 'bottom right', displayTime: 2500 })
    }
  }
  reader.readAsText(file)
  e.target.value = ''
}

onMounted(function() {
  fetch('data.json?t=' + Date.now())
    .then(function(r) { return r.json() })
    .then(function(d) {
      contests.value = d.contests || []
      if (contests.value.length > 0) currentIdx.value = 0
    })
    .catch(function() {
      contests.value = []
    })
})
</script>

<style>
body { margin: 0; background: #f5f5f5; }
.app-layout { display: flex; min-height: 100vh; }
.sidebar { width: 240px; background: #fff; border-right: 1px solid #ddd; display: flex; flex-direction: column; flex-shrink: 0; position: fixed; top: 0; left: 0; height: 100vh; z-index: 1; }
.sidebar-header { padding: 16px; border-bottom: 1px solid #eee; }
.sidebar-list { flex: 1; overflow-y: auto; }
.sidebar-item { padding: 10px 16px; cursor: pointer; border-bottom: 1px solid #f0f0f0; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }
.sidebar-item:hover { background: #f0f7ff; }
.sidebar-item.active { background: #dbeafe; font-weight: 600; }
.sidebar-item .date { color: #888; font-size: 11px; }
.sidebar-actions { padding: 12px; border-top: 1px solid #eee; }
.sidebar-footer { padding: 8px 12px; border-top: 1px solid #eee; font-size: 11px; color: #888; text-align: center; }
.main { margin-left: 240px; flex: 1; padding: 24px; overflow-y: auto; }
.checkbox-grid { display: flex; flex-wrap: wrap; gap: 3px 14px; padding: 6px 0; }
.custom-input-row { display: flex; gap: 6px; margin-top: 6px; }
.custom-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.empty-state { text-align: center; color: #999; padding: 20px; font-size: 13px; }
.reflection-list { display: flex; flex-direction: column; gap: 6px; padding: 6px 0; }
.reflection-row { display: flex; align-items: center; gap: 8px; padding: 4px 8px; background: #f8f9fa; border-radius: 4px; }
.reflection-name { flex: 1; font-size: 13px; }
.rating-btns { display: flex; gap: 2px; }
.rating-btn { padding: 2px 8px; border-radius: 3px; font-size: 11px; cursor: pointer; border: 1px solid #ddd; background: #fff; color: #888; user-select: none; }
.rating-btn.worth.active { background: #27ae60; color: #fff; border-color: #27ae60; }
.rating-btn.unsure.active { background: #f39c12; color: #fff; border-color: #f39c12; }
.rating-btn.not_worth.active { background: #e74c3c; color: #fff; border-color: #e74c3c; }
.del-btn { cursor: pointer; color: #e74c3c; font-size: 13px; opacity: 0.6; }
.del-btn:hover { opacity: 1; }
.preset-autocomplete { width: 100%; }
.preset-dropdown { position: absolute; top: 100%; left: 0; right: 0; background: #fff; border: 1px solid #ddd; border-radius: 4px; max-height: 200px; overflow-y: auto; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.preset-dropdown-item { padding: 6px 10px; font-size: 13px; cursor: pointer; }
.preset-dropdown-item:hover { background: #f0f7ff; }
</style>
