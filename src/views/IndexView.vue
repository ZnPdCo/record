<template>
  <SuiContainer style="padding: 20px 0;">
    <SuiSegment basic style="padding: 0; margin-bottom: 20px;">
      <SuiHeader>
        OI 比赛档案
        <template #sub>
          <router-link to="/edit">编辑</router-link>
        </template>
      </SuiHeader>
    </SuiSegment>

    <SuiMenu secondary pointing style="margin-bottom: 20px;">
      <SuiMenuItem :active="currentYear === '全部'" @selected="currentYear = '全部'">全部</SuiMenuItem>
      <SuiMenuItem v-for="y in years" :key="y" :active="currentYear === y" @selected="currentYear = y">{{ y }}</SuiMenuItem>
    </SuiMenu>

    <SuiGrid :doubling="true" :columns="4" style="margin-bottom: 20px;">
      <SuiGridColumn>
        <SuiSegment style="text-align: center;">
          <SuiStatistic size="huge">
            <SuiStatisticValue>{{ contestCount }}</SuiStatisticValue>
            <SuiStatisticLabel>参赛次数</SuiStatisticLabel>
          </SuiStatistic>
        </SuiSegment>
      </SuiGridColumn>
      <SuiGridColumn>
        <SuiSegment>
          <SuiHeader size="tiny">比赛反思</SuiHeader>
          <SuiLabelGroup v-if="contestRefItems.length">
            <SuiLabel v-for="[k, v] in contestRefItems" :key="k">
              {{ k }}<SuiLabelDetail>{{ v }}</SuiLabelDetail>
            </SuiLabel>
          </SuiLabelGroup>
          <span v-else style="color:#999;">暂无</span>
        </SuiSegment>
      </SuiGridColumn>
      <SuiGridColumn>
        <SuiSegment>
          <SuiHeader size="tiny">薄弱知识点</SuiHeader>
          <SuiLabelGroup v-if="weakItems.length">
            <SuiLabel v-for="[k, v] in weakItems" :key="k">
              {{ k }}<SuiLabelDetail>{{ v }}</SuiLabelDetail>
            </SuiLabel>
          </SuiLabelGroup>
          <span v-else style="color:#999;">暂无</span>
        </SuiSegment>
      </SuiGridColumn>
      <SuiGridColumn>
        <SuiSegment>
          <SuiHeader size="tiny">题目反思统计</SuiHeader>
          <SuiLabelGroup v-if="probRefItems.length">
            <SuiLabel v-for="[k, v] in probRefItems" :key="k">
              {{ k }}<SuiLabelDetail>{{ v }}</SuiLabelDetail>
            </SuiLabel>
          </SuiLabelGroup>
          <span v-else style="color:#999;">暂无</span>
        </SuiSegment>
      </SuiGridColumn>
    </SuiGrid>

    <SuiSegment basic v-if="!loaded" style="text-align:center;padding:60px 0;"><p>加载中...</p></SuiSegment>
    <SuiSegment basic v-else-if="!filteredContests.length" style="text-align:center;padding:60px 0;"><p>暂无比赛记录</p></SuiSegment>

    <SuiSegment v-for="c in filteredContests" :key="ckey(c)" style="margin-bottom: 12px;">
      <div class="contest-header" @click="toggleCard(c)">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <span class="meta-date">{{ c.date || '' }}</span>
            <span class="meta-name">{{ c.name || '未命名' }}</span>
            <span v-if="c.totalScore || c.expectedScore" class="meta-item">得分 {{ c.totalScore ?? 0 }}/{{ c.expectedScore ?? 0 }}</span>
            <span v-if="c.rank || c.total" class="meta-item">排名 {{ c.rank ?? '?' }}/{{ c.total ?? '?' }}</span>
          </div>
          <SuiIcon name="chevron right" :class="{ rotated: isOpen(c) }" />
        </div>
      </div>
      <div v-if="isOpen(c)" class="contest-body">
        <SuiMessage v-if="c.overallReview">
          <SuiMessageHeader>总体回顾</SuiMessageHeader>
          <p style="white-space:pre-wrap;">{{ c.overallReview }}</p>
        </SuiMessage>

        <SuiMessage v-if="c.reflections?.length">
          <SuiMessageHeader>比赛反思</SuiMessageHeader>
          <SuiLabelGroup>
            <SuiLabel v-for="r in c.reflections" :key="r.name" :style="ratingStyle(r.rating)">{{ r.name }}</SuiLabel>
          </SuiLabelGroup>
        </SuiMessage>

        <template v-if="c.timeline?.length && c.timeline[0].time">
          <SuiHeader size="tiny">时间线</SuiHeader>
          <SuiTable compact celled style="margin-bottom: 16px;">
            <SuiTableHeader>
              <SuiTableRow>
                <SuiTableHeaderCell style="width:15%;">时间</SuiTableHeaderCell>
                <SuiTableHeaderCell style="width:38%;">计划</SuiTableHeaderCell>
                <SuiTableHeaderCell style="width:47%;">完成情况</SuiTableHeaderCell>
              </SuiTableRow>
            </SuiTableHeader>
            <SuiTableBody>
              <SuiTableRow v-for="(t, ti) in c.timeline" :key="ti">
                <SuiTableCell style="font-weight:600;">{{ t.time }}</SuiTableCell>
                <SuiTableCell>{{ t.plan }}</SuiTableCell>
                <SuiTableCell><span style="white-space:pre-wrap;">{{ t.completion }}</span></SuiTableCell>
              </SuiTableRow>
            </SuiTableBody>
          </SuiTable>
        </template>

        <SuiSegment secondary v-for="(p, pi) in c.problems" :key="pi" style="margin-bottom: 10px;">
          <div class="problem-head">
            <span style="font-size:14px;font-weight:600;">
              <a v-if="p.link" :href="p.link" target="_blank">{{ p.name }}</a>
              <template v-else>{{ p.name }}</template>
            </span>
            <span v-if="p.isWeak" style="color:#f39c12;font-size:14px;">⭐</span>
            <span v-if="p.fixed && p.fixed !== 'no'" class="ui mini label" :class="fixedClass(p.fixed)">{{ fixedLabel(p.fixed) }}</span>
          </div>
          <div class="problem-meta">
            <span v-if="p.score !== undefined || p.fullScore" style="font-weight:600;">{{ p.score ?? 0 }}/{{ p.fullScore ?? '?' }}</span>
            <SuiLabel v-if="p.difficulty" :style="diffLabelStyle(p.difficulty)">{{ p.difficulty }}</SuiLabel>
            <SuiLabel v-for="t in p.tags" :key="t">{{ t }}</SuiLabel>
            <SuiLabel v-for="r in p.reflections" :key="r.name" :style="ratingStyle(r.rating)">{{ r.name }}</SuiLabel>
          </div>
          <SuiTable compact celled v-if="hasVisibleSubScores(p)" style="margin:6px 0;">
            <SuiTableHeader>
              <SuiTableRow>
                <SuiTableHeaderCell>实际</SuiTableHeaderCell>
                <SuiTableHeaderCell>预期</SuiTableHeaderCell>
                <SuiTableHeaderCell>满分</SuiTableHeaderCell>
                <SuiTableHeaderCell>描述</SuiTableHeaderCell>
              </SuiTableRow>
            </SuiTableHeader>
            <SuiTableBody>
              <SuiTableRow v-for="(s, si) in visibleSubScores(p)" :key="si">
                <SuiTableCell>{{ s.actual }}</SuiTableCell>
                <SuiTableCell>{{ s.expected }}</SuiTableCell>
                <SuiTableCell>{{ s.full }}</SuiTableCell>
                <SuiTableCell>{{ s.desc }}</SuiTableCell>
              </SuiTableRow>
            </SuiTableBody>
          </SuiTable>
          <div v-if="p.notes" class="problem-text"><strong>反思：</strong><br><span style="white-space:pre-wrap;">{{ p.notes }}</span></div>
        </SuiSegment>
      </div>
    </SuiSegment>
  </SuiContainer>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ratingColors, fixedOptions } from '../constants.js'

