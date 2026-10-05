<template>
  <main class="container">
    <h1>Ore Modeler</h1>
    <section>
      <h2>Create project</h2>
      <input v-model="name" placeholder="Project name" />
      <button @click="createProject">Create</button>
    </section>
    <section>
      <h2>Projects</h2>
      <div v-for="p in projects" :key="p.id" class="project">
        <strong>#{{ p.id }} {{ p.name }}</strong>
        <input type="file" accept=".csv" @change="upload($event, p.id)" />
        <span v-if="result[p.id]">{{ result[p.id].boreholes }} boreholes / {{ result[p.id].samples }} samples</span>
      </div>
    </section>
  </main>
</template>
<script setup>
import { onMounted, ref } from 'vue'
const api = 'http://localhost:8000'
const name = ref('')
const projects = ref([])
const result = ref({})
async function load() { projects.value = await fetch(`${api}/api/projects`).then(r => r.json()) }
async function createProject() {
  if (!name.value.trim()) return
  await fetch(`${api}/api/projects`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name:name.value})})
  name.value=''; await load()
}
async function upload(e, id) {
  const file=e.target.files[0]; if(!file) return
  const fd=new FormData(); fd.append('file',file)
  const r=await fetch(`${api}/api/projects/${id}/upload`, {method:'POST',body:fd})
  const data=await r.json(); if(!r.ok) return alert(data.detail || 'Upload failed')
  result.value[id]=data
}
onMounted(load)
</script>
<style>
body{font-family:Arial,sans-serif;margin:0;background:#f5f6f8}.container{max-width:900px;margin:40px auto;background:white;padding:30px;border-radius:12px}section{margin-top:30px}.project{padding:15px;border:1px solid #ddd;margin:10px 0;border-radius:8px}input{margin:5px;padding:8px}button{padding:9px 16px}
</style>