var diffColors = {
  '暂无评定':     'rgb(191, 191, 191)',
  '入门':         'rgb(254, 76, 97)',
  '普及−':        'rgb(243, 156, 17)',
  '普及/提高−':   'rgb(255, 193, 22)',
  '普及+/提高':   'rgb(82, 196, 26)',
  '提高+/省选−':  'rgb(52, 152, 219)',
  '省选/NOI−':    'rgb(157, 61, 207)',
  'NOI/NOI+/CTSC':'rgb(14, 29, 105)'
}

function diffLabelStyle(d) {
  var c = diffColors[d] || '#999'
  return { background: c + '20', color: c, border: '1px solid ' + c + '40' }
}

function ratingStyle(rating) {
  var rc = ratingColors[rating]
  if (!rc) return { background: '#f0f0f0', color: '#888' }
  return { background: rc.bg, color: rc.color, border: '1px solid ' + rc.color + '40' }
}

function fixedClass(v) {
  if (v === 'full') return 'green'
  if (v === 'partial') return 'yellow'
  return ''
}

function fixedLabel(v) {
  for (var i = 0; i < fixedOptions.length; i++) {
    if (fixedOptions[i].value === v) return fixedOptions[i].label
  }
  return v
}

function hasVisibleSubScores(p) {
  return p.subScores && p.subScores.some(function(s) { return s && (s.full || s.desc) })
}

function visibleSubScores(p) {
  if (!p.subScores) return []
  return p.subScores.filter(function(s) { return s && (s.full || s.desc) })
}

var loaded = ref(false)
var contests = ref([])
var currentYear = ref('全部')
var openCardMap = ref({})

watch(currentYear, function() { openCardMap.value = {} })

function toggleCard(c) {
  var key = ckey(c)
  openCardMap.value[key] = !openCardMap.value[key]
}

function isOpen(c) { return !!openCardMap.value[ckey(c)] }

function ckey(c) { return (c.date || '') + '|' + (c.name || '') }

var years = computed(function() {
  var set = {}
  contests.value.forEach(function(c) {
    if (c.date && c.date.length >= 4) set[c.date.substring(0, 4)] = true
  })
  return Object.keys(set).sort()
})

var filteredContests = computed(function() {
  if (currentYear.value === '全部') return contests.value
  return contests.value.filter(function(c) { return c.date && c.date.substring(0, 4) === currentYear.value })
})

var contestCount = computed(function() { return filteredContests.value.length })

var contestRefItems = computed(function() {
  var map = {}
  filteredContests.value.forEach(function(c) {
    (c.reflections || []).forEach(function(r) { map[r.name] = (map[r.name] || 0) + 1 })
  })
  return Object.entries(map).sort(function(a, b) { return b[1] - a[1] })
})

var weakItems = computed(function() {
  var map = {}
  filteredContests.value.forEach(function(c) {
    (c.problems || []).forEach(function(p) {
      if (p.isWeak) (p.tags || []).forEach(function(t) { map[t] = (map[t] || 0) + 1 })
    })
  })
  return Object.entries(map).filter(function(e) { return e[1] >= 2 }).sort(function(a, b) { return b[1] - a[1] })
})

var probRefItems = computed(function() {
  var map = {}
  filteredContests.value.forEach(function(c) {
    (c.problems || []).forEach(function(p) {
      (p.reflections || []).forEach(function(r) { map[r.name] = (map[r.name] || 0) + 1 })
    })
  })
  return Object.entries(map).sort(function(a, b) { return b[1] - a[1] })
})

onMounted(function() {
  fetch('data.json?t=' + Date.now())
    .then(function(r) { return r.json() })
    .then(function(d) { contests.value = d.contests || []; loaded.value = true })
    .catch(function() { loaded.value = true })
})
</script>

<style>
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }
.contest-header { cursor: pointer; user-select: none; }
.contest-header:hover { opacity: 0.85; }
.contest-body { padding-top: 16px; }
i.icon.rotated { transform: rotate(90deg); }
.meta-date { font-weight: 700; font-size: 15px; color: #555; min-width: 90px; display: inline-block; }
.meta-name { font-size: 15px; }
.meta-item { font-size: 12px; color: #888; margin-left: 10px; }
.problem-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
.problem-meta { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; font-size: 12px; margin-bottom: 6px; }
.problem-text { font-size: 12px; color: #555; margin-top: 4px; }
.problem-text strong { color: #333; }
</style>
